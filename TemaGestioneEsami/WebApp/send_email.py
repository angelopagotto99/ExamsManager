import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .envc
load_dotenv()

def generate_random_number():
    random_number = random.randint(0, 999999)
    formatted_number = f"{random_number:06d}"
    return formatted_number

def send_email(subject, body, recipient_email):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.libero.it", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email inviata con successo!")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")

if __name__ == "__main__":
    recipient_email = "destinatario@example.com"  # Sostituisci con l'indirizzo email del destinatario
    subject = "Matricola per iscrizione"
    matricola = generate_random_number()
    body = f"La tua Matricola per iscriverti è: {matricola}"
    send_email(subject, body, recipient_email)
