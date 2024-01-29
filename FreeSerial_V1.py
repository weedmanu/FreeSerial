# Import des librairies nécessaires 
import threading                        # pour utiliser les thread
import PySimpleGUI as sg                # pour faire une interface graphique (pip install pysimplegui)
import serial                           # pour utiliser la com série         (pip install pyserial)
import serial.tools.list_ports          # pour lister les port utilisés      (pip install serial-tool)

mon_icon = "~/Desktop/FreeSerial/img/th.ico"
FONT16B=('Helvetica', 16, 'bold')

# On créer une liste des ports série disponibles
ports = serial.tools.list_ports.comports()
port_names = [port.device for port in ports]

# On créer une liste des vitesses possibles
speeds = [9600, 19200, 38400, 57600, 115200]

# On créer une liste des commandes AT pour le Bluetooth
command_BT = [
    "AT", 
    "AT+VERSION?", 
    "AT+RESET", 
    "AT+ORGL", 
    "AT+NAME=BT_HC-05", 
    "AT+PSWD=0000", "AT+PSWD?", 
    "AT+ROLE?",
    "AT+ROLE=0",
    "AT+ROLE=1",
    "AT+ROLE=2",
    "AT+UART=9600,0,0"
]
# On créer une liste des commandes AT pour le LoraE5  
command_LoraE5 = [
    "AT", 
    "AT+VER", 
    "AT+ID", 
    "AT+TEMP", 
    "AT+VDD", 
    "AT+RTC", 
    "AT+RTC=FULL", 
    "AT+CH=NUM", 
    "AT+WDT", 
    "AT+MODE=TEST" , 
    "AT+TEST=?", 
    "AT+TEST=STOP"
]
# On créer une liste des infos des commandes AT pour le Bluetooth
infos_command_BT = [
    "Statut, utiliser pour tester si la connexion du module est OK.",  
    "Version du firmware", 
    "Reboot du module", 
    "Remet tous les paramètres d'usine", 
    "Renomme le module en BT_HC-05", 
    "Change le mot de passe en 0000",
    "Voir le mot de passe",
    "Mode 0 esclave, 1 maître, 2 esclave avec retour",
    "passe en mode 0 : esclave",
    "Passe en mode 1 : maître",
    "Passe en mode 2 : esclave avec retour",
    "Change la vitesse de communication",
]
# On créer une liste des infos des commandes AT pour le LoraE5
infos_command_LoraE5 = [
    "Statut, utiliser pour tester si la connexion du module est OK.", 
    "Version du firmware", 
    "Retourne le : DevAddr, DevEui et AppEui", 
    "Température du module(peu précis)", 
    "Tension d'alimentation", 
    "Temps depuis le démarrage, commence à 2000-01-01 00:00:00",
    "Temps complet, timezone, timestamp, ms depuis la mise sous tension",
    "Liste les canaux utilisés",
    "WatchDog actif ou pas",
    "Passe en mode test",
    "Vérifie si on est on mode test et affiche la config du module sinon : erreur -12", 
    "Sort du mode test",
]

command_device = command_LoraE5         # par défaut la liste des commandes est celle du LoraE5
infos_list = infos_command_LoraE5       # par défaut la liste des infos des commandes est celle du LoraE5

# on défini la disposition du menu
menu_layout = [
    ["Port COM", ["Recherche"]],
    ["Commande AT", ["Afficher Commande AT", "Masquer Commande AT"]],
    ["Terminal 2", ["Afficher Terminal 2", "Masquer Terminal 2"]]
]

