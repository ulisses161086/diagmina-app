import os
import streamlit as st
import google.generativeai as genai

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
    "Código de Erro / Alarme (Opcional):", placeholder="Ex: Falha no Mine Compass"
)
descricao_falha = st.text_area(
    "Descrição da Falha / Sintoma:", placeholder="Ex: Não exibe mapa no PTX"
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
    with st.spinner("A consultar manuais e a processar o diagnóstico..."):
      try:
        # Configura a API com a chave
        genai.configure(api_key=api_key)

        # Usa o modelo suportado atual
        # Opção A: Usar o flash atualizado
model = genai.GenerativeModel('gemini-1.5-flash')

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

        response = model.generate_content(prompt)

        st.success("Diagnóstico Concluído:")
        st.markdown(response.text)

      except Exception as e:
        st.error(
            f"Erro ao consultar a API ou processar a requisição. Detalhes: {e}"
        )
