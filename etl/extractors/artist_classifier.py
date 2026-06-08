"""Classifica artistas usando Groq (Llama 3.3 70B).

Para cada artista sem fee_tier ou popularity_level, chama o LLM para inferir:
- main_style: sertanejo | forro | gospel | samba_pagode | outro
- sub_style: universitario | raiz | romantico | tradicional | louvor | pagode | samba | outro
- fee_tier: micro | pequeno | medio | grande
- popularity_level: local | estadual | nacional | nacional_top
"""
import json
import os

from groq import Groq

_CLIENT = None
_MODEL = "llama-3.3-70b-versatile"

_SYSTEM = (
    "Voce e um especialista no mercado de shows e eventos do interior do Brasil, "
    "especialmente Mato Grosso do Sul. Responda APENAS com JSON valido."
)

_PROMPT = """\
Classifique o artista/banda "{name}" para o mercado de eventos municipais brasileiros.

Retorne JSON com exatamente estas chaves:
- "main_style": genero principal — um de: sertanejo, forro, gospel, samba_pagode, outro
- "sub_style": subgenero — um de: universitario, raiz, romantico, tradicional, louvor, pagode, samba, outro
- "fee_tier": faixa de cache estimada — um de: micro (<50k), pequeno (50k-200k), medio (200k-500k), grande (>500k)
- "popularity_level": alcance — um de: local, estadual, nacional, nacional_top
- "confidence": numero 0.0 a 1.0 indicando confianca da classificacao

Contexto adicional: {context}
"""


def _get_client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY nao definida no .env")
        _CLIENT = Groq(api_key=api_key)
    return _CLIENT


def classify_artist(name: str, context: str = "") -> dict:
    """Classifica um artista via Groq.

    Retorna dict com main_style, sub_style, fee_tier, popularity_level, confidence.
    Em caso de erro retorna {"error": ..., "confidence": 0.0}.
    """
    client = _get_client()
    prompt = _PROMPT.format(name=name, context=context or "artista brasileiro")
    try:
        completion = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
            temperature=0.1,
        )
        text = completion.choices[0].message.content
        return json.loads(text)
    except json.JSONDecodeError as exc:
        return {"error": f"JSON invalido: {exc}", "confidence": 0.0}
    except Exception as exc:
        return {"error": str(exc), "confidence": 0.0}


VALID_MAIN_STYLES = {"sertanejo", "forro", "gospel", "samba_pagode", "outro"}
VALID_SUB_STYLES = {"universitario", "raiz", "romantico", "tradicional", "louvor", "pagode", "samba", "outro"}
VALID_FEE_TIERS = {"micro", "pequeno", "medio", "grande"}
VALID_POPULARITY = {"local", "estadual", "nacional", "nacional_top"}


def _validate(result: dict) -> dict:
    """Garante que os valores retornados estao dentro dos sets validos."""
    if result.get("main_style") not in VALID_MAIN_STYLES:
        result["main_style"] = "outro"
    if result.get("sub_style") not in VALID_SUB_STYLES:
        result["sub_style"] = "outro"
    if result.get("fee_tier") not in VALID_FEE_TIERS:
        result["fee_tier"] = None
    if result.get("popularity_level") not in VALID_POPULARITY:
        result["popularity_level"] = None
    return result


def classify_artist_validated(name: str, context: str = "") -> dict:
    result = classify_artist(name, context)
    if "error" in result:
        return result
    return _validate(result)
