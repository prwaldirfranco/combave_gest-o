import json
import os
import bcrypt

CAMINHO_USUARIOS = os.path.join("data", "usuarios.json")

def carregar_usuarios():
    """Carrega a lista de usuários a partir do JSON."""
    if os.path.exists(CAMINHO_USUARIOS):
        try:
            with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar usuários: {e}")
    return []

def salvar_usuarios(usuarios):
    """Salva a lista de usuários no JSON."""
    try:
        with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERRO] Falha ao salvar usuários: {e}")

def hash_password(senha: str) -> str:
    """Gera um hash bcrypt seguro a partir de uma senha em texto plano."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verificar_senha(senha_digitada: str, senha_armazenada: str) -> bool:
    """Compara a senha digitada com a senha armazenada (hash bcrypt ou texto puro)."""
    try:
        # Caso novo: senha hash bcrypt
        if isinstance(senha_armazenada, str) and senha_armazenada.startswith("$2b$"):
            return bcrypt.checkpw(senha_digitada.encode("utf-8"), senha_armazenada.encode("utf-8"))
        # Caso antigo (texto puro)
        return senha_digitada == senha_armazenada
    except Exception:
        return False

def verificar_credenciais(usuario: str, senha: str):
    """Verifica se o par (usuario, senha) é válido."""
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u.get("usuario") == usuario:
            if verificar_senha(senha, u.get("senha", "")):
                return u
            return None  # usuário encontrado, mas senha incorreta
    return None  # usuário não encontrado