layout = [                    # On créer une disposition sur trois colonnes 
    [sg.Menu(menu_layout, key="-MENU-")],
    [   
        sg.pin(sg.Column(            # La colonne avec les commandes prédéfinies
            [
                [sg.Push(), sg.Text("commande AT", font=FONT16B, pad=(10,5)), sg.Push()],
                [sg.Checkbox('BT HC05', default=False,key='-BT-', enable_events=True, pad=(10,5)),
                 sg.Checkbox('LoraE5', default=True,key='-LORA-', enable_events=True, pad=(10,5))],
                [sg.Listbox(values=command_LoraE5, size=(35,17), key="-COMMAND-", enable_events=True, pad=(10,5))],
                [sg.Multiline(key="-OUTPUT-", size=(35, 3), disabled=True, pad=(10,5))],                
            ], key='-COL1-', visible=False
        )),
        sg.pin(sg.Column(           # La colonne avec le premier terminal série
            [
                [sg.Push(), sg.Text("Terminal 1", font=FONT16B, pad=(10,5)), sg.Push()],
                [sg.Combo(port_names, key="-PORT1-", size=(10,1),  pad=(10,5)), sg.Combo(speeds, key="-SPEED1-", size=(10,1), pad=(10,5)),
                 sg.Button("Connecter", key="-CONNECT1-", size=(10,1), pad=(10,5)), sg.Button("Déconnecter", key="-DISCONNECT1-", disabled=True, size=(10,1), pad=(10,5)),
                 sg.Button("Effacer", key="-ERASE1-", size=(10,1), pad=(10,5)),],
                [sg.Multiline(key="-OUTPUT1-", disabled=True, size=(73, 20), pad=(10,5))],
                [sg.Input(key="-INPUT1-", size=(60, 1), pad=(10,5)), sg.Button("Envoyer", key="-SEND1-", size=(10,1),  pad=(10,5))],
            ], key='-COL2-', visible=True
        )),
        sg.pin(sg.Column(          # La colonne avec le deuxième terminal série
            [
                [sg.Push(), sg.Text("Terminal 2", font=FONT16B, pad=(10,5)), sg.Push()],
                [sg.Combo(port_names, key="-PORT2-", size=(10,1),  pad=(10,5)), sg.Combo(speeds, key="-SPEED2-", size=(10,1),  pad=(10,5)),
                 sg.Button("Connecter", key="-CONNECT2-", size=(10,1),  pad=(10,5)), sg.Button("Déconnecter", key="-DISCONNECT2-", disabled=True, size=(10,1),  pad=(10,5)),
                 sg.Button("Effacer", key="-ERASE2-", size=(10,1),  pad=(10,5))],
                [sg.Multiline(key="-OUTPUT2-", disabled=True, size=(73, 20), pad=(10,5))],
                [sg.Input(key="-INPUT2-", size=(60, 1), pad=(10,5)), sg.Button("Envoyer", key="-SEND2-", size=(10,1),  pad=(10,5))],
            ], key='-COL3-', visible=False
        )),
    ]
]

# On créer deux variables pour recevoir nos objets serial.Serial
ser1 = None
ser2 = None

# On créer deux fonctions pour lire les données des ports série et les afficher
def read_from_port1():                                         # la fonction pour lire du terminal 1
    global ser1                                                  # on déclare notre variable global
    while ser1.is_open:                                          # quand le terminal 1 est ouvert
        data = ser1.readline().decode()                            # on récupère chaque ligne qui arrive
        window["-OUTPUT1-"].print(data, end="")                    # et on l'ajoute dans la sortie du terminal 1

def read_from_port2():                                         # la fonction pour lire du terminal 2
    global ser2                                                  # on déclare notre variable global
    while ser2.is_open:                                          # quand le terminal 2 est ouvert
        data = ser2.readline().decode()                            # on récupère chaque ligne qui arrive 
        window["-OUTPUT2-"].print(data, end="")                    # et on l'ajoute dans la sortie du terminal 2

# On créer une fonction pour centrer notre fenêtre à l'écran
def move_center(window):
    screen_width, screen_height = window.get_screen_dimensions()            # on récupère les dimensions de l'écran
    win_width, win_height = window.size                                     # on récupère les dimensions de la fenêtre
    x, y = (screen_width - win_width)//2, (screen_height - win_height)//2   # on récupère la position x et y pour centrer la fenêtre par rapport à la taille de l'écran
    window.move(x, y) # window.move(x, y)                                   # on déplace la fenêtre

# On créer notre fenêtre suivant notre disposition avec son icon (chemin complet de l'image)
window = sg.Window("GUI pour terminaux séries", layout,icon=mon_icon, finalize=True)  
# on centre la fenêtre
move_center(window)                                                             


