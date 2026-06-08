"""Extrae informacoes estruturadas de contratos publicos usando Groq API."""
import json
import os

from groq import Groq

_CLIENT = None
_MODEL = "llama-3.3-70b-versatile"

_SYSTEM = (
    "Voce e um assistente especializado em contratos publicos brasileiros "
    "de eventos e shows. Responda APENAS com JSON valido."
)

_PROMPT = """\
Analise este contrato publico e extraia as informacoes abaixo.
Use null para campos nao disponiveis.

{context}

Retorne JSON com exatamente estas chaves:
- "event_name": nome do evento (ex: "Festa da Pecuaria 2024") ou null
- "event_date_iso": data ISO do evento (AAAA-MM-DD) ou null -- primeiro dia se periodo
- "event_date_text": descricao textual do periodo (ex: "9 a 14 de fevereiro de 2024") ou null
- "artist_name": nome do artista ou banda contratado, senao null
- "services": lista de ate 3 strings resumindo os servicos/itens
- "notes": observacao util para empresa de shows (max 40 palavras) ou null
- "confidence": numero 0.0 a 1.0 indicando confianca geral
"""


def _get_client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY nao definida no .env")
        _CLIENT = Groq(api_key=api_key)
    return _CLIENT


def _build_context(description: str, items: list[dict]) -> str:
    ctx = f"Objeto: {description}"
    if items:
        lines = []
        for it in items[:10]:
            desc = it.get("descricao", "")
            qtd = it.get("quantidade", "")
            un = it.get("unidade", "")
            val = it.get("valor_total") or it.get("valor_unitario") or ""
            info = it.get("info") or ""
            line = f"- {desc}"
            if qtd and un:
                line += f" ({qtd} {un})"
            if val:
                line += f" R$ {val:.2f}" if isinstance(val, float) else f" R$ {val}"
            if info:
                line += f" -- {info[:60]}"
            lines.append(line)
        ctx += "\n\nItens do contrato:\n" + "\n".join(lines)
    return ctx


def extract_contract_info(description: str, items: list[dict] | None = None) -> dict:
    """Extrai campos estruturados de um contrato via Groq (Llama 3.3 70B).

    Aceita description (obrigatorio) e items opcionais do PNCP para contexto mais rico.
    Retorna dict com: event_name, event_date_iso, event_date_text, artist_name,
    services, notes, confidence. Em caso de erro retorna {"error": ..., "confidence": 0.0}.
    """
    client = _get_client()
    context = _build_context(description[:2000], items or [])
    try:
        completion = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": _PROMPT.format(context=context)},
            ],
            response_format={"type": "json_object"},
            max_tokens=512,
            temperature=0.1,
        )
        text = completion.choices[0].message.content
        return json.loads(text)
    except json.JSONDecodeError as exc:
        return {"error": f"JSON invalido: {exc}", "confidence": 0.0}
    except Exception as exc:
        return {"error": str(exc), "confidence": 0.0}
