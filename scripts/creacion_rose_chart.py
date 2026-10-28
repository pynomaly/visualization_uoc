import numpy as np
import pandas as pd
import plotly.express as px

# Fuente: https://analisi.transparenciacatalunya.cat/Societat-benestar/L-nia-d-atenci-contra-la-viol-ncia-masclista-900-9/q2sg-894k/about_data
ARCHIVO = "datasets/linea_violencia_machista_900_900_120_20261026.csv"

d = pd.read_csv(ARCHIVO, low_memory=False)

d = d[d["Any"] == 2025]  # selecciono solo los registros de 2025

# Mapeo de la persona que contacta al castellano
d["persona"] = d["Persona que truca"].map(
    {
        "La pròpia usuària": "La propia usuaria",
        "Familiar o persona propera": "Familiar o persona cercana",
        "Professional": "Profesional u otros",
        "Altres": "Profesional u otros",
    }
)
d["hora"] = pd.to_datetime(d["Hora"], format="mixed").dt.hour

# Contactos por hora y persona
conteo = d.groupby(["hora", "persona"]).size().reset_index(name="contactos")
conteo["hora"] = conteo["hora"].astype(int).map("{:02d} h".format)

# Orden de las horas y de las categorías (de mayor a menor, de dentro a fuera)
horas = [f"{h:02d} h" for h in range(24)]
personas = (
    conteo.groupby("persona")["contactos"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)

# Proporcional al área y no al radio
conteo["persona"] = pd.Categorical(conteo["persona"], personas, ordered=True)
conteo = conteo.sort_values(["hora", "persona"])
acumulado = conteo.groupby("hora")["contactos"].cumsum()
conteo["radio"] = np.sqrt(acumulado) - np.sqrt(acumulado - conteo["contactos"])

# Rose chart apilado
fig = px.bar_polar(
    conteo,
    r="radio",
    theta="hora",
    color="persona",
    category_orders={"hora": horas, "persona": personas},
    color_discrete_map={
        "La propia usuaria": "#6a3d7c",
        "Familiar o persona cercana": "#ddc9e5",
        "Profesional u otros": "#2f7e49",
    },
    hover_data={"contactos": True, "radio": False},
    labels={
        "persona": "Persona que contacta",
        "contactos": "Contactos",
        "hora": "Hora",
    },
    title="<b>Llamadas a la Línea contra la Violencia Machista 900 900 120</b>",
    subtitle="Distribución por hora y persona que contacta en 2025",
)
fig.update_layout(
    polar_angularaxis_rotation=90,
    polar_angularaxis_direction="clockwise",
    polar_radialaxis_showticklabels=False,  # las magnitudes son por área, no radio
    title_font_size=22,
    annotations=[
        dict(
            text="<b>Fuente</b>: Dades Obertes de Catalunya."
            "El área de cada segmento es proporcional al número de contactos.",
            x=0,
            y=-0.05,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="left",
            font=dict(size=13),
        )
    ],
    margin=dict(b=80),
)
fig.write_html("rose_chart.html")
