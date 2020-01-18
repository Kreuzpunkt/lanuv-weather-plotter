"""
Diese Klasse holt sich die Daten von der Webseite mittels des Python-modules 
request
"""
# Tool um Inhalte runterzuladen
import requests

# Tool um zu gucken, ob Dateien/Verzeichnisse existieren - Systemunabhängig !!
from pathlib import Path

# Für Datum und co
from datetime import date

# Definition von Fehlermeldungen (stehen außerhalb, da ich sonst über das
# 80 zeichen limit komme)

FEHLERMELDUNG_TIMEOUT = """Die Seite lanuv.nrw.de ist gerade nicht verfügbar. 
Außerdem ist die gewählt Statistik nicht zwischengespeichert. Versuche es 
später noch mal.""".replace(
    "\n", ""
)

FEHLERMELDUNG_INDEX = """
Invalide Anfragenummer: {}. Muss eine Zahl von 0-8 sein.
""".replace(
    "\n", ""
)

class Downloader:

    # hier werden Daten abgelegt
    SPEICHERFPAD = Path("daten")

    # mögliche Anfragetypen wobei (Webseitenname,Realname)

    ANFRAGETYPEN = {
        0: ("NO_AM1H", "Stickstoffmonoxid"),
        1: ("NO2_AM1H", "Stickstoffdioxid"),
        2: ("O3_AM1H", "Ozon"),
        3: ("PM10F_GM24H", "Partikel"),
        4: ("SO2_AM1H", "Schwefeldioxid"),
        5: ("T_AM1H", "Temperatur"),
        6: ("F_AM1H", "Luftfeuchtigkeit"),
        7: ("WR_VM1H", "Windgeschwindigkeit"),
        8: ("WG_SM1H", "Windrichtung"),
    }

    def __init__(self):
        # Daten sollen lokal gespeichert werden. Prüfe ob Speicherort
        # existiert, falls nicht erstelle Verzeichniss
        if not Downloader.SPEICHERFPAD.is_dir():
            Downloader.SPEICHERFPAD.mkdir()

    """
        Holt die Daten von der Internetseite und speichert diese lokal
    """

    def get(self, anfragenummer):
        # mit einem r vor dem String hat man keine Probleme mit Sonderzeichen
        basis = r"https://www.lanuv.nrw.de/fileadmin/lanuv/luft/temes/"
        anfrage = Downloader.ANFRAGETYPEN.get(anfragenummer, None)

        if anfrage is None:
            raise TypeError(FEHLERMELDUNG_INDEX.format(anfragenummer))

        # Es kann passieren, dass die Webseite nicht erreichbar ist
        try:
            # Tupel in zwei Variablen ausladen
            seitenname, realname = anfrage
            # Gewünschte Datei
            datei = realname + ".csv"
            # Speicherplatz der Datei
            dateispeicherplatz = Downloader.SPEICHERFPAD / Path(datei)

            # Datei aktualisieren
            if dateispeicherplatz.is_file():

                # Datumszeile aus der Datei holen
                with dateispeicherplatz.open() as lokale_datei:
                    erste_zeile = lokale_datei.readline()

                # wenn das heutige Datum nicht in der Datei steht ist diese alt

                heute = date.today().strftime("%d.%m.%Y")
                # quelle : 
                # https://www.programiz.com/
                # python-programming/datetime/current-datetime
                # Example 2 Zeile 6 abgewandelt

                # ist das heutige Datum NICHT in der Infozeile der csv-Datei
                if not heute in erste_zeile:
                    print("{} wird aktualisiert".format(datei))
                    
                    # herunterladen von der Webseite
                    daten = requests.get(basis + seitenname + ".csv").text
                    
                    # schreibe Inhalt in Datei
                    with dateispeicherplatz.open("w") as lokale_datei:
                        lokale_datei.write(daten)

            else:
                pfad = basis + seitenname + ".csv"
                print("{} wird heruntergeladen".format(pfad))

                # Herunterladen von der Webseite
                daten = requests.get(pfad).text

                # schreibe Inhalt in Datei
                with dateispeicherplatz.open("w") as lokale_datei:
                    lokale_datei.write(daten)

            return datei, dateispeicherplatz

        except requests.ConnectionError:
            # Seite nicht erreichbar
            raise TypeError(FEHLERMELDUNG_TIMEOUT)

