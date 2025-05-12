import socket
import threading
import os
import time
import json

HOST = 'localhost'
PORT = 5000
FOLDER_APLICATII = 'aplicatii'
FISIER_CLIENTI = 'clienti_aplicatii.json'

clienti_aplicatii = {}

def incarca_clienti():
    global clienti_aplicatii
    if os.path.exists(FISIER_CLIENTI):
        with open(FISIER_CLIENTI, 'r') as f:
            clienti_aplicatii = json.load(f)

def salveaza_clienti():
    with open(FISIER_CLIENTI, 'w') as f:
        json.dump(clienti_aplicatii, f, indent=2)

def trimite_lista_aplicatii(conexiune):
    aplicatii = os.listdir(FOLDER_APLICATII)
    conexiune.send(','.join(aplicatii).encode())

def trimite_aplicatie(conexiune, nume_aplicatie):
    cale = os.path.join(FOLDER_APLICATII, nume_aplicatie)
    if os.path.exists(cale):
        conexiune.send(b'EXISTA')
        with open(cale, 'rb') as f:
            date = f.read()
            conexiune.sendall(len(date).to_bytes(8, 'big'))
            conexiune.sendall(date)
    else:
        conexiune.send(b'NU_EXISTA')

def trimite_lista_aplicatii(conexiune):
    aplicatii = os.listdir(FOLDER_APLICATII)
    conexiune.send(','.join(aplicatii).encode())

def trimite_aplicatie(conexiune, nume_aplicatie):
    cale = os.path.join(FOLDER_APLICATII, nume_aplicatie)
    if os.path.exists(cale):
        conexiune.send(b'EXISTA')
        with open(cale, 'rb') as f:
            date = f.read()
            conexiune.sendall(len(date).to_bytes(8, 'big'))
            conexiune.sendall(date)
    else:
        conexiune.send(b'NU_EXISTA')

def gestioneaza_client(conexiune, adresa):
    global clienti_aplicatii

    try:
        mesaj = conexiune.recv(1024).decode()
        if not mesaj.startswith('ID'):
            conexiune.send(b'Mesaj invalid. Lipseste ID.')
            return

        parti = mesaj.split()
        id_client = parti[1]
        port_actualizare = int(parti[3])
        comanda = parti[4]

        if id_client not in clienti_aplicatii:
            clienti_aplicatii[id_client] = {
                'ip': adresa[0],
                'port': port_actualizare,
                'aplicatii': []
            }

        if comanda == 'LISTA':
            trimite_lista_aplicatii(conexiune)

        elif comanda == 'DESCARCA':
            if len(parti) >= 6:
                nume_aplicatie = parti[5]
                trimite_aplicatie(conexiune, nume_aplicatie)

                if nume_aplicatie not in clienti_aplicatii[id_client]["aplicatii"]:
                    clienti_aplicatii[id_client]["aplicatii"].append(nume_aplicatie)
                    salveaza_clienti()
            else:
                conexiune.send(b'Comanda DESCARCA fara nume aplicatie!')
        else:
            conexiune.send(b'Comanda necunoscuta')
    except Exception as e:
        print(f"Eroare client {adresa}: {e}")
    finally:
                conexiune.close()


def trimite_actualizare(ip, port, nume_aplicatie):
    cale = os.path.join(FOLDER_APLICATII, nume_aplicatie)
    if not os.path.exists(cale): return

    with open(cale, 'rb') as f:
        date = f.read()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(f'ACTUALIZARE {nume_aplicatie}'.encode())
        s.sendall(len(date).to_bytes(8, 'big'))
        s.sendall(date)
        s.close()
        print(f"> Actualizare trimisa pentru {nume_aplicatie} -> {ip}:{port}")
    except:
        print(f"! Eroare trimitere actualizare la {ip}:{port}")

def monitorizeaza_modificari():
    ultima_modif = {}
    while True:
        for aplicatie in os.listdir(FOLDER_APLICATII):
            cale = os.path.join(FOLDER_APLICATII, aplicatie)
            if not os.path.isfile(cale): continue

            modif = os.path.getmtime(cale)
            if aplicatie not in ultima_modif:
                ultima_modif[aplicatie] = modif
            elif ultima_modif[aplicatie] != modif:
                ultima_modif[aplicatie] = modif
                print(f"\n# Detectata modificare la {aplicatie}. Trimit actualizari...")

                for id_client, info in clienti_aplicatii.items():
                    if aplicatie in info["aplicatii"]:
                        threading.Thread(target=trimite_actualizare,
                                         args=(info["ip"], info["port"], aplicatie)).start()
        time.sleep(5)

def porneste_server():
    incarca_clienti()
    threading.Thread(target=monitorizeaza_modificari, daemon=True).start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server ascultă pe {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"> Conexiune de la {addr}")
        threading.Thread(target=gestioneaza_client, args=(conn, addr)).start()

if __name__ == '__main__':
    porneste_server()
