import paramiko

# Genera una chiave ECDSA
key = paramiko.ECDSAKey.generate(bits=256)
# Salva la chiave privata in un file
key.write_private_key_file('server_key')

# Salva la chiave pubblica in un file
with open('server_key.pub', 'w') as f:
    f.write(f'{key.get_name()} {key.get_base64()}')
