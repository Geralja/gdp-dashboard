import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import re
import time
from PIL import Image
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="GeralJá IA", layout="wide", page_icon="🚀")

# 2. INICIALIZAÇÃO DO FIREBASE (Protegida)
if not firebase_admin._apps:
    try:
        # Tente carregar dos Secrets do Streamlit
        cred_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except:
        # Se falhar (rodando local), busca arquivo local
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

# 3. CLASSE IA MESTRE (Processamento de Imagens e Dados)
class IAMestre:
    @staticmethod
    def otimizar_imagem(file):
        """Reduz peso para caber no limite de 1MB do Firestore"""
        if file is None: return None
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((600, 600))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except: return None

    @staticmethod
    def limpar_tel(tel):
        return re.sub(r'\D', '', str(tel or ""))

# 4. VARIÁVEIS GLOBAIS
CATEGORIAS = ["Eletricista", "Encanador", "Limpeza", "Pintor", "Mecânico", "Outros"]

# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================
st.title("🚀 GeralJá - Versão Piloto IA")

menu_abas = st.tabs(["🔍 BUSCAR", "📢 MEU PERFIL", "⚙️ ADMIN"])

# ------------------------------------------------------------------------------
# ABA 1: BUSCA (Onde a mágica acontece)
# ------------------------------------------------------------------------------
with menu_abas[0]:
    busca = st.text_input("O que você procura hoje?", placeholder="Ex: encanador no centro...")
    
    # Aqui entrará a lógica de Geolocalização e Rank de Moedas
    st.info("Aguardando lógica de proximidade...")

# ------------------------------------------------------------------------------
# ABA 2: MEU PERFIL (Sua Vitrine com 4 Fotos)
# ------------------------------------------------------------------------------
with menu_abas[1]:
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        col_l1, col_l2 = st.columns([1,1])
        with col_l1:
            st.subheader("🔑 Acesso ao Parceiro")
            l_zap = st.text_input("WhatsApp", key="login_zap")
            l_pass = st.text_input("Senha", type="password")
            if st.button("ENTRAR"):
                # Lógica de login simples
                tel = IAMestre.limpar_tel(l_zap)
                doc = db.collection("profissionais").document(tel).get()
                if doc.exists and str(doc.to_dict().get('senha')) == l_pass:
                    st.session_state.auth = True
                    st.session_state.user_id = tel
                    st.rerun()
                else: st.error("Erro de acesso.")
        with col_l2:
            st.subheader("📝 Quero me Cadastrar")
            if st.button("Ir para Cadastro"): st.info("Link para formulário")

    else:
        # ÁREA DO PARCEIRO LOGADO
        uid = st.session_state.user_id
        dados = db.collection("profissionais").document(uid).get().to_dict()
        
        sub_tab1, sub_tab2 = st.tabs(["📊 Painel", "🛠️ Editar Vitrine"])
        
        with sub_tab2:
            with st.form("edit_form"):
                st.write("### Editar Minhas Fotos e Dados")
                f1, f2 = st.columns(2)
                up1 = f1.file_uploader("Foto 1", type=['jpg','png'], key="f1")
                up2 = f1.file_uploader("Foto 2", type=['jpg','png'], key="f2")
                up3 = f2.file_uploader("Foto 3", type=['jpg','png'], key="f3")
                up4 = f2.file_uploader("Foto 4", type=['jpg','png'], key="f4")
                
                desc = st.text_area("Descrição", value=dados.get('descricao', ''))
                
                if st.form_submit_button("SALVAR"):
                    # Processar e Salvar
                    st.success("Dados enviados para IA...")

# ------------------------------------------------------------------------------
# ABA 3: ADMIN
# ------------------------------------------------------------------------------
with menu_abas[2]:
    pass_adm = st.text_input("Chave Mestra", type="password")
    if pass_adm == "admin123":
        st.write("Painel de Controle Ativo")
