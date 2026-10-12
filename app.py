import streamlit as st
import google.generativeai as genai

# Configuração da página para celular
st.set_page_config(
    page_title="DiagMina AI",
    page_icon="🚜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização profissional para o campo
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
st.caption("⚡ Assistente Técnico de Manutenção - Tecnologia de Mina")

# Leitura da chave de API armazenada nos Secrets do Streamlit
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

with st.form("diag_form"):
    st.subheader("🔍 Consulta de Falha em Campo")
    tag = st.text_input("TAG / Frota do Equipamento:", placeholder="Ex: CA-1043, CA-1029...").strip().upper()
    codigo_erro = st.text_input("Código de Erro / Alarme (Opcional):", placeholder="Ex: PTX travado...").strip().upper()
    sintoma = st.text_area("Descrição da Falha / Sintoma:", placeholder="Ex: Câmera traseira com imagem invertida...", height=100)
    submitted = st.form_submit_button("✨ Buscar Diagnóstico")

if submitted:
    if not sintoma and not codigo_erro:
        st.warning("⚠️ Preencha o código do erro ou a descrição da falha.")
    elif not api_key:
        st.error("❌ Chave GEMINI_API_KEY não configurada nos Secrets do Streamlit.")
    else:
        with st.spinner("🔎 Consultando base técnica de manutenção..."):
            try:
                genai.configure(api_key=api_key)
                
                prompt = f"""
                Você é o DiagMina AI, um assistente técnico especialista em manutenção preventiva e corretiva de frotas de mina (sistemas Dispatch, Provision, PTX, Câmeras, GPS, Rajant).
                
                DADOS DA OCORRÊNCIA EM CAMPO:
                - TAG / Equipamento: {tag if tag else 'Não informada'}
                - Código de Erro / Alarme: {codigo_erro if codigo_erro else 'Não informado'}
                - Sintoma / Falha Relatada: {sintoma}
                
                DIRETRIZES DE RESPOSTA (Seja direto, técnico e focado em campo):
                1. **Causa Raiz Provável**: Analise o problema considerando falhas comuns em campo (ex: mau contato em bornes/conectores de alimentação 24V, travamento de aplicação embarcada, inversão de sinal de trigger/vídeo).
                2. **Checklist e Ações Corretivas**: Forneça o passo a passo objetivo para o técnico executar no equipamento (ex: inspeção de chicotes, procedimento de reboot/reset físico, ressincronização com o Dispatch).
                """
                
                # Utiliza o modelo gemini-1.5-flash, amplamente estável para produção
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.success("✅ Diagnóstico Encontrado!")
                    st.markdown(response.text)
                else:
                    st.error("A IA não gerou uma resposta válida.")
                    
            except Exception as e:
                st.error(f"Erro ao consultar a API: {e}")
