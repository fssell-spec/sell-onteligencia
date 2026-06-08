"""
Consulta contratos em aberto para prospecção esta semana.
Execute: python consulta_contratos_abertos.py
"""
import sys
import json
from datetime import date

try:
    import psycopg2
except ImportError:
    print("Instalando psycopg2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="sell_inteligencia",
    user="sell_user", password="sell_password"
)
cur = conn.cursor()
today = date.today()

# 1. Contratos show artístico com vigência ativa
cur.execute("""
    SELECT
        m.name AS municipio,
        c.contract_number,
        c.object_description,
        c.value,
        c.start_date,
        c.end_date,
        c.status,
        c.source
    FROM contracts c
    JOIN municipalities m ON c.municipality_id = m.id
    WHERE
        (c.end_date >= %s OR c.end_date IS NULL)
        AND (
            c.contract_type = 'show_artistico'
            OR c.object_description ILIKE '%show%'
            OR c.object_description ILIKE '%artista%'
            OR c.object_description ILIKE '%musical%'
            OR c.object_description ILIKE '%sertanejo%'
            OR c.object_description ILIKE '%forró%'
            OR c.object_description ILIKE '%festa%'
            OR c.object_description ILIKE '%rodeio%'
        )
    ORDER BY c.end_date ASC NULLS LAST
""", (today,))

rows = cur.fetchall()
cols = [d[0] for d in cur.description]
contratos = [dict(zip(cols, r)) for r in rows]
for c in contratos:
    for k, v in c.items():
        if hasattr(v, 'isoformat'):
            c[k] = v.isoformat()

# 2. Top oportunidades (score)
cur.execute("""
    SELECT
        m.name AS municipio,
        o.score,
        o.status,
        o.next_action,
        o.next_action_date,
        o.notes
    FROM opportunities o
    JOIN municipalities m ON o.municipality_id = m.id
    ORDER BY o.score DESC
    LIMIT 20
""")
rows2 = cur.fetchall()
cols2 = [d[0] for d in cur.description]
oportunidades = [dict(zip(cols2, r)) for r in rows2]
for o in oportunidades:
    for k, v in o.items():
        if hasattr(v, 'isoformat'):
            o[k] = v.isoformat()

cur.close()
conn.close()

result = {"contratos_abertos": contratos, "top_oportunidades": oportunidades}

with open("resultado_consulta.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n=== CONTRATOS ABERTOS ({len(contratos)}) ===")
for c in contratos:
    print(f"  {c['municipio']:30} | Vence: {c.get('end_date','?'):12} | R${c.get('value') or 0:>10,.0f} | {(c.get('object_description') or '')[:60]}")

print(f"\n=== TOP OPORTUNIDADES (score) ===")
for o in oportunidades[:10]:
    print(f"  {o['municipio']:30} | Score: {o['score']:5.1f} | Status: {o['status']:15} | {o.get('next_action') or ''}")

print("\nResultado completo salvo em: resultado_consulta.json")
