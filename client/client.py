import socket
import os
import threading
import time

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
FOLDER_DESCARCARI = 'aplicatii_descarcate'
PORT_ACTUALIZARI = 5001

if not os.path.exists(FOLDER_DESCARCARI):
    os.makedirs(FOLDER_DESCARCARI)

def cere_lista_aplicatii():
    conexiune = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexiune.connect((SERVER_HOST, SERVER_PORT))
    
    conexiune.send(f'PORT {PORT_ACTUALIZARI}'.encode()) 
    time.sleep(0.1)  
    conexiune.send('LISTA'.encode())
    
    aplicatii = conexiune.recv(1024).decode()
    print("Aplicatii disponibile:", aplicatii)
    conexiune.close()

def descarca_aplicatie(nume_aplicatie):
    conexiune = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexiune.connect((SERVER_HOST, SERVER_PORT))

    conexiune.send(f'PORT {PORT_ACTUALIZARI}'.encode())
    time.sleep(0.1)
    conexiune.send(f'DESCARCA {nume_aplicatie}'.encode())

    raspuns = conexiune.recv(1024)
    if raspuns == b'EXISTA':
        lungime_date = int.from_bytes(conexiune.recv(8), 'big')
        date_aplicatie = b''
        while len(date_aplicatie) < lungime_date:
            date_aplicatie += conexiune.recv(1024)

        cale = os.path.join(FOLDER_DESCARCARI, nume_aplicatie)
        with open(cale, 'wb') as fisier:
            fisier.write(date_aplicatie)
        print(f"Aplicatia {nume_aplicatie} a fost descarcata cu succes!")
    else:
        print(f"Aplicatia {nume_aplicatie} nu exista pe server!")
    conexiune.close()

def asculta_actualizari():
    conexiune = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexiune.bind(('localhost', PORT_ACTUALIZARI))
    conexiune.listen()

    while True:
        client_conn, _ = conexiune.accept()
        mesaj = client_conn.recv(1024).decode()

        if mesaj.startswith('ACTUALIZARE'):
            _, nume_aplicatie = mesaj.split()

            lungime_date = int.from_bytes(client_conn.recv(8), 'big')
            date_aplicatie = b''
            while len(date_aplicatie) < lungime_date:
                date_aplicatie += client_conn.recv(1024)

            cale_aplicatie = os.path.join(FOLDER_DESCARCARI, nume_aplicatie)
            cale_temporara = cale_aplicatie + '.nou'

            with open(cale_temporara, 'wb') as fisier:
                fisier.write(date_aplicatie)

            while True:
                try:
                    os.replace(cale_temporara, cale_aplicatie)
                    print(f"Actualizare {nume_aplicatie} instalata cu succes!")
                    break
                except:
                    print(f"OOPS! Actualizarea {nume_aplicatie} nu poate fi instalată acum, reincearca in 5 secunde...")
                    time.sleep(5)

if __name__ == '_main_':
    threading.Thread(target=asculta_actualizari, daemon=True).start()

    while True:
        print("\nHello! Ce vrei sa faci?")
        print("1 - Vezi lista aplicatii disponibile")
        print("2 - Descarca aplicatie")
        print("3 - Iesire")

        optiune = input("Introdu optiunea: ")
        if optiune == '1':
            cere_lista_aplicatii()
        elif optiune == '2':
            nume_aplicatie = input("Introdu numele aplicatiei: ")
            descarca_aplicatie(nume_aplicatie)
        elif optiune == '3':
            break
        else:
            print("Optiune invalida.")
