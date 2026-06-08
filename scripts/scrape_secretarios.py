"""Raspa sites das prefeituras do MS para encontrar secretarios de cultura e turismo.

Para cada municipio com official_website, busca paginas de secretaria/governo,
extrai o texto e usa Groq para identificar o secretario de cultura e de turismo.

Uso:
  python scripts/scrape_secretarios.py
  python scripts/scrape_secretarios.py --dry-run
  python scripts/scrape_secretarios.py --municipio "Campo Grande"
  python scripts/scrape_secretarios.py --limit 10
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.public_contact import PublicContact

TIMEOUT = 10
SLEEP_BETWEEN_SITES = 1.5
GROQ_MIN_INTERVAL = 20.0

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SellInteligencia/1.0)"}

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Palavras-chave para encontrar paginas de secretarios
LINK_KEYWORDS = [
    "secretaria", "secretarias", "secretario", "governo", "equipe",
    "administracao", "estrutura", "gestao", "gabinete",
    "cultura", "turismo", "lazer", "esporte",
]

# Paths diretos comuns em sites de prefeituras brasileiras
DIRECT_PATHS = [
    "/secretarias",
    "/governo/secretarias",
    "/secretarias-municipais",
    "/orgaos/secretarias",
    "/secretaria-de-cultura",
    "/secretaria-municipal-de-cultura",
    "/secretaria-de-turismo",
    "/secretaria-municipal-de-turismo",
    "/secretaria-de-esporte-e-cultura",
    "/governo",
    "/equipe-de-governo",
    "/gestao-municipal",
    "/estrutura-organizacional",
    "/administracao",
    "/orgaos",
]

_GROQ_CLIENT = None
_LAST_GROQ_CALL = 0.0

GROQ_SYSTEM = (
    "Voce e um assistente que extrai dados de funcionarios publicos de paginas web brasileiras. "
    "Responda APENAS com JSON valido."
)

GROQ_PROMPT = """\
Analise este texto de um site de prefeitura municipal brasileira.
Encontre o nome da pessoa que ocupa o cargo de Secretario de Cultura e o nome da pessoa que ocupa o cargo de Secretario de Turismo (ou pastas equivalentes como Esporte, Lazer, Turismo, Cultura e Turismo).

IMPORTANTE: "nome" deve ser o nome proprio da pessoa (ex: "Joao Silva"), NAO o nome da secretaria ou orgao.
Se nao encontrar o nome da pessoa, use null.

Texto:
{texto}

Retorne JSON:
{{
  "secretario_cultura": {{
    "nome": null,
    "email": null,
    "telefone": null,
    "instagram_url": null,
    "facebook_url": null,
    "confidence": 0.0
  }},
  "secretario_turismo": {{
    "nome": null,
    "email": null,
    "telefone": null,
    "instagram_url": null,
    "facebook_url": null,
    "confidence": 0.0
  }}
}}

