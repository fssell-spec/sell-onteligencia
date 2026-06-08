"""Salva hits do Diário Oficial (DOE/MS e DIOGRANDE) no banco."""
import json
import unicodedata

from groq import Groq
from sqlalchemy.orm import Session

from app.models.diario_oficial_hit import DiarioOficialHit
from app.models.municipality import Municipality
from crawlers.diarios_oficiais.collector import DOCollectedHit
from crawlers.diogrande.collector import DGCollectedHit

# IBGE 5002704 = Campo Grande — todos os hits DIOGRANDE pertencem a este município
_CAMPO_GRANDE_IBGE = "5002704"
_campo_grande_id: int | None = None


def _get_campo_grande_id(db: Session) -> int | None:
    global _campo_grande_id
    if _campo_grande_id is None:
        m = db.query(Municipality.id).filter(Municipality.ibge_code == _CAMPO_GRANDE_IBGE).first()
        _campo_grande_id = m.id if m else None
    return _campo_grande_id

_SYSTEM_PROMPT = """\
Você receberá trechos de publicações do Diário Oficial do Mato Grosso do Sul sobre contratações.

Extraia:
- municipio: nome do município contratante (ex: "Campo Grande") ou null se não identificável
- artista: nome do artista/banda/dupla contratado(a) ou null
- tipo: EXATAMENTE um desses: inexigibilidade | dispensa | pregao | outro
- valor: valor em reais (número sem R$) ou null
- relevante: true se for contratação de show/evento/artista; false se irrelevante

Responda SOMENTE com JSON:
{"municipio": null, "artista": null, "tipo": "outro", "valor": null, "relevante": false}
"""

_muni_index: dict[str, int] = {}


def _normalize(s: str) -> str:
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


def _build_muni_index(db: Session) -> None:
    global _muni_index
    if not _muni_index:
        for m in db.query(Municipality.name, Municipality.id).filter(Municipality.state == "MS").all():
            _muni_index[_normalize(m.name)] = m.id


def _match_municipality(name: str | None, db: Session) -> int | None:
    if not name:
        return None
    _build_muni_index(db)
    key = _normalize(name)
    if key in _muni_index:
        return _muni_index[key]
    for muni_norm, muni_id in _muni_index.items():
        if muni_norm in key or key in muni_norm:
            return muni_id
    return None


def _extract_with_llm(groq: Groq, highlight: str) -> dict:
    _fallback = {"municipio": None, "artista": None, "tipo": "outro", "valor": None, "relevante": False}
    try:
        resp = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": highlight[:3000]},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=256,
        )
        result = json.loads(resp.choices[0].message.content)
        # Groq ocasionalmente retorna lista em vez de dict — pega o primeiro elemento
        if isinstance(result, list):
            result = result[0] if result else _fallback
        if not isinstance(result, dict):
            return _fallback
        return result
    except Exception:
        return _fallback


def save_diario_hits(
    db: Session,
    hits: list[DOCollectedHit],
    groq: Groq,
    verbose: bool = False,
) -> tuple[int, int]:
    """Salva hits com extração LLM. Retorna (criados, duplicatas)."""
    criados = 0
    duplicatas = 0

    for h in hits:
        # Dedup por (arquivo, pagina, keyword)
        exists = (
            db.query(DiarioOficialHit.id)
            .filter(
                DiarioOficialHit.arquivo == h.hit.nome_arquivo,
                DiarioOficialHit.pagina == h.hit.pagina,
                DiarioOficialHit.keyword == h.keyword,
            )
            .first()
        )
        if exists:
            duplicatas += 1
            continue

        extracted = _extract_with_llm(groq, h.hit.highlight or h.keyword)

        status = "irrelevante" if not extracted.get("relevante", False) else "novo"
        muni_id = _match_municipality(extracted.get("municipio"), db) if status == "novo" else None

        def _trunc(val, n=255):
            return val[:n] if isinstance(val, str) else val

        hit_obj = DiarioOficialHit(
            keyword=_trunc(h.keyword),
            data_publicacao=_trunc(h.hit.data_publicacao or ""),
            arquivo=_trunc(h.hit.nome_arquivo),
            pagina=h.hit.pagina,
            highlight=h.hit.highlight,
            municipio_detectado=_trunc(extracted.get("municipio")) if status == "novo" else None,
            municipio_id=muni_id,
            artista_detectado=_trunc(extracted.get("artista")) if status == "novo" else None,
            tipo_contratacao=_trunc(extracted.get("tipo", "outro"), 50),
            valor_estimado=float(extracted["valor"]) if extracted.get("valor") else None,
            confidence_score=0.8 if muni_id else (0.5 if status == "novo" else 0.2),
            status=status,
            raw_json=h.hit.raw,
        )
        db.add(hit_obj)
        criados += 1

        if verbose and status == "novo":
            muni = extracted.get("municipio") or "?"
            artista = extracted.get("artista") or "?"
            tipo = extracted.get("tipo") or "?"
            print(f"  + {muni} | {artista} | {tipo}")

    db.commit()
    return criados, duplicatas


def save_diogrande_hits(
    db: Session,
    hits: list[DGCollectedHit],
    verbose: bool = False,
) -> tuple[int, int]:
    """Salva hits do DIOGRANDE. Sem LLM — status='potencial' até download do PDF ser possível.

    Retorna (criados, duplicatas).
    """
    cg_id = _get_campo_grande_id(db)
    criados = 0
    duplicatas = 0

    for h in hits:
        arquivo = (h.edicao.arquivo or "").strip()
        if not arquivo:
            continue

        exists = (
            db.query(DiarioOficialHit.id)
            .filter(
                DiarioOficialHit.arquivo == arquivo,
                DiarioOficialHit.pagina == 0,
                DiarioOficialHit.keyword == h.keyword,
            )
            .first()
        )
        if exists:
            duplicatas += 1
            continue

        hit_obj = DiarioOficialHit(
            keyword=h.keyword[:100],
            data_publicacao=h.edicao.dia or None,
            arquivo=arquivo[:255],
            pagina=0,
            highlight=None,
            municipio_detectado="Campo Grande",
            municipio_id=cg_id,
            artista_detectado=None,
            tipo_contratacao="potencial",
            valor_estimado=None,
            confidence_score=0.4,
            status="potencial",
            raw_json={
                "fonte": "diogrande",
                "numero": h.edicao.numero,
                "desctpd": h.edicao.desctpd,
                "codigodia": h.edicao.codigodia,
            },
        )
        db.add(hit_obj)
        criados += 1

        if verbose:
            print(f"  DG + ed.{h.edicao.numero} ({h.edicao.dia}) | kw={h.keyword}")

    db.commit()
    return criados, duplicatas
