import socket
import threading
import os
import time

HOST = 'localhost'
PORT = 5000
FOLDER_APLICATII = 'aplicatii'

clienti_aplicatii = {}

def trimite_lista_aplicatii(conexiune):
    aplicatii = os.listdir(FOLDER_APLICATII)
    aplicatii_str = ','.join(aplicatii)
    conexiune.send(aplicatii_str.encode())

def trimite_aplicatie(conexiune, nume_aplicatie):
    cale_aplicatie = os.path.join(FOLDER_APLICATII, nume_aplicatie)
    if os.path.exists(cale_aplicatie):
        conexiune.send(b'EXISTA')
        with open(cale_aplicatie, 'rb') as fisier:
            date = fisier.read()
            conexiune.sendall(len(date).to_bytes(8, 'big'))
            conexiune.sendall(date)
    else:
        conexiune.send(b'NU_EXISTA')

def gestioneaza_client(conexiune, adresa):
    global clienti_aplicatii
    while True:
        try:
            mesaj = conexiune.recv(1024).decode()
            if mesaj == 'LISTA':
                trimite_lista_aplicatii(conexiune)
            elif mesaj.startswith('DESCARCA'):
                _, nume_aplicatie = mesaj.split()
                trimite_aplicatie(conexiune, nume_aplicatie)

                if adresa not in clienti_aplicatii:
                    clienti_aplicatii[adresa] = []
                clienti_aplicatii[adresa].append(nume_aplicatie)
        except:
            print(f'Clientul {adresa} s-a deconectat.')
            break
    conexiune.close()

def porneste_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Serverul este pornit și ascultă conexiuni...")

    while True:
        conexiune, adresa = server_socket.accept()
        print(f"Conexiune nouă de la {adresa}")
        thread = threading.Thread(target=gestioneaza_client, args=(conexiune, adresa))
        thread.start()

porneste_server()
