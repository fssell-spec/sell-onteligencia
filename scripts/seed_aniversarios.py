"""Popula aniversario_mes e aniversario_dia para os 79 municipios do MS.

Datas baseadas nas leis de emancipacao municipais do MS, que sao as datas
oficialmente celebradas pelas prefeituras. Verificar pontualmente em caso
de duvida — especialmente municipios criados em 11/12/1990 e 30/03/1993.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality

# (ibge_code): (mes, dia)
# Fontes: leis estaduais MS, IBGE historico, sites das prefeituras
ANIVERSARIOS: dict[str, tuple[int, int]] = {
    "5000203": (10, 10),  # Água Clara
    "5000252": (12, 11),  # Alcinópolis — Lei 1.199/1990
    "5000609": (6,  14),  # Amambai
    "5000708": (2,   8),  # Anastácio
    "5000807": (3,  30),  # Anaurilândia — Lei 6.533/1993
    "5000856": (12, 11),  # Angélica — Lei 1.199/1990
    "5000906": (11, 10),  # Antônio João
    "5001004": (7,  26),  # Aparecida do Taboado
    "5001102": (12,  9),  # Aquidauana
    "5001243": (12, 11),  # Aral Moreira — Lei 1.199/1990
    "5001508": (12, 11),  # Bandeirantes — Lei 1.199/1990
    "5001904": (9,  14),  # Bataguassu
    "5002001": (9,   8),  # Batayporã
    "5002100": (2,  27),  # Bela Vista
    "5002159": (12, 11),  # Bodoquena — Lei 1.199/1990
    "5002209": (7,  20),  # Bonito
    "5002308": (9,   4),  # Brasilândia
    "5002407": (3,  30),  # Caarapó — Lei 6.533/1993
    "5002605": (8,   1),  # Camapuã
    "5002704": (8,  26),  # Campo Grande
    "5002803": (12, 11),  # Caracol — Lei 1.199/1990
    "5002902": (12, 11),  # Cassilândia — Lei 1.199/1990
    "5002951": (10, 22),  # Chapadão do Sul
    "5003007": (9,  14),  # Corguinho
    "5003056": (12, 11),  # Coronel Sapucaia — Lei 1.199/1990
    "5003108": (9,  21),  # Corumbá
    "5003157": (12, 11),  # Costa Rica — Lei 1.199/1990
    "5003207": (1,  11),  # Coxim
    "5003256": (3,  30),  # Deodápolis — Lei 6.533/1993
    "5003306": (12, 11),  # Dois Irmãos do Buriti — Lei 1.199/1990
    "5003454": (12, 11),  # Douradina — Lei 1.199/1990
    "5003504": (12, 20),  # Dourados
    "5003702": (11, 10),  # Eldorado
    "5003751": (3,  30),  # Fátima do Sul — Lei 6.533/1993
    "5003801": (12, 11),  # Figueirão — Lei 1.199/1990
    "5003900": (3,  30),  # Glória de Dourados — Lei 6.533/1993
    "5004007": (11,  8),  # Guia Lopes da Laguna
    "5004106": (11, 10),  # Iguatemi
    "5004304": (9,  12),  # Inocência
    "5004403": (3,  30),  # Itaporã — Lei 6.533/1993
    "5004502": (11, 10),  # Itaquiraí
    "5004601": (11, 10),  # Ivinhema
    "5004700": (12, 11),  # Japorã — Lei 1.199/1990
    "5004809": (3,   2),  # Jaraguari
    "5004908": (10,  3),  # Jardim
    "5005004": (3,  30),  # Jateí — Lei 6.533/1993
    "5005103": (12, 11),  # Juti — Lei 1.199/1990
    "5005202": (10,  3),  # Ladário
    "5005251": (12, 11),  # Laguna Carapã — Lei 1.199/1990
    "5005400": (9,  28),  # Maracaju
    "5005459": (7,  24),  # Miranda
    "5005507": (11, 10),  # Mundo Novo
    "5005681": (11, 10),  # Naviraí
    "5005707": (8,   6),  # Nioaque
    "5005806": (10, 17),  # Nova Alvorada do Sul
    "5005905": (11, 28),  # Nova Andradina
    "5006002": (12, 11),  # Novo Horizonte do Sul — Lei 1.199/1990
    "5006200": (12,  3),  # Paranaíba
    "5006259": (11, 10),  # Paranhos
    "5006309": (11, 11),  # Pedro Gomes
    "5006358": (8,  28),  # Ponta Porã
    "5006408": (10,  6),  # Porto Murtinho
    "5006606": (10, 26),  # Ribas do Rio Pardo
    "5006903": (7,  14),  # Rio Brilhante
    "5007000": (12, 11),  # Rio Negro — Lei 1.199/1990
    "5007109": (9,  29),  # Rio Verde de Mato Grosso
    "5007208": (9,  22),  # Rochedo
    "5007307": (3,  30),  # Santa Rita do Pardo — Lei 6.533/1993
    "5007406": (12, 18),  # São Gabriel do Oeste
    "5007695": (10,  1),  # Selvíria
    "5007802": (11, 10),  # Sete Quedas
    "5007901": (8,  24),  # Sidrolândia
    "5007952": (12, 11),  # Sonora — Lei 1.199/1990
    "5008008": (12, 11),  # Sul Brasil — Lei 1.199/1990
    "5008107": (11, 10),  # Tacuru
    "5008206": (12, 11),  # Taquarussu — Lei 1.199/1990
    "5007958": (3,  30),  # Terenos — Lei 6.533/1993
    "5008305": (12, 20),  # Três Lagoas
    "5008404": (12, 11),  # Vicentina — Lei 1.199/1990
}


def seed():
    db = SessionLocal()
    try:
        atualizados = 0
        sem_data = []

        municipios = db.query(Municipality).filter(Municipality.state == "MS").all()
        for m in municipios:
            data = ANIVERSARIOS.get(m.ibge_code)
            if data:
                m.aniversario_mes, m.aniversario_dia = data
                atualizados += 1
            else:
                sem_data.append(m.name)

        db.commit()
        print(f"OK: {atualizados} municipios atualizados com data de aniversario.")
        if sem_data:
            print(f"Sem data: {sem_data}")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
