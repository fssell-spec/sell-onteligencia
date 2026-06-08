"""Seed das 79 prefeituras do Mato Grosso do Sul com dados do IBGE."""
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality

# Dados: (ibge_code, nome, populacao_2022, area_km2, mesorregiao, microrregiao)
MUNICIPIOS_MS = [
    ("5000203", "Agua Clara",               15081,  11543, "Leste de Mato Grosso do Sul",        "Tres Lagoas"),
    ("5000252", "Alcinopolis",               4401,   7067, "Centro-Norte de Mato Grosso do Sul", "Alto Taquari"),
    ("5000609", "Amambai",                  38074,   4848, "Sudeste de Mato Grosso do Sul",       "Amambai"),
    ("5000708", "Anastacio",                24352,   3956, "Pantanais Sul-Mato-Grossenses",       "Aquidauana"),
    ("5000807", "Anaurilandia",              9500,   5131, "Leste de Mato Grosso do Sul",         "Nova Andradina"),
    ("5000856", "Angelica",                  8524,   2095, "Sudeste de Mato Grosso do Sul",       "Nova Andradina"),
    ("5000906", "Antonio Joao",             11948,   2820, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5001004", "Aparecida do Taboado",     24024,   2830, "Leste de Mato Grosso do Sul",         "Paranaiba"),
    ("5001102", "Aquidauana",               44297,  16958, "Pantanais Sul-Mato-Grossenses",       "Aquidauana"),
    ("5001243", "Aral Moreira",             15777,   2010, "Sudeste de Mato Grosso do Sul",       "Amambai"),
    ("5001508", "Bandeirantes",              6845,   3589, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5001904", "Bataguassu",               20716,   4490, "Leste de Mato Grosso do Sul",         "Nova Andradina"),
    ("5002001", "Bataypora",                10889,   2889, "Leste de Mato Grosso do Sul",         "Nova Andradina"),
    ("5002100", "Bela Vista",               23893,  10354, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5002159", "Bodoquena",                 8030,   3189, "Pantanais Sul-Mato-Grossenses",       "Bodoquena"),
    ("5002209", "Bonito",                   22960,   4934, "Pantanais Sul-Mato-Grossenses",       "Bodoquena"),
    ("5002308", "Brilandia",                13882,   5853, "Leste de Mato Grosso do Sul",         "Tres Lagoas"),
    ("5002407", "Caarapo",                  30316,   2574, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5002605", "Camapua",                  18157,   7246, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5002704", "Campo Grande",            895934,   8092, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5002803", "Caracol",                   5432,   3748, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5002902", "Cassilandia",              21968,   5591, "Leste de Mato Grosso do Sul",         "Paranaiba"),
    ("5002951", "Chapadao do Sul",          27903,   5741, "Leste de Mato Grosso do Sul",         "Paranaiba"),
    ("5003007", "Corguinho",                 5045,   3793, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5003056", "Coronel Sapucaia",         15207,    866, "Sudeste de Mato Grosso do Sul",       "Amambai"),
    ("5003108", "Corumba",                 109181,  64960, "Pantanais Sul-Mato-Grossenses",       "Corumba"),
    ("5003157", "Costa Rica",               19869,   5165, "Leste de Mato Grosso do Sul",         "Paranaiba"),
    ("5003207", "Coxim",                    35003,   6409, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5003256", "Deodapolis",               11773,   1307, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5003306", "Dois Irmaos do Buriti",    10917,   2340, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5003454", "Douradina",                 5524,   1024, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5003504", "Dourados",                221309,   4086, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5003702", "Eldorado",                 12071,   1589, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5003751", "Fatima do Sul",            21265,    847, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5003801", "Figueirao",                 3025,   4571, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5003900", "Gloria de Dourados",        9024,   1108, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5004007", "Guia Lopes da Laguna",     10906,   3044, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5004106", "Iguatemi",                 17912,   3124, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5004304", "Inocencia",                 9107,  10814, "Leste de Mato Grosso do Sul",         "Paranaiba"),
    ("5004403", "Itapora",                  26190,   2093, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5004502", "Itaquirai",                19885,   2419, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5004601", "Ivinhema",                 24847,   2481, "Sudeste de Mato Grosso do Sul",       "Nova Andradina"),
    ("5004700", "Japora",                    7117,    597, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5004809", "Jaraguari",                 7144,   2415, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5004908", "Jardim",                   27128,   5168, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5005004", "Jatei",                     4891,   2108, "Sudeste de Mato Grosso do Sul",       "Nova Andradina"),
    ("5005103", "Juti",                      7470,   2007, "Sudeste de Mato Grosso do Sul",       "Amambai"),
    ("5005202", "Ladario",                  21756,    346, "Pantanais Sul-Mato-Grossenses",       "Corumba"),
    ("5005251", "Laguna Carapa",             7498,   1406, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5005400", "Maracaju",                 44004,   5297, "Sudoeste de Mato Grosso do Sul",      "Campo Grande"),
    ("5005459", "Miranda",                  26880,   5497, "Pantanais Sul-Mato-Grossenses",       "Aquidauana"),
    ("5005507", "Mundo Novo",               20098,   1427, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5005681", "Navirai",                  56156,   3134, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5005707", "Nioaque",                  14974,   4981, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5005806", "Nova Alvorada do Sul",     14969,   2873, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5005905", "Nova Andradina",           55155,   5422, "Leste de Mato Grosso do Sul",         "Nova Andradina"),
    ("5006002", "Novo Horizonte do Sul",     3893,   1596, "Sudeste de Mato Grosso do Sul",       "Nova Andradina"),
    ("5006200", "Paranaiba",                42012,   8370, "Leste de Mato Grosso do Sul",         "Paranaiba"),
    ("5006259", "Paranhos",                 15118,   1396, "Sudeste de Mato Grosso do Sul",       "Amambai"),
    ("5006309", "Pedro Gomes",               8132,   5387, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5006358", "Ponta Pora",               89331,   5328, "Sudeste de Mato Grosso do Sul",       "Dourados"),
    ("5006408", "Porto Murtinho",           16010,  17739, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5006606", "Ribas do Rio Pardo",       25180,  17380, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5006903", "Rio Brilhante",            35213,   4290, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5007000", "Rio Negro",                 5024,   2188, "Sudoeste de Mato Grosso do Sul",      "Bodoquena"),
    ("5007109", "Rio Verde de Mato Grosso", 20310,   8075, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5007208", "Rochedo",                   4524,   2537, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5007307", "Santa Rita do Pardo",      10010,   7168, "Leste de Mato Grosso do Sul",         "Tres Lagoas"),
    ("5007406", "Sao Gabriel do Oeste",     24114,   3864, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5007695", "Selviria",                  7939,   2899, "Leste de Mato Grosso do Sul",         "Tres Lagoas"),
    ("5007802", "Sete Quedas",              12032,   2072, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5007901", "Sidrolandia",              50001,   6917, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5007952", "Sonora",                   12140,   5823, "Centro-Norte de Mato Grosso do Sul",  "Alto Taquari"),
    ("5008008", "Sul Brasil",                3481,    717, "Sudeste de Mato Grosso do Sul",       "Iguatemi"),
    ("5008107", "Tacuru",                   12075,   2137, "Sudeste de Mato Grosso do Sul",       "Amambai"),
    ("5008206", "Taquarussu",                4002,   1415, "Sudeste de Mato Grosso do Sul",       "Nova Andradina"),
    ("5007958", "Terenos",                  19966,   2950, "Centro-Sul de Mato Grosso do Sul",    "Campo Grande"),
    ("5008305", "Tres Lagoas",             125137,  10206, "Leste de Mato Grosso do Sul",         "Tres Lagoas"),
    ("5008404", "Vicentina",                 5491,    755, "Sudeste de Mato Grosso do Sul",       "Nova Andradina"),
]

# Nomes originais com acentuacao para exibicao no banco
NOMES_ORIGINAIS = {
    "5000203": "Água Clara",
    "5000252": "Alcinópolis",
    "5000609": "Amambai",
    "5000708": "Anastácio",
    "5000807": "Anaurilândia",
    "5000856": "Angélica",
    "5000906": "Antônio João",
    "5001004": "Aparecida do Taboado",
    "5001102": "Aquidauana",
    "5001243": "Aral Moreira",
    "5001508": "Bandeirantes",
    "5001904": "Bataguassu",
    "5002001": "Batayporã",
    "5002100": "Bela Vista",
    "5002159": "Bodoquena",
    "5002209": "Bonito",
    "5002308": "Brasilândia",
    "5002407": "Caarapó",
    "5002605": "Camapuã",
    "5002704": "Campo Grande",
    "5002803": "Caracol",
    "5002902": "Cassilândia",
    "5002951": "Chapadão do Sul",
    "5003007": "Corguinho",
    "5003056": "Coronel Sapucaia",
    "5003108": "Corumbá",
    "5003157": "Costa Rica",
    "5003207": "Coxim",
    "5003256": "Deodápolis",
    "5003306": "Dois Irmãos do Buriti",
    "5003454": "Douradina",
    "5003504": "Dourados",
    "5003702": "Eldorado",
    "5003751": "Fátima do Sul",
    "5003801": "Figueirão",
    "5003900": "Glória de Dourados",
    "5004007": "Guia Lopes da Laguna",
    "5004106": "Iguatemi",
    "5004304": "Inocência",
    "5004403": "Itaporã",
    "5004502": "Itaquiraí",
    "5004601": "Ivinhema",
    "5004700": "Japorã",
    "5004809": "Jaraguari",
    "5004908": "Jardim",
    "5005004": "Jateí",
    "5005103": "Juti",
    "5005202": "Ladário",
    "5005251": "Laguna Carapã",
    "5005400": "Maracaju",
    "5005459": "Miranda",
    "5005507": "Mundo Novo",
    "5005681": "Naviraí",
    "5005707": "Nioaque",
    "5005806": "Nova Alvorada do Sul",
    "5005905": "Nova Andradina",
    "5006002": "Novo Horizonte do Sul",
    "5006200": "Paranaíba",
    "5006259": "Paranhos",
    "5006309": "Pedro Gomes",
    "5006358": "Ponta Porã",
    "5006408": "Porto Murtinho",
    "5006606": "Ribas do Rio Pardo",
    "5006903": "Rio Brilhante",
    "5007000": "Rio Negro",
    "5007109": "Rio Verde de Mato Grosso",
    "5007208": "Rochedo",
    "5007307": "Santa Rita do Pardo",
    "5007406": "São Gabriel do Oeste",
    "5007695": "Selvíria",
    "5007802": "Sete Quedas",
    "5007901": "Sidrolândia",
    "5007952": "Sonora",
    "5008008": "Sul Brasil",
    "5008107": "Tacuru",
    "5008206": "Taquarussu",
    "5007958": "Terenos",
    "5008305": "Três Lagoas",
    "5008404": "Vicentina",
}

MESORREGIOES_ORIGINAIS = {
    "Leste de Mato Grosso do Sul":        "Leste de Mato Grosso do Sul",
    "Centro-Norte de Mato Grosso do Sul": "Centro-Norte de Mato Grosso do Sul",
    "Sudeste de Mato Grosso do Sul":      "Sudeste de Mato Grosso do Sul",
    "Pantanais Sul-Mato-Grossenses":      "Pantanais Sul-Mato-Grossenses",
    "Sudoeste de Mato Grosso do Sul":     "Sudoeste de Mato Grosso do Sul",
    "Centro-Sul de Mato Grosso do Sul":   "Centro-Sul de Mato Grosso do Sul",
}

MICRORREGIOES_ORIGINAIS = {
    "Tres Lagoas":     "Três Lagoas",
    "Alto Taquari":    "Alto Taquari",
    "Amambai":         "Amambaí",
    "Aquidauana":      "Aquidauana",
    "Nova Andradina":  "Nova Andradina",
    "Dourados":        "Dourados",
    "Paranaiba":       "Paranaíba",
    "Bodoquena":       "Bodoquena",
    "Corumba":         "Corumbá",
    "Campo Grande":    "Campo Grande",
    "Iguatemi":        "Iguatemi",
}


def normalize(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return nfkd.encode("ascii", "ignore").decode("ascii").lower().strip()


def seed():
    db = SessionLocal()
    try:
        existing = db.query(Municipality).count()
        if existing > 0:
            print(f"Banco ja contem {existing} prefeituras. Limpando para novo seed...")
            db.query(Municipality).delete()
            db.commit()

        municipios = []
        for ibge_code, nome_ascii, populacao, area_km2, mesorregiao_ascii, microrregiao_ascii in MUNICIPIOS_MS:
            nome_original = NOMES_ORIGINAIS[ibge_code]
            mesorregiao = MESORREGIOES_ORIGINAIS[mesorregiao_ascii]
            microrregiao = MICRORREGIOES_ORIGINAIS[microrregiao_ascii]
            m = Municipality(
                ibge_code=ibge_code,
                name=nome_original,
                normalized_name=normalize(nome_original),
                state="MS",
                population=populacao,
                area_km2=float(area_km2),
                mesorregiao=mesorregiao,
                microrregiao=microrregiao,
                region=mesorregiao,
            )
            municipios.append(m)

        db.add_all(municipios)
        db.commit()
        print(f"OK: {len(municipios)} prefeituras inseridas com sucesso.")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
