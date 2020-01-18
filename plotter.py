# Tool zum Zeichnen
import plotly.graph_objects as go

# Tool für berechnungen der Datensätze
import numpy as np

# (https://plot.ly/python/ referenz)
import pandas as pd

# Berechnung von Zeitdifferenzen
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Plotter:
    def __init__(self, name, dateipfad, tage, messstation, alle_stationen, einheit):
        self.name = name
        self.dateipfad = dateipfad
        self.tage = tage
        self.messstation = messstation
        self.alle_stationen = alle_stationen
        self.einheit = einheit
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
            oben mit einem "<" ab
        """

        def convert(item):

            if item == "":
                return "0"
            else:
                return item.replace("<", "")

        # https://honingds.com/blog/pandas-read_csv/
        # da wurde alles erklärt

        df = pd.read_csv(
            self.dateipfad,
            # umbenennung
            names=["date", "time"] + self.alle_stationen,
            # daten in der csv sind in verkehrt
            skiprows=range(0, 24 * (365 - self.tage - 1)),
            # csv mit ; getrennt
            sep=";",
            # erste Zeile ist kommentar
            header=1,
            # Datum muss zusammengesetzt werden
            parse_dates={"date_col": ["date", "time"]},
            encoding="utf-8",
            # Datum wir aus date und time zusammengesetzt
            date_parser=dateparser,
            # Konvertierung von ungültigen Einträgen
            converters=dict((w, convert) for w in self.alle_stationen),
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

        fig.update_layout(
            # (kopiert von https://stackoverflow.com/questions/441147/how-to-subtract-a-day-from-a-date/29104710#29104710)
            xaxis_title="Zeitraum vom {} bis {}".format(
                (datetime.today() - relativedelta(days=self.tage)).date(),
                datetime.today().date(),
            ),
            yaxis_title="{} {}".format(self.name, self.einheit),
        )

        fig.show()
