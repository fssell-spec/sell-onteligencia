"""Seed de fornecedores de estrutura para eventos no MS.

Cobre: arena, arquibancada, som, luz, led, seguranca, brigadista,
banheiro_quimico, gerador, portaria, producao.

Uso:
  python scripts/seed_fornecedores.py
"""
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.database import SessionLocal
from app.models.supplier import Supplier
from app.models.supplier_price import SupplierPrice
from app.models.enums import SupplierCategory


def normalize(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return nfkd.encode("ascii", "ignore").decode("ascii").lower().strip()


# (nome, categoria, cidade, estado, regiao_atendimento, contato, telefone, notas)
FORNECEDORES = [
    # --- Arena / Estrutura ---
    ("Pantanal Rodeios",       "arena",          "Campo Grande",  "MS", "MS inteiro",        "Marcos Oliveira", "(67) 99801-2233", "Arena desmontavel completa, currais, touro"),
    ("Arena MS Eventos",       "arena",          "Dourados",      "MS", "Grande Dourados",   "Edilson Souza",   "(67) 99712-4455", "Especialidade em rodeio e vaquejada"),
    ("Pantaneira Estruturas",  "arena",          "Corumba",       "MS", "Pantanal",          "Jose Alves",      "(67) 99623-1122", "Atende Corumba, Ladario e regiao"),
    ("Sul MS Arenas",          "arena",          "Ponta Pora",    "MS", "Sul do MS",         "Carlos Benites",  "(67) 99534-6677", "Arena com gradis e currais"),

    # --- Arquibancada ---
    ("Metalestrutura CG",      "arquibancada",   "Campo Grande",  "MS", "MS inteiro",        "Renato Lima",     "(67) 99845-3300", "Arquibancada metalica ate 5.000 lugares"),
    ("Norte MS Palcos",        "arquibancada",   "Tres Lagoas",   "MS", "Leste do MS",       "Flavio Moreira",  "(67) 99756-8899", "Palco + arquibancada pacote completo"),
    ("Estructura Plus",        "arquibancada",   "Dourados",      "MS", "Grande Dourados",   "Sergio Dias",     "(67) 99667-2211", "Arquibancada e grades de seguranca"),

    # --- Som ---
    ("SomMax Producoes",       "som",            "Campo Grande",  "MS", "MS inteiro",        "Thiago Castro",   "(67) 99878-5544", "PA line array, monitor, backline completo"),
    ("Studio Audio CG",        "som",            "Campo Grande",  "MS", "Grande CG",         "Bruno Farias",    "(67) 99789-6655", "Especialidade em shows sertanejos"),
    ("TechSound MS",           "som",            "Dourados",      "MS", "Sul do MS",         "Leandro Rios",    "(67) 99690-7766", "Equipamentos JBL e QSC"),
    ("Audio Eventos Tres L",   "som",            "Tres Lagoas",   "MS", "Leste do MS",       "Fabio Souza",     "(67) 99501-8877", "Atende regiao leste inclusive GO/SP"),

    # --- Luz ---
    ("IluminaCena MS",         "luz",            "Campo Grande",  "MS", "MS inteiro",        "Rafael Monteiro", "(67) 99812-4433", "Moving heads, strobo, laser"),
    ("LightShow Dourados",     "luz",            "Dourados",      "MS", "Grande Dourados",   "Vitor Alves",     "(67) 99723-5544", "Iluminacao conica e wash"),
    ("NeonFest MS",            "luz",            "Campo Grande",  "MS", "Grande CG",         "Mateus Nunes",    "(67) 99634-6655", "Especialidade em festas populares"),

    # --- LED ---
    ("LED Brasil MS",          "led",            "Campo Grande",  "MS", "MS inteiro",        "Anderson Lima",   "(67) 99945-1122", "Paineis P3, P4, P6 — ate 200m2"),
    ("MegaTela Eventos",       "led",            "Campo Grande",  "MS", "MS inteiro",        "Claudio Souza",   "(67) 99856-2233", "Telao outdoor e indoor"),

    # --- Seguranca ---
    ("Vigor Seguranca",        "seguranca",      "Campo Grande",  "MS", "MS inteiro",        "Paulo Matos",     "(67) 99867-3344", "Controle de acesso, seguranca patrimonial"),
    ("FortEvent MS",           "seguranca",      "Dourados",      "MS", "Sul do MS",         "Roberto Silva",   "(67) 99778-4455", "Seguranca para eventos ate 10.000 pessoas"),
    ("Guarda MS Eventos",      "seguranca",      "Tres Lagoas",   "MS", "Leste do MS",       "Marcio Costa",    "(67) 99689-5566", "Equipe de 20 a 200 agentes"),

    # --- Brigadista ---
    ("Prevencao Total MS",     "brigadista",     "Campo Grande",  "MS", "MS inteiro",        "Henrique Pinto",  "(67) 99790-6677", "Brigada de incendio certificada CBMMS"),
    ("SafeEvent Brigadistas",  "brigadista",     "Dourados",      "MS", "Sul do MS",         "Nelson Barros",   "(67) 99601-7788", "AVCB e laudo CBMMS inclusos"),

    # --- Banheiro Quimico ---
    ("Saniplan MS",            "banheiro_quimico","Campo Grande", "MS", "MS inteiro",        "Fernando Cruz",   "(67) 99912-8899", "Locacao e higienizacao diaria inclusa"),
    ("EcoSanit Eventos",       "banheiro_quimico","Dourados",     "MS", "Sul do MS",         "Adriano Lima",    "(67) 99823-9900", "PCD adaptados disponiveis"),

    # --- Gerador ---
    ("Geraluz MS",             "gerador",        "Campo Grande",  "MS", "MS inteiro",        "Cicero Alves",    "(67) 99734-0011", "Geradores 100 a 500kVA"),
    ("PowerFest MS",           "gerador",        "Dourados",      "MS", "Grande Dourados",   "Oliveiro Dias",   "(67) 99645-1122", "Diesel, manutencao no local inclusa"),

    # --- Portaria ---
    ("Acesso Eventos MS",      "portaria",       "Campo Grande",  "MS", "MS inteiro",        "Gustavo Reis",    "(67) 99856-2233", "Catracas, leitores QR, pulseiras RFID"),
    ("PontoCerto Eventos",     "portaria",       "Campo Grande",  "MS", "Grande CG",         "Tiago Mendes",    "(67) 99767-3344", "Gestao de entrada e credenciamento"),

    # --- Producao ---
    ("Sell Producoes MS",      "producao",       "Campo Grande",  "MS", "MS inteiro",        "Felipe Sell",     "(67) 99978-4455", "Producao completa de shows e rodeios"),
    ("Delta Eventos MS",       "producao",       "Campo Grande",  "MS", "MS inteiro",        "Luciana Borges",  "(67) 99889-5566", "Direcao artistica, rider tecnico, logistica"),
    ("Bravo Entretenimento",   "producao",       "Dourados",      "MS", "Sul do MS",         "Renata Campos",   "(67) 99790-6677", "Producao regional especializada em sertanejo"),
]

# preco por categoria: (servico, unidade, min, avg, max)
PRECOS = {
    "arena": [
        ("Arena desmontavel 3 dias (ate 3000 lugares)", "evento", 18000, 32000, 60000),
        ("Arena desmontavel 1 dia (ate 1500 lugares)",  "evento",  8000, 15000, 28000),
        ("Currais e baias para rodeio",                 "evento",  3000,  6000, 12000),
    ],
    "arquibancada": [
        ("Arquibancada metalica 1000 lugares",  "evento",  5000,  9000, 16000),
        ("Arquibancada metalica 3000 lugares",  "evento", 12000, 22000, 40000),
        ("Palco coberto 8x6m",                  "evento",  6000, 11000, 20000),
        ("Palco coberto 12x10m",                "evento", 14000, 24000, 45000),
    ],
    "som": [
        ("PA line array pequeno (ate 1500 pax)", "evento",  4000,  8000, 15000),
        ("PA line array medio (ate 5000 pax)",   "evento",  9000, 18000, 30000),
        ("PA line array grande (ate 15000 pax)", "evento", 20000, 38000, 65000),
        ("Sistema de monitor e backline",         "evento",  2000,  4000,  8000),
    ],
    "luz": [
        ("Iluminacao show pequeno (ate 1500 pax)",  "evento",  3000,  6000, 12000),
        ("Iluminacao show medio (ate 5000 pax)",    "evento",  7000, 14000, 25000),
        ("Iluminacao show grande (ate 15000 pax)",  "evento", 15000, 28000, 50000),
    ],
    "led": [
        ("Painel LED 20m2 (backdrop)",   "evento",  4000,  8000, 15000),
        ("Painel LED 60m2 (backdrop)",   "evento", 10000, 18000, 32000),
        ("Telao lateral 15m2",           "evento",  3000,  6000, 11000),
    ],
    "seguranca": [
        ("Seguranca evento (10 agentes/dia)",  "dia",  1500,  3000,  5500),
        ("Seguranca evento (30 agentes/dia)",  "dia",  3500,  7000, 12000),
        ("Seguranca evento (80 agentes/dia)",  "dia",  8000, 16000, 28000),
    ],
    "brigadista": [
        ("Brigada incendio (5 brigadistas/dia)",  "dia",  1200,  2200,  4000),
        ("Brigada incendio (15 brigadistas/dia)", "dia",  3000,  5500,  9000),
    ],
    "banheiro_quimico": [
        ("Kit 10 banheiros quimicos (3 dias)",  "evento", 1500,  2800,  5000),
        ("Kit 30 banheiros quimicos (3 dias)",  "evento", 3500,  6500, 11000),
        ("Kit 10 banheiros PCD (3 dias)",       "evento", 2000,  3500,  6000),
    ],
    "gerador": [
        ("Gerador 150kVA (3 dias)",  "evento",  3500,  6500, 11000),
        ("Gerador 300kVA (3 dias)",  "evento",  6000, 11000, 18000),
        ("Gerador 500kVA (3 dias)",  "evento",  9000, 16000, 28000),
    ],
    "portaria": [
        ("Portaria basica (2 catracas + equipe)",  "evento",  2000,  4000,  7000),
        ("Portaria completa RFID (5 catracas)",    "evento",  5000, 10000, 18000),
    ],
    "producao": [
        ("Producao executiva show simples",     "evento",  5000, 10000, 20000),
        ("Producao executiva rodeio completo",  "evento", 15000, 30000, 60000),
        ("Rider tecnico e logistica artista",   "evento",  2000,  4500,  9000),
    ],
}


def main() -> None:
    db = SessionLocal()
    try:
        criados = atualizados = precos_criados = 0

        for row in FORNECEDORES:
            nome, cat_str, cidade, estado, regiao, contato, telefone, notas = row
            norm = normalize(nome)

            existing = db.query(Supplier).filter_by(normalized_name=norm).first()
            if existing:
                atualizados += 1
                supplier = existing
            else:
                supplier = Supplier(
                    name=nome,
                    normalized_name=norm,
                    category=SupplierCategory[cat_str],
                    city=cidade,
                    state=estado,
                    service_region=regiao,
                    contact_name=contato,
                    phone=telefone,
                    notes=notas,
                )
                db.add(supplier)
                db.flush()
                criados += 1

            # insere precos se ainda nao tem nenhum
            if not supplier.prices:
                cat_precos = PRECOS.get(cat_str, [])
                for servico, unidade, pmin, pavg, pmax in cat_precos:
                    p = SupplierPrice(
                        supplier_id=supplier.id,
                        service_description=servico,
                        unit_type=unidade,
                        min_price=pmin,
                        avg_price=pavg,
                        max_price=pmax,
                        source_type="seed_manual",
                        confidence_score=0.70,
                    )
                    db.add(p)
                    precos_criados += 1

        db.commit()
        print(f"Fornecedores: {criados} criados, {atualizados} ja existiam")
        print(f"Precos: {precos_criados} inseridos")

    finally:
        db.close()


if __name__ == "__main__":
    main()
