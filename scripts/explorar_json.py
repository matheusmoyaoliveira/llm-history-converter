import json
import sys
from pathlib import Path


def mostrar_estrutura(valor, nivel=0, nivel_maximo=4):
    if nivel > nivel_maximo:
        return

    recuo = "  " * nivel

    if isinstance(valor, dict):
        for chave, item in valor.items():
            print(f"{recuo}{chave}: {type(item).__name__}")
            mostrar_estrutura(item, nivel + 1, nivel_maximo)

    elif isinstance(valor, list):
        print(f"{recuo}[lista com {len(valor)} itens]")
        if valor:
            mostrar_estrutura(valor[0], nivel + 1, nivel_maximo)


caminho = Path(sys.argv[1])
dados = json.loads(caminho.read_text(encoding="utf-8"))

print(f"Arquivo: {caminho.name}")
print(f"Tipo principal: {type(dados).__name__}\n")
mostrar_estrutura(dados, nivel_maximo=6)