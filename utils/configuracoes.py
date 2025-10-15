
import json
import os

CAMINHO_CONFIG = "data/configuracoes.json"

def carregar_config():
    if os.path.exists(CAMINHO_CONFIG):
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"nome_igreja": "Nome da Igreja", "logo": ""}

def salvar_config(config):
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
