# Proiect Retele de Calculatoare - Actualizarea aplicatiilor la distanta

Cerinte: 

 - pe server exista o serie de aplicatii executabile, lista care nu se modifica pe durata rularii procesului server
 - clientii se conecteaza la server si solicita lista acestora
 - un client poate solicita descarcarea unei aplicatii
 - server-ul mentine o lista cu toate aplicatiile descarcate de un client
 - pe server se pot publica noi versiuni ale unei aplicatii prin suprascrierea celei existente; in acest caz, server-ul trimite tuturor clientilor care au descarcat aplicatia respectiva noua versiune
 - in cazul in care aplicatia ruleaza pe client, acesta salveaza versiunea primita si reincearca s-o suprascrie pe cea veche pana reuseste
