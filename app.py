import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

st.set_page_config(page_title="Disparador de E-mail Simples", page_icon="📧")

st.title("📧 Disparador de E-mail em Massa")
st.markdown("Suba sua planilha, configure o template e envie.")

st.sidebar.header("⚙️ Configuração do SMTP")
smtp_server = st.sidebar.text_input("Servidor SMTP", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("Porta", value=587)
email_remetente = st.sidebar.text_input("Seu E-mail")
senha_app = st.sidebar.text_input("Senha de App", type="password", help="Para Gmail, use uma 'Senha de App'. Não use sua senha normal.")

st.subheader("1. Base de Dados (CSV)")
uploaded_file = st.file_uploader("Suba o arquivo CSV (deve ter uma coluna 'Email')", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())
    colunas = df.columns.tolist()
    st.info(f"Colunas detectadas para usar no template: {', '.join([f'{{{c}}}' for c in colunas])}")

    # 2. Configuração do E-mail
    st.subheader("2. Template do E-mail")
    assunto = st.text_input("Assunto do E-mail")
    
    tipo_email = st.radio("Formato", ["Texto Puro", "HTML"])
    
    template = st.text_area(
        "Corpo do E-mail", 
        height=300, 
        placeholder="Olá {Nome},\n\nSeguem os detalhes do seu pedido {Pedido}..."
    )

    # 3. Disparo
    if st.button("🚀 Enviar E-mails"):
        if not email_remetente or not senha_app or not template or not 'Email' in df.columns:
            st.error("Preencha as configurações de SMTP e certifique-se que o CSV tem uma coluna chamada 'Email'.")
        else:
            bar = st.progress(0)
            sucesso = 0
            falhas = 0
            
            # Conectar ao servidor (uma vez para todo o lote)
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(email_remetente, senha_app)
                
                st_console = st.empty() # Área para logs

                for index, row in df.iterrows():
                    try:
                        # Substituição das variáveis
                        corpo_final = template.format(**row.to_dict())
                        destinatario = row['Email']

                        # Montar E-mail
                        msg = MIMEMultipart()
                        msg['From'] = email_remetente
                        msg['To'] = destinatario
                        msg['Subject'] = assunto

                        if tipo_email == "HTML":
                            msg.attach(MIMEText(corpo_final, 'html'))
                        else:
                            msg.attach(MIMEText(corpo_final, 'plain'))

                        # Enviar
                        server.send_message(msg)
                        sucesso += 1
                        st_console.write(f"✅ Enviado para: {destinatario}")
                        
                    except Exception as e:
                        falhas += 1
                        st_console.write(f"❌ Erro ao enviar para {row.get('Email', 'Desconhecido')}: {e}")
                    
                    # Atualizar barra de progresso
                    bar.progress((index + 1) / len(df))
                    time.sleep(1) # Pausa para evitar bloqueio por spam
                
                server.quit()
                st.success(f"Processo finalizado! Enviados: {sucesso} | Falhas: {falhas}")

            except Exception as e:
                st.error(f"Erro na conexão com o servidor de e-mail: {e}")