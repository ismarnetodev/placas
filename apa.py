import json
import os

ARQUIVO_USUARIOS = "usuarios_json"

def carregar_usuarios():
    # Verifica se o arquivo de usuários existe
    if not os.path.exists(ARQUIVO_USUARIOS):
        # Se não existir, cria um arquivo vazio com um objeto JSON vazio
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)
    # Abre o arquivo e carrega os dados dos usuários
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

print(json.dumps(indent=2))