# On créer une boucle d'événements pour gérer les interactions de l'utilisateur avec l'interface
while True:     
    event, values = window.read()                                             # on récupère les événements et les valeurs 
    #print(event, values)                                                     # pour debug
    if event == sg.WINDOW_CLOSED:                                             # si on click sur la croix pour fermer l'application :
        break                                                                   # on sort de la boucle

    elif (values["-MENU-"] == "Recherche"):                                   # si on choisi dans le menu (Port COM) Recherche : 
        ports = serial.tools.list_ports.comports()                              # on créer une liste des ports série disponibles
        port_names = [port.device for port in ports]
        window["-PORT1-"].update(values=port_names)                             # on met à jour la liste des ports dans le terminal 1
        window["-PORT2-"].update(values=port_names)                             # on met à jour la liste des ports dans le terminal 2

    elif (values["-MENU-"] == "Afficher Commande AT"):                        # si on choisi dans le menu (Commande AT) Afficher Commande AT :
        window["-COL1-"].update(visible=True)                                   # on rend visible la colonne des commande AT
        window.refresh()                                                        # on rafraîchi notre fenêtre (prend en compte sa nouvelle taille)
        move_center(window)                                                     # on recentre la fenêtre 

    elif (values["-MENU-"] == "Masquer Commande AT"):                         # si on choisi dans le menu (Commande AT) Masquer Commande AT :
        window["-COL1-"].update(visible=False)                                  # on rend invisible la colonne des commande AT
        window.refresh()                                                        # on rafraîchi notre fenêtre (prend en compte sa nouvelle taille)
        move_center(window)                                                     # on recentre la fenêtre 

    elif (values["-MENU-"] == "Afficher Terminal 2"):                         # si on choisi dans le menu (Terminal 2) Afficher Terminal 2 :
        window["-COL3-"].update(visible=True)                                   # on rend visible la colonne du Terminal 2
        window.refresh()                                                        # on rafraîchi notre fenêtre (prend en compte sa nouvelle taille)
        move_center(window)                                                     # on recentre la fenêtre 

    elif (values["-MENU-"] == "Masquer Terminal 2"):                          # si on choisi dans le menu (Terminal 2) Masquer Terminal 2 :
        window["-COL3-"].update(visible=False)                                  # on rend invisible la colonne du Terminal 2    
        window.refresh()                                                        # on rafraîchi notre fenêtre (prend en compte sa nouvelle taille)        
        move_center(window)                                                     # on recentre la fenêtre     

    elif event == "-CONNECT1-":                                               # si on click sur le bouton Connecter du terminal 1 :
        port = values["-PORT1-"]                                                # on récupère le port série sélectionné pour le terminal 1
        speed = values["-SPEED1-"]                                              # on récupère la vitesse sélectionnée pour le terminal 1
        if port and speed:                                                      # si le port et la vitesse sont définis :
            try:                                                                  # on tente de :
                ser1 = serial.Serial(port, speed)                                   # définir le port à utiliser
                window["-CONNECT1-"].update(disabled=True)                          # on désactive le bouton connecter du terminal 1
                window["-DISCONNECT1-"].update(disabled=False)                      # on active le bouton déconnecter du terminal 1
                window["-INPUT1-"].update(disabled=False)                           # on active l'entée de la partie envoyer du terminal 1
                window["-SEND1-"].update(disabled=False)                            # on active le bouton envoyer du terminal 1               
                thread = threading.Thread(target=read_from_port1, daemon=True)      # on définie un thread pour lire les données du port série dans un autre processus 
                thread.start()                                                      # on lance le thread
            except serial.SerialException as e:                                   # si la tentative échoue :
                sg.popup_error(f"Erreur: {e}")                                      # on affiche un popup avec l'erreur

    elif event == "-DISCONNECT1-":                                            # si on click sur le bouton déconnecter du terminal 1 :
        if ser1 and ser1.is_open:                                               # si le terminal 1 est ouvert :
            ser1.close()                                                          # on le ferme
            window["-CONNECT1-"].update(disabled=False)                           # on active le bouton connecter du terminal 1
            window["-DISCONNECT1-"].update(disabled=True)                         # on désactive le bouton déconnecter du terminal 1
            window["-INPUT1-"].update(disabled=True)                              # on désactive l'entée de la partie envoyer du terminal 1
            window["-SEND1-"].update(disabled=True)                               # on désactive le bouton envoyer du terminal 1

    elif event == "-CONNECT2-":                                               # si on click sur le bouton Connecter du terminal 2 :      
        port = values["-PORT2-"]                                              # on récupère le port série sélectionné pour le terminal 2
        speed = values["-SPEED2-"]                                            # on récupère la vitesse sélectionnée pour le terminal 2  
        if port and speed:                                                    # si le port et la vitesse sont définis :  
            try:                                                                # on tente de :
                ser2 = serial.Serial(port, speed)                                 # définir le port à utiliser
                window["-CONNECT2-"].update(disabled=True)                        # on désactive le bouton connecter du terminal 2
                window["-DISCONNECT2-"].update(disabled=False)                    # on active le bouton déconnecter du terminal 2
                window["-INPUT2-"].update(disabled=False)                         # on active l'entée de la partie envoyer du terminal 2
                window["-SEND2-"].update(disabled=False)                          # on active le bouton envoyer du terminal 2
                thread = threading.Thread(target=read_from_port2, daemon=True)    # on définie un thread pour lire les données du port série dans un autre processus 
                thread.start()                                                    # on lance le thread      
            except serial.SerialException as e:                                 # si la tentative échoue :
                sg.popup_error(f"Erreur: {e}")                                    # on affiche un popup avec l'erreur      

    elif event == "-DISCONNECT2-":                                            # si on click sur le bouton déconnecter du terminal 2 :      
        if ser2 and ser2.is_open:                                               # si le terminal 2 est ouvert :
            ser2.close()                                                        # on le ferme
            window["-CONNECT2-"].update(disabled=False)                         # on active le bouton connecter du terminal 2
            window["-DISCONNECT2-"].update(disabled=True)                       # on désactive le bouton déconnecter du terminal 2    
            window["-INPUT2-"].update(disabled=True)                            # on désactive l'entée de la partie envoyer du terminal 2        
            window["-SEND2-"].update(disabled=True)                             # on désactive le bouton envoyer du terminal 2            

    elif event == "-SEND1-":                                                  # si on click sur le bouton envoyer du terminal 1 :      
        command = values["-INPUT1-"]                                            # on récupère l'entrée du terminal 1
        if ser1 and ser1.is_open and command:                                   # si le terminal 1 est ouvert et que l'entrée n'est pas vide :
            ser1.write(command.encode() + b"\r\n")                                # on écrit l'entrée dans le terminal 1
            window["-INPUT1-"].update("")                                         # on vide l'entrée

    elif event == "-SEND2-":                                                  # si on click sur le bouton envoyer du terminal 2 :
        command = values["-INPUT2-"]                                            # on récupère l'entrée du terminal 2
        if ser2 and ser2.is_open and command:                                   # si le terminal 2 est ouvert et que l'entrée n'est pas vide :
            ser2.write(command.encode() + b"\r\n")                                # on écrit l'entrée dans le terminal 2
            window["-INPUT2-"].update("")                                         # on vide l'entrée

    elif event == "-ERASE1-":                                                 # si on click sur le bouton effacer du terminal 1 :
        window["-OUTPUT1-"].update("")                                          # on vide la sortie du terminal 1 :

    elif event == "-ERASE2-":                                                 # si on click sur le bouton effacer du terminal 2 :  
        window["-OUTPUT2-"].update("")                                          # on vide la sortie du terminal 2 :                                                   

    elif event == "-LORA-":                                                   # si on a coché LoraE5 (par défaut, dans la colonne Commande AT)
        window["-BT-"].update(False)                                            # on décoche BT HC05
        infos_list = infos_command_LoraE5                                       # la liste d'infos est celle du LoraE5
        command_device = command_LoraE5                                         # la liste des commandes est celle du LoraE5
        window["-COMMAND-"].update(values=command_LoraE5)                       # on met à jour la liste des commandes

    elif event == "-BT-":                                                     # si on a coché BT HC05
        window["-LORA-"].update(False)                                          # on décoche LoraE5
        infos_list = infos_command_BT                                           # la liste d'infos est celle du BT HC05   
        command_device = command_BT                                             # la liste des commandes est celle du BT HC05  
        window["-COMMAND-"].update(values=command_BT)                           # on met à jour la liste des commandes                

    elif event == "-COMMAND-":                                                # si on click sur une commande            
        index = command_device.index(values["-COMMAND-"][0])                    # on récupère la place de la commande dans le tableau                        
        selected_item = infos_list[index]                                       # on récupère l'infos correspondant a cette place dans le tableau des infos
        window['-OUTPUT-'].update(f'{selected_item}')                           # on met à jour la liste des infos         
        window["-INPUT1-"].update(values["-COMMAND-"][0])
        window["-INPUT2-"].update(values["-COMMAND-"][0])
        
#si on sort de la boucle on ferme l'application
window.close()
exit()