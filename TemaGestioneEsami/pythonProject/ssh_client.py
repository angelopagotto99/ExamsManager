import paramiko
import logging
import time

# Configura il logging per il debug
logging.basicConfig(level=logging.DEBUG)


class SSHClient:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.channel = None

    def connect(self):
        try:
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password
            )
            logging.debug("Connected to server")
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return False
        return True

    def open_shell(self):
        try:
            self.channel = self.client.invoke_shell()
            logging.debug("Shell opened")
        except Exception as e:
            logging.error(f"Failed to open shell: {e}")
            return False
        return True

    def send_command(self, command):
        try:
            self.channel.send(command + '\n')
            logging.debug(f"Sent command: {command}")
        except Exception as e:
            logging.error(f"Error sending command: {e}")

    def receive_output(self):
        output = ''
        try:
            while self.channel.recv_ready():
                output += self.channel.recv(1024).decode('utf-8')
            logging.debug(f"Received output: {output}")
        except Exception as e:
            logging.error(f"Error receiving output: {e}")
        return output

    def close(self):
        if self.channel:
            self.channel.close()
        self.client.close()
        logging.debug("Connection closed")


# Esempio di utilizzo della classe SSHClient
if __name__ == "__main__":
    client = SSHClient(hostname='127.0.0.1', port=2200, username='test', password='password')

    if client.connect():
        if client.open_shell():
            try:
                while True:
                    command = input("Enter command: ")
                    if command.lower() == 'exit':
                        client.send_command('exit')
                        time.sleep(1)
                        print(client.receive_output())
                        break
                    client.send_command(command)
                    time.sleep(1)
                    output = client.receive_output()
                    print(output, end='')
            except KeyboardInterrupt:
                print("\nExiting...")

        client.close()
