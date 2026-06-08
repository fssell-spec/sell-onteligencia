"""Prefeitura Scanner — extrai secretários via Playwright + Groq LLM.

Para cada município com official_website, navega até a página de secretarias,
extrai texto e usa LLM para identificar secretário de cultura/turismo.

Uso interno:
    from crawlers.prefeituras.scanner import PrefeituraScanner
    scanner = PrefeituraScanner(groq_api_key="gsk_...")
    contacts = scanner.scan(municipality)
"""
import json
import re
import time

from groq import Groq
from playwright.sync_api import Browser, Page, TimeoutError as PlaywrightTimeout, sync_playwright

# Palavras no href/texto do link que indicam página de secretarias
_MENU_KEYWORDS = [
    "secretaria", "secretario", "secretária", "governo",
    "equipe", "organograma", "gestao", "administracao",
    "estrutura", "municipio",
]

# Palavras que identificam diretamente as secretarias de interesse
_ALVO_KEYWORDS = ["cultura", "turismo", "cultural", "turistico", "lazer", "eventos", "arte"]

# Apenas esses roles nos interessam comercialmente
ROLES_ALVO = {"secretario_cultura", "secretario_turismo"}

_NAV_TIMEOUT = 25_000   # ms
_PAGE_LOAD = 12_000     # ms para aguardar rede ociosa
_MAX_CANDIDATE_LINKS = 6
_MAX_TEXT_CHARS = 12_000  # limite de contexto enviado ao LLM (~3k tokens)

_SYSTEM_PROMPT = """\
Você receberá texto extraído de uma página de prefeitura municipal brasileira.
Identifique secretários municipais mencionados.

Para cada um, extraia:
- name: nome completo (string)
- role_display: cargo conforme aparece no texto (ex: "Secretária de Cultura e Turismo")
- role_normalized: um desses valores EXATOS — secretario_cultura, secretario_turismo, secretario_educacao, secretario_financas, secretario_saude, secretario_obras, secretario_admin, outro
- phone: telefone (string ou null)
- email: email (string ou null)

Responda SOMENTE com JSON válido:
{"secretarios": [...]}

Se não houver secretários, responda: {"secretarios": []}
Não inclua explicações fora do JSON.
"""


def _clean_text(html: str) -> str:
    """Remove tags HTML e compacta espaços."""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _score_link(href: str, text: str) -> int:
    """Pontuação de relevância de um link para páginas de secretaria."""
    combined = (href + " " + text).lower()
    score = 0
    for kw in _MENU_KEYWORDS:
        if kw in combined:
            score += 1
    # Links de secretaria específica valem mais
    if "secretar" in combined:
        score += 3
    # Links de cultura/turismo têm prioridade máxima
    for kw in _ALVO_KEYWORDS:
        if kw in combined:
            score += 5
    # Penalizar links externos, âncoras, documentos binários
    if href.startswith("#") or "http" in href[1:]:
        score -= 5
    if any(href.lower().endswith(ext) for ext in (".pdf", ".docx", ".doc", ".xlsx", ".xls", ".zip", ".rar")):
        score -= 10
    return score


