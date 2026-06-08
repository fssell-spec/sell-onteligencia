import logging; logging.disable(logging.CRITICAL)
import sys; sys.path.insert(0, '.')
from dotenv import load_dotenv; load_dotenv('.env')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Hits com municipio_id resolvido - de onde vem?
print('=== Hits COM municipio_id (amostra) ===')
rows = db.execute(text("""
    SELECT d.id, d.arquivo, d.municipio_detectado, m.name as muni_name,
           d.keyword, LEFT(d.highlight, 100) as trecho
    FROM diario_oficial_hits d
    JOIN municipalities m ON d.municipio_id = m.id
    WHERE d.artista_detectado IS NOT NULL AND d.artista_detectado != ''
    LIMIT 5
""")).fetchall()
for r in rows:
    print(f'  arquivo={r[1]}  detectado="{r[2]}"  resolvido={r[3]}')

# Hits com municipio_detectado real (nao null, nao vazio)
print('\n=== Hits com municipio_detectado real (sem FK) ===')
rows2 = db.execute(text("""
    SELECT id, municipio_detectado, LEFT(highlight, 100) as trecho
    FROM diario_oficial_hits
    WHERE municipio_id IS NULL
      AND municipio_detectado IS NOT NULL
      AND municipio_detectado != ''
      AND municipio_detectado != 'null'
      AND artista_detectado IS NOT NULL
""")).fetchall()
for r in rows2:
    print(f'  id={r[0]}  detectado="{r[1]}"')
    print(f'  trecho: {r[2]}')

# Highlight text with municipality patterns for null ones
print('\n=== Tentando extrair municipio do highlight para hits null ===')
rows3 = db.execute(text("""
    SELECT id, highlight
    FROM diario_oficial_hits
    WHERE municipio_id IS NULL
      AND municipio_detectado = 'null'
      AND highlight ILIKE '%campo grande%'
       OR highlight ILIKE '%dourados%'
       OR highlight ILIKE '%tres lagoas%'
    LIMIT 5
""")).fetchall()
print(f'  Hits com nome de municipio no trecho: {len(rows3)}')

db.close()
