import streamlit as st
import google.generativeai as genai

# Configuração da página móvel
st.set_page_config(
    page_title="DiagMina AI",
    page_icon="🚜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo para celular
st.markdown("""
    <style>
    .stApp { background-color: #0b1329; color: #f8fafc; }
    .stTextInput input, .stTextArea textarea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #0f172a;
        font-weight: bold;
        font-size: 16px;
        border-radius: 12px;
        height: 3.2em;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚜 DiagMina AI")
st.caption("⚡ Assistente Técnico de Tecnologia de Mina")

# Chave API do Gemini
api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)

with st.form("diag_form"):
    st.subheader("🔍 Consulta de Falha em Campo")
    tag = st.text_input("TAG / Frota do Equipamento:", placeholder="Ex: CA-1029, PF-4502...").strip().upper()
    codigo_erro = st.text_input("Código de Erro / Alarme (Opcional):", placeholder="Ex: TRIGGER DA CÂMERA INVERTIDO...").strip().upper()
    sintoma = st.text_area("Descrição da Falha / Sintoma:", placeholder="Ex: Câmera traseira com imagem invertida...", height=100)
    submitted = st.form_submit_button("✨ Buscar Diagnóstico")

if submitted:
    if not sintoma and not codigo_erro:
        st.warning("⚠️ Preencha o código do erro ou a descrição da falha.")
    elif not api_key:
        st.error("❌ Chave GEMINI_API_KEY não configurada nos Secrets.")
    else:
        with st.spinner("🔎 Consultando base de dados de manutenção..."):
            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
                prompt = f"""
                Você é um especialista em manutenção de Tecnologia de Mina (Dispatch, Provision, Câmeras, GPS, Rajant).
                
                DADOS DA OCORRÊNCIA:
                - TAG: {tag if tag else 'Não informada'}
                - Código de Erro: {codigo_erro if codigo_erro else 'Não informado'}
                - Sintoma: {sintoma}
                
                INSTRUÇÕES:
                1. Indique a CAUSA RAIZ provável.
                2. Forneça o CHECKLIST PASSO A PASSO para teste em campo.
                3. Detalhe reconfigurações necessárias (display, conectores, parâmetros).
                """
                response = model.generate_content(prompt)
                st.success("✅ Diagnóstico Encontrado!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro ao consultar o modelo: {e}")
