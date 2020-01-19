# Tool zum Zeichnen
import plotly.graph_objects as go

# (https://plot.ly/python/ referenz)
import pandas as pd

# Berechnung von Zeitdifferenzen
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Plotter:
    def __init__(self, name, datei, tage, messstation, allestationen, einheit):

        self.name = name
        self.dateipfad = datei
        self.tage = tage
        self.messstation = messstation
        self.allestationen = allestationen
        self.einheit = einheit
        # plotten
        self.draw()

    def draw(self):
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

        # https://honingds.com/blog/pandas-read_csv/
        # da wurde alles erklärt

        df = pd.read_csv(
            self.dateipfad,
            # umbenennung
            names=["date", "time"] + self.allestationen,
            # daten in der csv sind in verkehrt
            skiprows=range(0, 24 * (365 - self.tage) + 2),
            # csv mit ; getrennt
            sep=";",
            # erste Zeile ist kommentar
            header=1,
            # Datum muss zusammengesetzt werden
            parse_dates={"date_col": ["date", "time"]},
            encoding="utf-8",
            # Datum wir aus date und time zusammengesetzt
            date_parser=dateparser,
            # Konvertierung von ungültigen Einträgen. Dafür gehen die Werte
            # in die Funktion convert. (Werte=Mögliche Messtationen)
            # https://stackoverflow.com/questions/1747817/
            # create-a-dictionary-with-list-comprehension/1747827#1747827
            converters=dict((w, convert) for w in self.allestationen),
        )

        fig = go.Figure()
        # linie hinzufügen

        fig.add_trace(
            go.Scatter(
                x=df["date_col"],
                y=df[self.messstation],
                # spline sieht schön aus
                line_shape="spline",
                name=self.name,
            )
        )
        # (angelehnt an https://stackoverflow.com/questions/
        # 441147/how-to-subtract-a-day-from-a-date/29104710#29104710)
        vom = (datetime.today() - relativedelta(days=self.tage)).date()
        bis = datetime.today().date()

        # Sachinformationen hinzufügen
        fig.update_layout(
            xaxis_title="Zeitraum vom {} bis {}".format(vom, bis),
            yaxis_title="{} {}".format(self.name, self.einheit),
        )

        fig.show()