Preencha apenas os campos que encontrar no texto. Confidence entre 0.0 e 1.0.
"""


def _get_groq():
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY nao definida no .env")
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


def _groq_wait():
    global _LAST_GROQ_CALL
    elapsed = time.monotonic() - _LAST_GROQ_CALL
    if elapsed < GROQ_MIN_INTERVAL:
        time.sleep(GROQ_MIN_INTERVAL - elapsed)
    _LAST_GROQ_CALL = time.monotonic()


def _fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers=HEADERS, allow_redirects=True, verify=False)
        if resp.status_code >= 400:
            return None
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception:
        return None


def _extract_text(html: str, max_chars: int = 4000) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)[:max_chars]


def _find_secretaria_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    found = []
    seen = set()
    base_domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = (a.get_text() or "").lower()
        full = urljoin(base_url, href)

        # Ignora links externos, anchors, arquivos
        if urlparse(full).netloc != base_domain:
            continue
        if full.endswith((".pdf", ".doc", ".xls", ".jpg", ".png")):
            continue
        if full in seen:
            continue

        # Prioriza links com palavras-chave no texto ou href
        combined = text + " " + href.lower()
        if any(kw in combined for kw in LINK_KEYWORDS):
            seen.add(full)
            found.append(full)

    return found[:10]  # maximo 10 links por site


def _groq_extract(text: str) -> dict:
    client = _get_groq()
    _groq_wait()
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": GROQ_SYSTEM},
                {"role": "user", "content": GROQ_PROMPT.format(texto=text)},
            ],
            response_format={"type": "json_object"},
            max_tokens=512,
            temperature=0.1,
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as exc:
        print(f"    [Groq erro: {exc}]")
        return {}


def _fmt_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    digits = "".join(c for c in raw if c.isdigit())
    if not digits or digits == "0":
        return None
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return digits


def scrape_municipality(mun: Municipality) -> dict | None:
    """Retorna dict com secretario_cultura e secretario_turismo, ou None se falhar."""
    base_url = mun.official_website.rstrip("/")

    # 1. Busca pagina principal
    html = _fetch(base_url)
    if not html:
        print(f"  ERRO: nao conseguiu acessar {base_url}")
        return None

    # 2. Tenta paths diretos comuns
    direct_texts = []
    for path in DIRECT_PATHS:
        url = base_url + path
        page_html = _fetch(url)
        if page_html:
            t = _extract_text(page_html, max_chars=2000)
            if t:
                direct_texts.append(t)
        time.sleep(0.2)
        if len(direct_texts) >= 4:
            break

    # 3. Busca links de secretaria na pagina principal (fallback)
    sec_links = _find_secretaria_links(html, base_url)
    extra_texts = []
    for link in sec_links[:4]:
        page_html = _fetch(link)
        if page_html:
            extra_texts.append(_extract_text(page_html, max_chars=1500))
        time.sleep(0.3)

    # 4. Consolida texto
    parts = []
    if direct_texts:
        parts.append("--- PAGINAS DIRETAS ---\n" + "\n\n".join(direct_texts))
    if extra_texts:
        parts.append("--- LINKS DESCOBERTOS ---\n" + "\n\n".join(extra_texts))
    if not parts:
        parts.append(_extract_text(html, max_chars=3000))

    full_text = "\n\n".join(parts)[:5500]
    found_pages = len(direct_texts) + len(extra_texts)
    print(f"  {found_pages} paginas com conteudo encontradas")

    # 5. Extrai via Groq
    result = _groq_extract(full_text)
    return result


_INSTITUTION_KEYWORDS = {
    "secretaria", "secretario", "departamento", "coordenadoria",
    "diretoria", "gerencia", "assessoria", "gabinete", "prefeitura",
    "municipal", "estadual", "federal", "fundacao", "instituto", "fundo",
    "centro", "nucleo", "divisao", "setor", "orgao", "servico",
    "cultura", "turismo", "esporte", "lazer", "desenvolvimento",
    "educacao", "saude", "obras", "financas", "administracao",
}


def _normalize_word(w: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode().lower()


def _is_person_name(nome: str) -> bool:
    """Rejeita se o nome parece ser uma instituicao ou titulo, nao uma pessoa."""
    words = {_normalize_word(w) for w in nome.split()}
    if words.intersection(_INSTITUTION_KEYWORDS):
        return False
    # Nome de pessoa tem pelo menos 2 palavras e nenhuma muito curta como "de turismo"
    real_words = [w for w in words if len(w) > 2]
    return len(real_words) >= 2


def _save_contact(db, mun: Municipality, role: str, data: dict, source_url: str, dry_run: bool):
    nome = data.get("nome")
    if not nome or str(nome).strip().lower() in ("null", "none", ""):
        return False
    if not _is_person_name(str(nome)):
        return False

    confidence = float(data.get("confidence", 0.5))
    if confidence < 0.3:
        return False

    email = data.get("email") if data.get("email") not in (None, "null") else None
    phone = _fmt_phone(data.get("telefone"))
    ig = data.get("instagram_url") if data.get("instagram_url") not in (None, "null") else None
    fb = data.get("facebook_url") if data.get("facebook_url") not in (None, "null") else None

    existing = (
        db.query(PublicContact)
        .filter(
            PublicContact.municipality_id == mun.id,
            PublicContact.role == role,
        )
        .first()
    )

    if existing:
        existing.name = nome
        existing.email = email
        existing.phone = phone
        existing.instagram_url = ig
        existing.facebook_url = fb
        existing.source_url = source_url
        existing.confidence_score = confidence
        status = "atualizado"
    else:
        if not dry_run:
            db.add(PublicContact(
                municipality_id=mun.id,
                name=nome,
                role=role,
                email=email,
                phone=phone,
                instagram_url=ig,
                facebook_url=fb,
                source_url=source_url,
                confidence_score=confidence,
            ))
        status = "criado"

    ig_tag = "ig" if ig else "  "
    ph_tag = "tel" if phone else "   "
    em_tag = "em" if email else "  "
    print(f"    [{role[:3]}] {nome:<35} [{ig_tag}][{ph_tag}][{em_tag}] conf={confidence:.1f} {status}")
    return True


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--municipio", type=str, help="Processar apenas este municipio")
    p.add_argument("--limit", type=int, default=0, help="Limite de municipios a processar")
    p.add_argument("--only-missing", action="store_true", help="Pula municipios que ja tem secretario salvo")
    return p.parse_args()


def main():
    args = parse_args()
    db = SessionLocal()
    try:
        q = db.query(Municipality).filter(
            Municipality.state == "MS",
            Municipality.official_website.isnot(None),
        ).order_by(Municipality.population.desc())

        if args.municipio:
            q = q.filter(Municipality.name.ilike(f"%{args.municipio}%"))

        munis = q.all()

        if args.only_missing:
            already_done = {
                c.municipality_id
                for c in db.query(PublicContact)
                .filter(PublicContact.role.like("secretario%"))
                .all()
            }
            munis = [m for m in munis if m.id not in already_done]
            print(f"  (--only-missing: {len(munis)} municipios sem secretario cadastrado)")

        if args.limit:
            munis = munis[: args.limit]

        print(f"Processando {len(munis)} municipios com site oficial cadastrado")

        created = updated = skipped = errors = 0

        for mun in munis:
            print(f"\n{mun.name} ({mun.official_website})")
            result = scrape_municipality(mun)
            time.sleep(SLEEP_BETWEEN_SITES)

            if not result:
                errors += 1
                continue

            sec_c = result.get("secretario_cultura") or {}
            sec_t = result.get("secretario_turismo") or {}

            saved_c = _save_contact(db, mun, "secretario_cultura", sec_c, mun.official_website, args.dry_run)
            saved_t = _save_contact(db, mun, "secretario_turismo", sec_t, mun.official_website, args.dry_run)

            if not saved_c and not saved_t:
                print(f"  Nenhum secretario identificado")
                skipped += 1
            else:
                if saved_c:
                    created += 1
                if saved_t:
                    created += 1

            if not args.dry_run:
                db.commit()

        print(f"\nResultado: {created} secretarios salvos | {skipped} sem dados | {errors} erros de acesso")
        if args.dry_run:
            print("Dry-run — nada salvo no banco.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