class PrefeituraScanner:
    def __init__(self, groq_api_key: str, headless: bool = True, verbose: bool = False):
        self._groq = Groq(api_key=groq_api_key)
        self._headless = headless
        self._verbose = verbose

    def scan(self, municipality_name: str, base_url: str) -> list[dict]:
        """Retorna lista de dicts com dados dos secretários encontrados."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self._headless)
                try:
                    return self._scan_with_browser(browser, municipality_name, base_url)
                finally:
                    browser.close()
        except Exception as exc:
            self._log(f"  [ERRO fatal] {municipality_name}: {exc}")
            return []

    def _scan_with_browser(self, browser: Browser, name: str, base_url: str) -> list[dict]:
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (compatible; SellInteligencia/1.0)"})

        # 1. Carregar homepage
        try:
            page.goto(base_url, timeout=_NAV_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=_PAGE_LOAD)
        except PlaywrightTimeout:
            self._log(f"  [TIMEOUT homepage] {name}")
            return []
        except Exception as exc:
            self._log(f"  [ERRO homepage] {name}: {exc}")
            return []

        # 2. Coletar links candidatos da homepage
        candidates = self._collect_candidate_links(page, base_url)
        self._log(f"  {name}: {len(candidates)} links candidatos")

        # 3. Visitar APENAS páginas de cultura/turismo (economiza tokens no LLM)
        all_text_chunks: list[str] = []
        visited: set[str] = {base_url, page.url}
        per_page = 5_000  # chars por página — suficiente para nome+contato

        # Prioridade 1: links com "cultura" ou "turismo" na URL/texto
        priority = [u for u in candidates if any(kw in u.lower() for kw in _ALVO_KEYWORDS)]
        # Prioridade 2: demais candidatos (secretarias genéricas, organograma)
        outros = [u for u in candidates if u not in priority]

        for url in (priority + outros)[:_MAX_CANDIDATE_LINKS]:
            if url in visited:
                continue
            visited.add(url)
            chunk = self._fetch_page_text(page, url, max_chars=per_page)
            if chunk:
                all_text_chunks.append(chunk)
                self._log(f"  +pag {len(chunk)}ch: {url.split('/')[-2] or url.split('/')[-1]}")
            time.sleep(0.5)

        # 3b. Fallback: tentar URLs comuns se candidatos não produziram conteúdo útil
        if sum(len(c) for c in all_text_chunks) < 500:
            from urllib.parse import urljoin
            fallback_paths = [
                "/secretarias", "/governo/secretarias", "/governo",
                "/equipe", "/administracao", "/municipio/secretarias",
                "/secretaria-de-cultura", "/secretaria-de-turismo",
                "/secretaria-municipal-de-cultura", "/secretaria-municipal-de-turismo",
            ]
            for path in fallback_paths:
                fb_url = urljoin(base_url, path)
                if fb_url in visited:
                    continue
                visited.add(fb_url)
                chunk = self._fetch_page_text(page, fb_url)
                if chunk and len(chunk) > 200:
                    all_text_chunks.append(chunk)
                    self._log(f"  Fallback OK: {fb_url}")
                    break
                time.sleep(0.3)

        # 4. Enviar ao LLM
        combined = "\n\n---\n\n".join(all_text_chunks)
        self._log(f"  Texto total: {len(combined)} chars | enviando {min(len(combined), _MAX_TEXT_CHARS)}")
        debug = getattr(self, "_debug_text_file", None)
        return self._extract_with_llm(combined[:_MAX_TEXT_CHARS], debug_file=debug)

    def _collect_candidate_links(self, page: Page, base_url: str) -> list[str]:
        """Coleta e ordena URLs por relevância para páginas de secretaria."""
        try:
            anchors = page.query_selector_all("a[href]")
        except Exception:
            return []

        scored: list[tuple[int, str]] = []
        seen: set[str] = set()

        for a in anchors:
            try:
                href = (a.get_attribute("href") or "").strip()
                text = (a.inner_text() or "").strip()
            except Exception:
                continue

            if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue

            # Normalizar URL
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            elif not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)

            # Manter apenas links do mesmo domínio
            from urllib.parse import urlparse
            base_domain = urlparse(base_url).netloc
            link_domain = urlparse(href).netloc
            if base_domain not in link_domain and link_domain not in base_domain:
                continue

            sc = _score_link(href, text)
            if sc > 0 and href not in seen:
                scored.append((sc, href))
                seen.add(href)

        scored.sort(reverse=True)
        return [url for _, url in scored]

    def _fetch_page_text(self, page: Page, url: str, max_chars: int | None = None) -> str:
        if max_chars is None:
            max_chars = _MAX_TEXT_CHARS // 2
        try:
            page.goto(url, timeout=_NAV_TIMEOUT, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=_PAGE_LOAD)
            except PlaywrightTimeout:
                pass  # continua mesmo sem networkidle — pega o que tiver
            # Aguarda render JS (SPAs e CMSs que injetam conteúdo após load)
            page.wait_for_timeout(1500)
            text = _clean_text(page.content())
            return text[:max_chars]
        except PlaywrightTimeout:
            self._log(f"    [TIMEOUT] {url}")
            return ""
        except Exception as exc:
            self._log(f"    [ERRO] {url}: {exc}")
            return ""

    def _extract_with_llm(self, text: str, debug_file: str | None = None) -> list[dict]:
        if debug_file:
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(text)

        for attempt in range(3):
            try:
                resp = self._groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": text},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0,
                    max_tokens=1024,
                )
                data = json.loads(resp.choices[0].message.content)
                contacts = data.get("secretarios", [])
                return [self._fix_role(c) for c in contacts]
            except Exception as exc:
                err_str = str(exc)
                if "429" in err_str and "rate_limit" in err_str:
                    # Extrair tempo de espera da mensagem
                    import re as _re
                    m = _re.search(r"Please try again in (\d+)m([\d.]+)s", err_str)
                    wait = 60
                    if m:
                        wait = int(m.group(1)) * 60 + float(m.group(2)) + 5
                    self._log(f"    [RATE LIMIT] Aguardando {round(wait)}s...")
                    if attempt < 2:
                        time.sleep(wait)
                        continue
                self._log(f"    [LLM ERRO] {exc}")
                return []
        return []

    @staticmethod
    def _fix_role(contact: dict) -> dict:
        """Corrige role_normalized baseado no texto do cargo.

        Se o display menciona cultura/turismo, promove para o role correto
        mesmo que o LLM tenha classificado como educação ou outro.
        """
        dept = (contact.get("role_display") or "").lower()
        current = contact.get("role_normalized", "outro")

        has_cultura = any(kw in dept for kw in ("cultur", "arte", "patrimonio", "lazer"))
        has_turismo = any(kw in dept for kw in ("turis", "turistico", "turístico"))

        # Promover se o display menciona cultura/turismo explicitamente
        if has_turismo:
            contact["role_normalized"] = "secretario_turismo"
        elif has_cultura and current not in ("secretario_turismo",):
            contact["role_normalized"] = "secretario_cultura"
        elif current in ("outro", None):
            pass  # não altera — deixa como está
        return contact

    def _log(self, msg: str) -> None:
        if self._verbose:
            print(msg)
