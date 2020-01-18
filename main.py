from downloader import Downloader
from plotter import Plotter

# @ Hannes Einheiten für die sachen unten hinzufügen wie Temperatur in Celsius

EINGANGSTEXT = """
Grafische Darstellung von Wetterdaten.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diese Programm erzeugt ein Diagramm it aktuellen Wetterdaten der letzten Tage.
Hierfür werden 3 Paramtere gebraucht:
- Gewünschter Messwert                  Standard=Temperatur
- Anzahl der darzustellenden Tage       Standard=7
- Messstation                           Standard=BONN

Folgende Messwerte stehen zur Auswahl:

    0] Stickstoffmonoxid (NO)
    1] Stickstoffdioxid (NO2)
    2] Ozon (O3)
    3] Partikel PM10
    4] Schwefeldioxid (SO2)
    5] Temperatur (Celsius)
    6] Relative Luftfeuchtigkeit
    7] Windgeschwindigkeit
    8] Windrichtung

Es kann vorkommen, dass Messwerte ungültig sind. Diese werden dann einfach auf
0 gesetzt.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

EINGABE_MESSWERT = "Gebe die Kennziffer des gewünschten Messwerts ein: "

"""
    Der Auswahlhelfer kümmert sich darum, dass der Nutzer richtige Eingaben 
    macht. Außerdem formatiert er diese und ruft den Downloader auf. Falls
    alle Angaben richtig waren werden diese gezeichnet.
"""


class Auswahlhelfer:
    def __init__(self):
        self.dl = Downloader()

    def automodus(self):
        print(EINGANGSTEXT)

        self.name, self.datei = self.auswahl_messwerte()
        self.stationen = self.erstelle_auswahl()
        self.tage = self.auswahl_tage()
        self.station = self.auswahl_station()

        self.plotter = Plotter(
            self.name, self.datei, self.tage, self.station, self.stationen, self.einheit
        )

    def erstelle_auswahl(self):
        # zweite zeile auslesen
        with self.datei.open("r") as file:
            file.readline()
            stationen = file.readline()

        stationen_liste = []

        # datum und zeit auslassen
        trennung = stationen.split(";")[2:]

        for eintrag in trennung:
            # alles ist durch ein leerzeichen getrennt
            name = eintrag.split(" ")[0]
            stationen_liste.append(name)

        # letzter Eintrag ist die einheit
        self.einheit = eintrag.split(" ")[-1]

        return stationen_liste

    def auswahl_messwerte(self):
        eingabe = input(EINGABE_MESSWERT)

        try:
            # Standardwert
            if eingabe == "":
                auswahl = 5
            else:
                auswahl = int(eingabe)

            # Wenn die Eingabe valide ist wird die Datei heruntergeladen
            name, datei = Downloader().get(auswahl)

            print("Auswertung für Messwert '{}'".format(name))

            return name, datei

        except TypeError as te:

            # Fehler während des Downloadens
            print(te)
            self.auswahl_messwerte()

        except ValueError:

            # Inkorrekte Eingabe
            print("Eingabe inkorrekt. Wähle eine Zahl zwischen 0 und 8.")
            self.auswahl_messwerte()

    def auswahl_tage(self):
        eingabe = input("\nGib die Anzahl an Tagen an: ")

        try:
            # Standardwert
            if eingabe == "":
                auswahl = 7
            else:
                auswahl = int(eingabe)

            # Fehlerüberprüfung
            if auswahl > 365:
                print("Datensatz reicht nur für 365 Tage aus.")
                self.auswahl_tage()
            elif auswahl <= 0:
                print("Muss eine Zahl größer 0 sein.")
                self.auswahl_tage()
            else:
                print("Auswertung für {} Tage".format(auswahl))
                return auswahl

        except ValueError:

            print("Eingabe inkorrekt.")
            self.auswahl_tage()

    def auswahl_station(self):
        print("Mögliche Wetterstationen:")

        for station in self.stationen:
            print("\t", station, sep="")

        eingabe = input("Geben sie den name der Wetterstationen an: ")

        # Standardwert
        if eingabe == "":
            auswahl = "BONN"
        else:
            auswahl = eingabe.upper()

        # Fehlerüberprüfung
        if auswahl in self.stationen:
            print("Messstation {} ausgewählt".format(auswahl))
            return auswahl
        else:
            print("Eingabe inkorrekt")
            self.auswahl_station()


Auswahlhelfer().automodus()
