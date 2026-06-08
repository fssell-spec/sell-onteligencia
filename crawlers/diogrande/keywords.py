"""Termos de busca para o DIOGRANDE (Diário Oficial de Campo Grande).

Retorna edições inteiras (sem highlights) — termos específicos têm mais sinal.
A API faz busca por substring, case-insensitive, sem distinção de acentos.
"""

BUSCAS_DG: list[str] = [
    # Frases específicas de contratação direta de artistas
    "artista exclusivo",
    "empresario exclusivo",
    "notoria especializacao",
    "banda musical",
    "artista musical",
    # Gêneros — sem espaço (aparece como palavra isolada no texto do DO)
    "sertanejo",
    "sertaneja",
    "pagode",
    # Eventos diretos
    "show musical",
    "show artistico",
    "apresentacao artistica",
]
