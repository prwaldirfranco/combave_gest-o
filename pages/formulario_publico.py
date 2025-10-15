import streamlit as st
import json
import os
import uuid
from datetime import datetime, date
from pathlib import Path

# Caminhos
CAMINHO_BASE = Path("data")
CAMINHO_FORMULARIOS = CAMINHO_BASE / "formularios.json"
CAMINHO_RESPOSTAS = CAMINHO_BASE / "respostas_formularios.json"

# Garante que o diretório 'data' exista
CAMINHO_BASE.mkdir(exist_ok=True)

# --- Funções de Leitura/Escrita ---

def carregar_json(caminho):
    """Carrega a lista de dados do arquivo JSON de forma segura."""
    if caminho.exists():
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                # Retorna a lista se o arquivo não estiver vazio, caso contrário, retorna []
                conteudo = f.read()
                return json.loads(conteudo) if conteudo else []
        except json.JSONDecodeError:
            return []
    return []

def salvar_resposta(resposta):
    """Salva uma nova resposta no arquivo JSON."""
    dados = carregar_json(CAMINHO_RESPOSTAS)
    
    # Adiciona nova resposta
    dados.append(resposta)
    
    with open(CAMINHO_RESPOSTAS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- Função Principal de Exibição ---

def exibir():
    st.set_page_config(layout="wide")
    st.title("📝 Formulário Dinâmico")
    
    # 1. Captura e Validação do ID
    params = st.query_params
    # Usamos .get() com fallback para segurança
    form_id = params.get("id", None)

    if not form_id:
        st.error("❌ Erro: ID do formulário não foi fornecido na URL.")
        st.info("Exemplo de URL: `?id=SEU_ID_UNICO`")
        return

    formularios = carregar_json(CAMINHO_FORMULARIOS)
    formulario = next((f for f in formularios if f.get("id") == form_id), None)

    if not formulario:
        st.error(f"❌ Erro: Formulário com ID '{form_id}' não encontrado.")
        return

    # 2. Renderização do Título e Descrição
    st.header(formulario.get("titulo", "Formulário sem Título"))
    st.markdown(f"*{formulario.get('descricao', 'Preencha os campos abaixo.')}*")
    st.markdown("---")

    # Verifica se o estado de sucesso já foi definido e exibe a mensagem, impedindo reenvio
    if st.session_state.get(f"form_submitted_{form_id}", False):
        st.balloons()
        st.success("✅ **Obrigado! Sua resposta foi registrada com sucesso!**")
        st.info("Você pode fechar esta página.")
        return
    
    # 3. Geração e Submissão do Formulário
    respostas = {}
    campos_faltando = False
    
    # Usamos um container para submissão, mas a validação precisa ser feita no botão
    with st.form("responder_formulario", clear_on_submit=False):
        
        # 3.1. Gera campos dinamicamente e coleta respostas
        for campo in formulario.get("campos", []):
            tipo = campo.get("tipo")
            pergunta = campo.get("pergunta")
            obrigatorio = campo.get("obrigatorio", False)
            
            label = pergunta + (" *" if obrigatorio else "")
            key = f"input_{campo.get('id') or pergunta.replace(' ', '_')}"

            valor = None
            
            # Mapeamento de Tipos de Campo
            if tipo == "texto":
                valor = st.text_input(label, key=key)
            elif tipo == "texto_longo":
                valor = st.text_area(label, key=key)
            elif tipo == "numero":
                # Usamos None como valor inicial, o que é seguro para validação
                valor = st.number_input(label, key=key, value=None, format="%g")
            elif tipo == "opcoes":
                opcs = campo.get("opcoes", [])
                # Adiciona uma opção de "Selecione..." se for obrigatório e não tiver padrão
                opcs_com_placeholder = (["Selecione..."] + opcs) if obrigatorio else opcs
                valor = st.selectbox(label, opcs_com_placeholder, key=key)
                if obrigatorio and valor == "Selecione...":
                     valor = "" # Define como vazio para falhar na validação
            elif tipo == "checkbox":
                valor = st.checkbox(pergunta, key=key) # Checkbox não tem label de "obrigatorio" na UI padrão
            elif tipo == "data":
                valor = st.date_input(label, key=key, value=date.today())
                
            respostas[pergunta] = valor

        st.markdown("---")
        enviado = st.form_submit_button("✅ Enviar Resposta", type="primary", use_container_width=True)

        if enviado:
            # 3.2. Validação dos Campos Obrigatórios
            campos_faltando = False
            for campo in formulario.get("campos", []):
                pergunta = campo.get("pergunta")
                obrigatorio = campo.get("obrigatorio", False)
                
                # Checkbox False é um valor válido. Valida apenas se for True ou se não for Checkbox
                if obrigatorio and (respostas.get(pergunta) in [None, "", "Selecione..."] or (campo.get("tipo") == "checkbox" and respostas.get(pergunta) is False)):
                    campos_faltando = True
                    # O streamlit não permite interromper a execução do formulário facilmente. 
                    # Usaremos o erro final.

            if campos_faltando:
                st.error("🚨 Por favor, preencha **todos os campos obrigatórios** (*).")
                # Não salva e mantém o estado
                return
            
            # 3.3. Salvamento e Confirmação
            resposta_salvar = {
                "id_resposta": str(uuid.uuid4()),
                "id_formulario": form_id,
                "respostas": respostas,
                "enviado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            salvar_resposta(resposta_salvar)
            
            # Define o estado de sucesso e reruns para mostrar a mensagem final e desativar o formulário
            st.session_state[f"form_submitted_{form_id}"] = True
            st.rerun()

# --- Estrutura de Exemplo para Teste ---
# Para testar, crie um arquivo 'data/formularios.json' com este conteúdo:
"""
[
  {
    "id": "cadastro_membro_temp",
    "titulo": "Ficha de Pré-Cadastro de Membro",
    "descricao": "Preencha suas informações para iniciar seu cadastro na igreja.",
    "campos": [
      {"id": "nome_completo", "tipo": "texto", "pergunta": "Seu nome completo", "obrigatorio": true},
      {"id": "data_nasc", "tipo": "data", "pergunta": "Data de Nascimento", "obrigatorio": true},
      {"id": "telefone", "tipo": "numero", "pergunta": "Telefone (apenas números)", "obrigatorio": true},
      {"id": "endereco_livre", "tipo": "texto_longo", "pergunta": "Endereço Completo", "obrigatorio": true},
      {"id": "como_conheceu", "tipo": "opcoes", "pergunta": "Como nos conheceu?", "opcoes": ["Amigo", "Rede Social", "Evento", "Outro"], "obrigatorio": true},
      {"id": "termo_dados", "tipo": "checkbox", "pergunta": "Li e concordo com o uso dos meus dados para contato.", "obrigatorio": true}
    ]
  }
]
"""
# E acesse a URL com o parâmetro: http://localhost:8501/?id=cadastro_membro_temp

if __name__ == "__main__":
    exibir()