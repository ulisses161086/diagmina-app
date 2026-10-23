import os
from google import genai
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="DiagMina AI - Consulta de Falha em Campo",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 DiagMina AI - Consulta de Falha em Campo")
st.markdown(
    "Carregue os manuais ou relatórios técnicos em PDF (pode selecionar"
    " múltiplos) para obter o diagnóstico exato."
)

# Upload de múltiplos ficheiros PDF em simultâneo
uploaded_files = st.file_uploader(
    "📄 Carregar Manuais ou Relatórios Técnicos (PDFs):",
    type=["pdf"],
    accept_multiple_files=True,
)

# Campos de entrada
tag_equipamento = st.text_input(
    "TAG / Frota do Equipamento:", placeholder="Ex: CA-1026"
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

if st.button("✨ Buscar Diagnóstico nos Documentos"):
  if not tag_equipamento or not descricao_falha:
    st.warning(
      "Por favor, preencha pelo menos a TAG do equipamento e a descrição da"
      " falha."
    )
  elif not uploaded_files:
    st.warning(
      "Por favor, carregue pelo menos um manual ou relatório em PDF para a"
      " análise."
    )
  elif not api_key:
    st.error(
      "Chave da API do Google não encontrada. Configure o secret 'GEMINI_API_KEY'."
    )
  else:
    spinner_text = (
        f"A processar {len(uploaded_files)} ficheiro(s) e a cruzar dados"
        " técnicos..."
    )
    with st.spinner(spinner_text):
      uploaded_refs = []
      client = genai.Client(api_key=api_key)

      try:
        # Faz o upload de cada ficheiro PDF selecionado
        for uploaded_file in uploaded_files:
          file_ref = client.files.upload(file=uploaded_file)
          uploaded_refs.append(file_ref)

        # Monta a lista de conteúdos para o modelo (todos os PDFs + o prompt)
        contents_payload = list(uploaded_refs)

        prompt = f"""
Você é o DiagMina AI, um assistente técnico especialista em manutenção de tecnologia de mineração.
Analise rigorosamente os documentos PDF fornecidos (manuais e/ou relatórios técnicos) para resolver a ocorrência abaixo:

- TAG / Equipamento: {tag_equipamento}
- Código de Erro / Alarme: {codigo_erro if codigo_erro else 'Não informado'}
- Sintoma / Descrição: {descricao_falha}

INSTRUÇÃO CRÍTICA:
- Baseie a sua resposta **estritamente** nas informações, códigos e procedimentos descritos nos documentos PDF anexados.
- Se houver divergências ou referências cruzadas entre os manuais e os relatórios, priorize a solução técnica descrita.

Forneça um diagnóstico estruturado e direto:
1. Causas Raiz Identificadas nos Documentos.
2. Procedimento de Correção Passo a Passo em Campo.
3. Validação e Testes Pós-Intervenção.
"""
        contents_payload.append(prompt)

        # Envia os documentos e o prompt para o modelo processar em conjunto
        response = client.models.generate_content(
            model="gemini-3.8-flash", contents=contents_payload
        )

        st.success("Diagnóstico Concluído com Base nos Documentos Carregados:")
        st.markdown(response.text)

      except Exception as e:
        st.error(
            f"Erro ao processar os ficheiros ou consultar a API. Detalhes: {e}"
        )
