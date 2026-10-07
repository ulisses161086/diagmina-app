import streamlit as st
import requests

# Configuração da página para celular
st.set_page_config(
    page_title="DiagMina AI",
    page_icon="🚜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização visual
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

# Leitura da chave do Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

with st.form("diag_form"):
    st.subheader("🔍 Consulta de Falha em Campo")
    tag = st.text_input("TAG / Frota do Equipamento:", placeholder="Ex: CA-1043, CA-1029...").strip().upper()
    codigo_erro = st.text_input("Código de Erro / Alarme (Opcional):", placeholder="Ex: PTX TRAVADO...").strip().upper()
    sintoma = st.text_area("Descrição da Falha / Sintoma:", placeholder="Ex: Não é possível realizar ações no PTX...", height=100)
    submitted = st.form_submit_button("✨ Buscar Diagnóstico")

if submitted:
    if not sintoma and not codigo_erro:
        st.warning("⚠️ Preencha o código do erro ou a descrição da falha.")
    elif not api_key:
        st.error("❌ Chave GEMINI_API_KEY não configurada nos Secrets.")
    else:
        with st.spinner("🔎 Consultando base de dados de manutenção..."):
            try:
                # Lista de modelos por ordem de preferência
                modelos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
                
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key
                }
                
                prompt_text = f"""
                Você é um especialista em manutenção preventiva e corretiva de Tecnologia de Mina (sistemas Dispatch, Provision, PTX, Câmeras, GPS, Rajant).
                
                DADOS DA OCORRÊNCIA:
                - TAG / Equipamento: {tag if tag else 'Não informada'}
                - Código de Erro / Alarme: {codigo_erro if codigo_erro else 'Não informado'}
                - Sintoma / Falha Relatada: {sintoma}
                
                INSTRUÇÕES DE RESPOSTA (Direto e objetivo para o técnico em campo):
                1. **Causa Raiz Provável**: Para falha de PTX travado/congelado (ex: no CA-1043), explique as possíveis causas (ex: mau contato nos terminais olhal/borne de alimentação 24Vdc, cabo de alimentação ME4 solto, ou acúmulo de arquivos temporários do sistema).
                2. **Checklist / Passo a Passo em Campo**:
                   - Inspeção visual e reaperto dos conectores elétricos no painel/borne.
                   - Procedimento de reset físico/por chave geral do embarcado.
                   - Reinstalação / ressincronização completa da aplicação Dispatch/Provision.
                   - Limpeza de arquivos temporários do sistema operacional do PTX.
                """
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_text}]
                    }]
                }
                
                sucesso = False
                for modelo in modelos:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
                    response = requests.post(url, json=payload, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        resultado_texto = res_data['candidates'][0]['content']['parts'][0]['text']
                        st.success("✅ Diagnóstico Encontrado!")
                        st.markdown(resultado_texto)
                        sucesso = True
                        break
                
                if not sucesso:
                    res_data = response.json()
                    erro_msg = res_data.get('error', {}).get('message', 'Erro na requisição')
                    st.error(f"Erro na API ({response.status_code}): {erro_msg}")
                    
            except Exception as e:
                st.error(f"Erro ao consultar o modelo: {e}")
