import socket
import os
import threading
import time

# configurare client
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
FOLDER_DESCARCARI = 'aplicatii_descarcate'

# creeaza folderul pentru descarcari daca nu exista
if not os.path.exists(FOLDER_DESCARCARI):
    os.makedirs(FOLDER_DESCARCARI)

# solicita serverului lista de aplicatii disponibile
def cere_lista_aplicatii():
    conexiune = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexiune.connect((SERVER_HOST, SERVER_PORT))
    conexiune.send('LISTA'.encode())
    aplicatii = conexiune.recv(1024).decode()
    print("Aplicatii disponibile:", aplicatii)
    conexiune.close()

# solicita descarcarea unei aplicatii
def descarca_aplicatie(nume_aplicatie):
    conexiune = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexiune.connect((SERVER_HOST, SERVER_PORT))
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
        print(f"Aplicatia {nume_aplicatie} nu exista pe server.")
    conexiune.close()

# exemplu simplu de utilizare
if __name__ == '_main_':
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
