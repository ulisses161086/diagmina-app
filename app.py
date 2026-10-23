import os
import streamlit as st
from google import genai
from google.genai import types

# Configuração da página do Streamlit
st.set_page_config(
    page_title="DiagMina AI - Consulta de Falha em Campo",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Consulta de Falha em Campo")
st.markdown(
    "Insira os dados do equipamento para obter o diagnóstico baseado nos manuais."
)

# Campos de entrada
tag_equipamento = st.text_input(
    "TAG / Frota do Equipamento:", placeholder="Ex: CA-1006"
)
codigo_erro = st.text_input(
    "Código de Erro / Alarme (Opcional):", placeholder="Ex: Falha no Mine Compass"
)
descricao_falha = st.text_area(
    "Descrição da Falha / Sintoma:", placeholder="Ex: Não exibe mapa no PTX"
)

# Chave da API (certifique-se de configurar nos Secrets do Streamlit)
# No Streamlit Cloud, adicione GEMINI_API_KEY em st.secrets
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
    with st.spinner("A consultar manuais e a processar o diagnóstico..."):
      try:
        # Inicializa o cliente oficial do Google GenAI
        client = genai.Client(api_key=api_key)

        # Monta o prompt com os dados de campo
        prompt = f"""
                Atue como um especialista em manutenção de tecnologia de mineração.
                Analise a seguinte ocorrência:
                - TAG / Equipamento: {tag_equipamento}
                - Código de Erro: {codigo_erro if codigo_erro else 'Não informado'}
                - Sintoma / Descrição: {descricao_falha}
                
                Forneça um diagnóstico técnico estruturado com:
                1. Possíveis causas raiz.
                2. Procedimento passo a passo para resolução em campo.
                3. Precauções de segurança necessárias.
                """

        # Utiliza um modelo atual suportado (ex: gemini-2.0-flash ou geminti-1.5-pro)
        # Configuramos também uma configuração de segurança ou parâmetros se necessário
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,  # Respostas mais objetivas e técnicas
            ),
        )

        st.success("Diagnóstico Concluído:")
        st.markdown(response.text)

      except Exception as e:
        st.error(
            f"Erro ao consultar a API ou processar a requisição. Detalhes: {e}"
        )
