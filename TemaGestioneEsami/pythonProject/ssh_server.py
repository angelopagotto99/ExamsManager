import socket
import paramiko
import threading
import traceback
import logging
import os
import subprocess

# Configura il logging per il debug
logging.basicConfig(level=logging.DEBUG)

# Carica la chiave privata generata
host_key = paramiko.ECDSAKey(filename='server_key')


# Implementazione della classe Server che gestisce le richieste del server SSH
class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()  # Crea un evento di threading

    def check_channel_request(self, kind, chanid):
        # Log del tipo di richiesta del canale
        logging.debug(f"Channel request: {kind}, id: {chanid}")
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED  # Accetta richieste di tipo 'session'
        return paramiko.OPEN_FAILED_ADMINISTRATIVAMENTE_PROHIBITED  # Rifiuta altri tipi di richieste

    def check_auth_password(self, username, password):
        # Log del tentativo di autenticazione
        logging.debug(f"Auth attempt: username={username}, password={password}")
        if (username == 'test') and (password == 'password'):
            return paramiko.AUTH_SUCCESSFUL  # Autenticazione riuscita se username e password sono corretti
        return paramiko.AUTH_FAILED  # Autenticazione fallita

    def get_allowed_auths(self, username):
        # Specifica i metodi di autenticazione permessi
        return 'password'

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        # Log della richiesta di PTY
        logging.debug("PTY request")
        return True  # Accetta la richiesta di PTY

    def check_channel_shell_request(self, channel):
        # Log della richiesta di shell
        logging.debug("Shell request")
        self.event.set()  # Imposta l'evento per indicare che la shell è stata richiesta
        return True  # Accetta la richiesta di shell


# Funzione per gestire le connessioni dei client
def handle_connection(client):
    # Log della gestione di una nuova connessione
    logging.debug("Handling new connection")
    transport = paramiko.Transport(client)  # Crea un oggetto Transport per gestire la connessione
    transport.add_server_key(host_key)  # Aggiunge la chiave del server al transport
    server = Server()  # Crea un'istanza della classe Server

    try:
        transport.start_server(server=server)  # Avvia il server SSH
        chan = transport.accept(60)  # Attende la creazione del canale per 60 secondi
        if chan is None:
            logging.debug("No channel.")  # Log nel caso in cui il canale non sia stato creato
            return

        logging.debug("Channel accepted")  # Log nel caso in cui il canale sia stato accettato
        server.event.wait(10)  # Attende che la shell sia richiesta per un massimo di 10 secondi
        if not server.event.is_set():
            logging.debug("No shell request.")  # Log nel caso in cui la richiesta di shell non sia stata ricevuta
            return

        chan.send("Welcome to the SSH server!\n")  # Invia un messaggio di benvenuto al client

        while True:
            data = chan.recv(1024).decode('utf-8').strip()
            if not data:
                break

            # Controlla se il comando è nano o vim e avvia tmux
            if data.startswith('nano') or data.startswith('vim'):
                session_name = "editor_session"
                command = f"tmux new-session -d -s {session_name} '{data}'"
                subprocess.run(command, shell=True)
                chan.send(f"Opened {data} in a new tmux session. Use 'tmux attach -t {session_name}' to interact.\n")
            else:
                # Esegui altri comandi direttamente
                output = subprocess.run(data, shell=True, capture_output=True, text=True)
                if output.stdout:
                    chan.send(output.stdout)
                if output.stderr:
                    chan.send(output.stderr)

    except Exception as e:
        # Log in caso di eccezione durante l'avvio del server o la gestione del canale
        logging.error(f'Error: {e}')
        traceback.print_exc()
    finally:
        transport.close()  # Chiude il transport
        client.close()  # Chiude la connessione del client


# Funzione per avviare il server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP/IP
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Riutilizza l'indirizzo
    server_socket.bind(('0.0.0.0', 2200))  # Assegna il socket all'indirizzo IP e alla porta specificati
    server_socket.listen(100)  # Inizia ad ascoltare le connessioni

    # Log per indicare che il server è in ascolto
    logging.debug("Listening for connection ...")

    while True:
        client, addr = server_socket.accept()  # Accetta nuove connessioni
        # Log per indicare che è stata ricevuta una connessione
        logging.debug(f"Got a connection from {addr}")
        # Gestisce la connessione in un nuovo thread
        threading.Thread(target=handle_connection, args=(client,)).start()


if __name__ == "__main__":
    start_server()  # Avvia il server
