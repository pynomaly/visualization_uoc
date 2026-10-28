import pandas as pd

URL = "https://datos.madrid.es/dataset/795391-0-organigrama-del-ayuntamiento-de-madrid-y-sus-organismos-autonomos/resource/795391-1-organigrama-del-ayuntamiento-de-madrid-y-sus-organismos-autonomos/download/795391-1-organigrama-del-ayuntamiento-de-madrid-y-sus-organismos-autonomos.csv"

df = pd.read_csv(URL, sep=";")

# Eliminar duplicados
df_unique = df.drop_duplicates(subset=["cod_unidad"])

cod_raiz = 10000027  # correspondiente a urbanismo

# Nivel 0: unidad raíz
nivel_0 = df_unique[df_unique["cod_unidad"] == cod_raiz][["cod_unidad", "unidad"]]
nivel_0 = nivel_0.rename(columns={"cod_unidad": "cod_nivel_0", "unidad": "nivel_0"})

# Nivel 1: hijos directos
nivel_1 = df_unique[df_unique["unidad_padre"] == cod_raiz][["cod_unidad", "unidad"]]
nivel_1 = nivel_1.rename(columns={"cod_unidad": "cod_nivel_1", "unidad": "nivel_1"})

# Nivel 2: hijos de nivel 1
codigos_nivel_1 = nivel_1["cod_nivel_1"].tolist()
nivel_2 = df_unique[df_unique["unidad_padre"].isin(codigos_nivel_1)][
    ["cod_unidad", "unidad", "unidad_padre"]
]
nivel_2 = nivel_2.rename(
    columns={
        "cod_unidad": "cod_nivel_2",
        "unidad": "nivel_2",
        "unidad_padre": "cod_nivel_1",
    }
)

# Unir nivel 1 con nivel 2
df_dendrograma = nivel_1.merge(nivel_2, on="cod_nivel_1", how="left")

# Añadir la raíz
df_dendrograma["nivel_0"] = nivel_0["nivel_0"].values[0]
df_dendrograma["cod_nivel_0"] = cod_raiz

# Reordenar columnas
df_dendrograma = df_dendrograma[
    ["cod_nivel_0", "nivel_0", "cod_nivel_1", "nivel_1", "cod_nivel_2", "nivel_2"]
]

df_dendrograma.to_csv("urbanismo.csv", index=False)
