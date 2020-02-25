# Tool zum Zeichnen
import plotly.graph_objects as go

# (https://plot.ly/python/ referenz)
import pandas as pd

# Berechnung von Zeitdifferenzen
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Plotter:
    def __init__(self, name, datei, tage, messstation, allestationen, einheit, modus):

        self.name = name
        self.dateipfad = datei
        self.tage = tage
        self.allestationen = allestationen
        self.einheit = einheit
        # um mehrere Wetterstationen zu unterstüzen
        self.messstation = list(messstation)
        # parse and draw
        self.df = self.interpret_csv()
        self.draw(modus)

    def interpret_csv(self):
        def dateparser(datum, zeit):
            """
                pandas nimmt 24:00 uhr nicht an, es muss 0:00 sein.
                Hier muss aber ein unsauberer Weg leider genommen werden
                denn plotly interpretiert 0:00 falsch
            """

            if zeit == "24:00":
                return pd.to_datetime(datum + " 23:59:59", dayfirst=True)
            else:
                return pd.to_datetime(datum + " " + zeit, dayfirst=True)

        """
            Manche Einträge sind entweder leer oder schätzen den Wert nach 
            oben mit einem "<" ab. Außerdem müssen die Einträge in eine
            Gleitkommazahl konvertiert werden.
        """

        def convert(item):

            if item == "":
                return float("0")
            else:
                return float(item.replace("<", "").replace(",", "."))

        # wegen header=1 müssen die ersten beiden Zeilen nicht betrachtet
        # werden
        if self.tage == 365:
            ueberspringen = 0
        else:
            # Neuer Tag fängt immer eine Zeile danach an
            ueberspringen = 24 * (366 - self.tage)

        # https://honingds.com/blog/pandas-read_csv/
        # da wurde alles erklärt

        df = pd.read_csv(
            self.dateipfad,
            # umbenennung
            names=["date", "time"] + self.allestationen,
            # daten in der csv sind in verkehrt
            skiprows=ueberspringen,
            # csv mit ; getrennt
            sep=";",
            # erste Zeile ist kommentar
            header=1,
            # Datum muss zusammengesetzt werden
            parse_dates={"date_col": ["date", "time"]},
            encoding="utf-8",
            # Datum wir aus date und time zusammengesetzt
            date_parser=dateparser,
            # Begrenzung auf nur nötige daten
            usecols=["date", "time"] + self.messstation,
            # Konvertierung von ungültigen Einträgen. Dafür gehen die Werte
            # in die Funktion convert. (Werte=Mögliche Messtationen)
            # https://stackoverflow.com/questions/1747817/
            # create-a-dictionary-with-list-comprehension/1747827#1747827
            converters=dict((w, convert) for w in self.allestationen),
        )

        return df

    def draw(self, modus):

        fig = go.Figure()
        # linie hinzufügen

        for station in self.messstation:

            data = self.df[station]

            if modus == 2:
                arr = data.to_numpy()
                # wert von tag i minus wert von tag i-1
                data = arr[1:] - arr[:-1]

            fig.add_trace(
                go.Scatter(
                    # letzter tag hat keinen vorgänger
                    x=self.df["date_col"][1:],
                    y=data,
                    # spline sieht schön aus
                    line_shape="spline",
                    name=station,
                )
            )

        # (angelehnt an https://stackoverflow.com/questions/
        # 441147/how-to-subtract-a-day-from-a-date/29104710#29104710)
        vom = (datetime.today() - relativedelta(days=self.tage)).date()
        bis = datetime.today().date()

        # Sachinformationen hinzufügen
        fig.update_layout(
            xaxis_title="{} im Zeitraum vom {} bis {}".format(
                "Differezanzeige" if modus - 1 else "Normalwertanzeige", vom, bis
            ),
            yaxis_title="{} {}".format(self.name, self.einheit),
        )

        fig.show()
