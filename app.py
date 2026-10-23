import os
from google import genai
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="DiagMina AI - Consulta de Falha em Campo",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Consulta de Falha em Campo")
st.markdown(
    "Insira os dados do equipamento para obter o diagnóstico baseado nos"
    " manuais."
)

# Campos de entrada
tag_equipamento = st.text_input(
    "TAG / Frota do Equipamento:", placeholder="Ex: CA-1006"
)
codigo_erro = st.text_input(
    "Código de Erro / Alarme (Opcional):", placeholder="Ex: PTX travado"
)
descricao_falha = st.text_area(
    "Descrição da Falha / Sintoma:",
    placeholder="Ex: Não consegue realizar ações no PTX",
)

# Chave da API
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if st.button("✨ Buscar Diagnóstico"):
  if not tag_equipamento or not descricao_falha:
    st.warning(
      "Por favor, preencha pelo menos a TAG do equipamento e a descrição da"
      " falha."
    )
  elif not api_key:
    st.error(
      "Chave da API do Google não encontrada. Configure o secret 'GEMINI_API_KEY'."
    )
  else:
    with st.spinner(
        "A consultar manuais da frota e a processar o diagnóstico..."
    ):
      try:
        # Inicializa o cliente oficial moderno
        client = genai.Client(api_key=api_key)

        # Prompt estruturado para forçar respostas estritamente técnicas baseadas em manuais de mina
        prompt = f"""
Você é o DiagMina AI, um assistente técnico especialista em manutenção de tecnologia de mineração (Frotas e Automação).
Com base nos manuais técnicos oficiais de equipamentos de mina, analise a ocorrência abaixo:

- TAG / Equipamento: {tag_equipamento}
- Código de Erro / Alarme: {codigo_erro if codigo_erro else 'Não informado'}
- Sintoma / Descrição: {descricao_falha}

Forneça um diagnóstico rápido, direto e estruturado contendo:
1. Possíveis Causas Raiz (focadas em hardware, rede rádio/PTX ou SW embarcado).
2. Procedimento Passo a Passo para Resolução em Campo.
3. Validação pós-reparo.
"""

        # Utiliza o gemini-1.5-flash por ser extremamente rápido e estável para evitar erros 503
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )

        st.success("Diagnóstico Concluído:")
        st.markdown(response.text)

      except Exception as e:
        st.error(
            f"Erro ao consultar a API. O serviço pode estar temporariamente"
            f" instável. Detalhes: {e}"
        )
