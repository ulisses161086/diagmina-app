import streamlit as st
import requests
import json

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

# Leitura das chaves nos Secrets (suporta uma chave única ou lista separada por vírgulas)
raw_keys = st.secrets.get("GEMINI_API_KEY", "")
api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

with st.form("diag_form"):
    st.subheader("🔍 Consulta de Falha em Campo")
    tag = st.text_input("TAG / Frota do Equipamento:", placeholder="Ex: CA-1005...").strip().upper()
    codigo_erro = st.text_input("Código de Erro / Alarme (Opcional):", placeholder="Ex: Falha de comunicação entre rádio e PTX...").strip().upper()
    sintoma = st.text_area("Descrição da Falha / Sintoma:", placeholder="Ex: PTX off-line e rádio Rajant online...", height=100)
    submitted = st.form_submit_button("✨ Buscar Diagnóstico")

if submitted:
    if not sintoma and not codigo_erro:
        st.warning("⚠️ Preencha o código do erro ou a descrição da falha.")
    elif not api_keys:
        st.error("❌ Chave GEMINI_API_KEY não configurada nos Secrets do Streamlit.")
    else:
        with st.spinner("🔎 Consultando base técnica de manutenção..."):
            try:
                prompt_texto = f"""
                Você é o DiagMina AI, um assistente técnico especialista em manutenção preventiva e corretiva de frotas de mina (sistemas Dispatch, Provision, PTX, Câmeras, GPS, Rajant).
                
                DADOS DA OCORRÊNCIA EM CAMPO:
                - TAG / Equipamento: {tag if tag else 'Não informada'}
                - Código de Erro / Alarme: {codigo_erro if codigo_erro else 'Não informado'}
                - Sintoma / Falha Relatada: {sintoma}
                
                DIRETRIZES DE RESPOSTA (Seja direto, técnico e focado em campo):
                1. **Causa Raiz Provável**: Analise o problema considerando falhas comuns em campo (ex: perda de enlace de rádio Rajant, falha na porta Ethernet do PTX, queda de alimentação 24V).
                2. **Checklist e Ações Corretivas**: Forneça o passo a passo objetivo para o técnico executar no equipamento (ex: verificação de pings no rádio, reboot físico do PTX, checagem de cabos UTP/conectores RJ45).
                """
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_texto}]
                    }]
                }
                headers = {'Content-Type': 'application/json'}
                
                resposta_sucesso = None
                ultimo_erro = ""
                
                # Tenta enviar a requisição alternando entre as chaves disponíveis
                for current_key in api_keys:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={current_key}"
                    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=25)
                    
                    if response.status_code == 200:
                        data = response.json()
                        texto = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if texto:
                            resposta_sucesso = texto
                            break
                    else:
                        ultimo_erro = f"Status {response.status_code}: {response.text}"
                
                if resposta_sucesso:
                    st.success("✅ Diagnóstico Encontrado!")
                    st.markdown(resposta_sucesso)
                else:
                    st.error(f"Erro ao consultar o modelo gratuito. Detalhes: {ultimo_erro}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
