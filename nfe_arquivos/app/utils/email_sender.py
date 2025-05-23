import smtplib
from email.message import EmailMessage

def enviar_email(assunto, destinatario, corpo):
    msg = EmailMessage()
    msg.set_content(corpo)
    msg['Subject'] = assunto
    msg['From'] = 'seu@email.com'
    msg['To'] = destinatario

    try:
        with smtplib.SMTP('smtp.seudominio.com', 587) as smtp:
            smtp.starttls()
            smtp.login('seu@email.com', 'SUA_SENHA')
            smtp.send_message(msg)
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')
