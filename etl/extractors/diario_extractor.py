"""Extrai informacoes de paginas do Diario Oficial via pdfplumber + Groq."""
import io
import json
import os
import time

import pdfplumber
from groq import Groq

_CLIENT = None
_MODEL = "llama-3.1-8b-instant"
_LAST_CALL: float = 0.0
_MIN_INTERVAL = 20.0  # segundos entre chamadas (evita rate limit do Groq)

_SYSTEM = (
    "Voce e um especialista em contratos publicos brasileiros. "
    "Analise textos de Diarios Oficiais e extraia dados estruturados. "
    "Responda APENAS com JSON valido."
)

_PROMPT = """\
Analise este trecho do Diario Oficial do Mato Grosso do Sul.
Se nao houver contratacao de artista/show, retorne {{"relevante": false}}.

Texto:
{texto}

Se houver contratacao de artista ou show, retorne JSON com:
- "relevante": true
- "municipio": nome do municipio contratante (null se orgao estadual)
- "artista_nome": nome do artista ou banda (null se nao identificado)
- "nome_evento": nome do evento ou festa (null se nao identificado)
- "valor": valor em reais como numero sem formatacao (null se nao mencionado)
- "data_evento_iso": data ISO AAAA-MM-DD do evento (null se nao mencionado)
- "data_evento_texto": periodo textual do evento (null se nao mencionado)
- "modalidade": "inexigibilidade", "dispensa", "pregao" ou null
- "notas": observacao util para empresa de shows, max 40 palavras, ou null
- "confidence": numero 0.0 a 1.0
"""


def _get_client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY nao definida no .env")
        _CLIENT = Groq(api_key=api_key)
    return _CLIENT


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            texts = [p.extract_text() or "" for p in pdf.pages]
            return "\n\n".join(t.strip() for t in texts if t.strip())
    except Exception as exc:
        return f"[ERRO PDF: {exc}]"


def _rate_wait() -> None:
    global _LAST_CALL
    elapsed = time.monotonic() - _LAST_CALL
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _LAST_CALL = time.monotonic()


def extract_diario_info(text: str, _retries: int = 4) -> dict:
    """Extrai dados estruturados de texto de pagina do DO via Groq."""
    client = _get_client()
    for attempt in range(_retries):
        _rate_wait()
        try:
            completion = client.chat.completions.create(
                model=_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": _PROMPT.format(texto=text[:3000])},
                ],
                response_format={"type": "json_object"},
                max_tokens=512,
                temperature=0.1,
            )
            return json.loads(completion.choices[0].message.content)
        except json.JSONDecodeError as exc:
            return {"error": f"JSON invalido: {exc}", "confidence": 0.0, "relevante": False}
        except Exception as exc:
            msg = str(exc)
            if "429" in msg and attempt < _retries - 1:
                wait = 20 * (attempt + 1)
                print(f"[rate limit, aguardando {wait}s]", end=" ", flush=True)
                time.sleep(wait)
                continue
            return {"error": msg, "confidence": 0.0, "relevante": False}
    return {"error": "max retries", "confidence": 0.0, "relevante": False}
