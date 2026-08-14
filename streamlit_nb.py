import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Nacional B · Top Jugadores", layout="wide", initial_sidebar_state="expanded")

RENOMBRES = {
    "player": "Jugador", "team": "Equipo", "posicion": "Posición",
    "appearances": "Partidos", "minutesPlayed": "Minutos", "rating": "Rating",
    "goals": "Goles", "assists": "Asistencias", "goalsAssistsSum": "G+A",
    "penaltyGoals": "Goles penalti", "expectedGoals": "xG", "expectedAssists": "xA",
    "totalShots": "Tiros", "shotsOnTarget": "Tiros al arco", "shotsOffTarget": "Tiros fuera",
    "bigChancesCreated": "GC grandes", "keyPasses": "Pases clave",
    "totalPasses": "Pases", "accuratePassesPercentage": "% pases ok",
    "successfulDribbles": "Regates ok", "tackles": "Entradas",
    "interceptions": "Intercepciones", "ballRecovery": "Balones rec.",
    "clearances": "Despejes", "blockedShots": "Tiros bloqueados",
    "totalDuelsWon": "Duelos ganados", "duelLost": "Duelos perdidos",
    "wasFouled": "Faltas recibidas", "fouls": "Faltas",
    "yellowCards": "Amarillas", "redCards": "Rojas", "ownGoals": "Autogoles",
    "Edad": "Edad",
}

PER90 = ["goals", "assists", "goalsAssistsSum", "expectedGoals", "expectedAssists",
         "totalShots", "shotsOnTarget", "keyPasses", "successfulDribbles",
         "tackles", "interceptions", "ballRecovery", "totalDuelsWon",
         "wasFouled", "fouls", "yellowCards", "redCards"]
for c in PER90:
    RENOMBRES[f"{c}_per90"] = f"{RENOMBRES[c]} /90"

COLUMNAS_GRUPOS = {
    "Básicas": ["player", "team", "posicion", "Edad", "rating", "minutesPlayed", "appearances"],
    "Ataque": ["goals", "assists", "goalsAssistsSum", "expectedGoals", "expectedAssists", "penaltyGoals"],
    "Tiros": ["totalShots", "shotsOnTarget", "shotsOffTarget"],
    "Creación": ["bigChancesCreated", "keyPasses", "successfulDribbles"],
    "Pases": ["totalPasses", "accuratePassesPercentage"],
    "Defensa": ["tackles", "interceptions", "ballRecovery", "clearances", "blockedShots", "totalDuelsWon", "duelLost"],
    "Disciplina": ["yellowCards", "redCards", "fouls", "wasFouled", "ownGoals"],
    "Por 90": [f"{c}_per90" for c in PER90],
}

ORDENES = ["rating", "goals", "goals_per90", "expectedGoals", "expectedGoals_per90",
           "assists", "keyPasses", "minutesPlayed", "appearances", "totalShots",
           "successfulDribbles", "tackles", "ballRecovery", "Edad"]


@st.cache_data
def cargar():
    df = pd.read_csv("data/top_jugadores_nb.csv")
    df["player id"] = df["player id"].astype(str)
    df["team id"] = df["team id"].astype(str)
    df["Edad"] = pd.to_numeric(df["Edad"], errors="coerce").astype("Int64")
    return df


@st.cache_data
def ultima_actualizacion() -> str:
    try:
        with open("data/ultima_actualizacion.txt") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "desconocida"


df = cargar()

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("## Argentina - Nacional B")
    st.caption(f"Temporada 2026 · Sofascore · Datos: {ultima_actualizacion()}")
    st.divider()

    posiciones = st.multiselect("Posición", sorted(df["posicion"].dropna().unique()),
                                default=sorted(df["posicion"].dropna().unique()))
    equipos = st.multiselect("Equipo", sorted(df["team"].unique()), default=sorted(df["team"].unique()))

    rango_edad = st.slider("Edad", 15, 45, (15, 45))
    rango_min = st.slider("Minutos mínimos", 0, int(df["minutesPlayed"].max()), 300)
    rating_min = st.slider("Rating mínimo", 0.0, 10.0, 0.0, 0.1)

    st.divider()
    orden_col = st.selectbox("Ordenar por", ORDENES, format_func=lambda c: RENOMBRES[c])
    ascendente = st.checkbox("Ascendente", value=False)

    grupos_sel = st.multiselect("Columnas a mostrar", list(COLUMNAS_GRUPOS),
                                default=["Básicas", "Ataque", "Tiros", "Creación", "Por 90"])

# ======================
# FILTROS
# ======================
filtro = (
    df["posicion"].isin(posiciones)
    & df["team"].isin(equipos)
    & ((df["Edad"].isna()) | (df["Edad"] >= rango_edad[0]) & (df["Edad"] <= rango_edad[1]))
    & (df["minutesPlayed"] >= rango_min)
    & (df["rating"] >= rating_min)
)

filtrado = df[filtro].copy()
if filtrado.empty:
    st.warning("No hay jugadores que cumplan los filtros.")
    st.stop()

filtrado = filtrado.sort_values(orden_col, ascending=ascendente, na_position="last")

# ======================
# MÉTRICAS
# ======================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jugadores", f"{len(filtrado):,}")
c2.metric("Rating promedio", f"{filtrado['rating'].mean():.2f}")
c3.metric("Goles totales", f"{filtrado['goals'].sum():,.0f}")
mejor = filtrado.loc[filtrado["rating"].idxmax()]
c4.metric("Mejor rating", f"{mejor['rating']:.2f}", f"{mejor['player']}")

tab_tabla, tab_graficos, tab_ficha = st.tabs(["📋 Tabla", "📊 Gráficos", "👤 Ficha de jugador"])

# ======================
# TABLA
# ======================
with tab_tabla:
    cols = []
    for g in grupos_sel:
        cols += [c for c in COLUMNAS_GRUPOS[g] if c in filtrado.columns]
    cols = list(dict.fromkeys(cols))

    vista = filtrado[cols].rename(columns=RENOMBRES)

    config = {}
    for c in vista.columns:
        if pd.api.types.is_numeric_dtype(vista[c]):
            if pd.api.types.is_integer_dtype(vista[c]):
                config[c] = st.column_config.NumberColumn(format="%d")
            else:
                config[c] = st.column_config.NumberColumn(format="%.2f")

    st.dataframe(vista, width="stretch", height=520, column_config=config)

    csv = vista.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar CSV", data=csv, file_name="top_jugadores_filtrado.csv",
                       mime="text/csv")

# ======================
# GRÁFICOS
# ======================
with tab_graficos:
    g1, g2 = st.columns(2)
    with g1:
        fig = px.scatter(filtrado, x="goals_per90", y="expectedGoals_per90",
                         color="posicion", size="minutesPlayed",
                         hover_name="player", hover_data=["team", "rating"],
                         labels={"goals_per90": "Goles /90", "expectedGoals_per90": "xG /90"},
                         title="Goles vs xG por 90")
        st.plotly_chart(fig, width="stretch")
    with g2:
        top = filtrado.nlargest(10, "rating")
        fig = px.bar(top.sort_values("rating"), x="rating", y="player", orientation="h",
                     color="posicion", hover_data=["team", "minutesPlayed"],
                     labels={"rating": "Rating", "player": ""}, title="Top 10 rating")
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")

    g3, g4 = st.columns(2)
    with g3:
        fig = px.scatter(filtrado, x="goals", y="assists", color="posicion",
                         size="minutesPlayed", hover_name="player", hover_data=["team", "rating"],
                         labels={"goals": "Goles", "assists": "Asistencias"},
                         title="Goles vs Asistencias")
        st.plotly_chart(fig, width="stretch")
    with g4:
        fig = px.histogram(filtrado.dropna(subset=["Edad"]), x="Edad", nbins=20,
                           color_discrete_sequence=["#0ea5e9"],
                           labels={"Edad": "Edad"}, title="Distribución de edad")
        st.plotly_chart(fig, width="stretch")

# ======================
# FICHA DE JUGADOR
# ======================
with tab_ficha:
    jugador = st.selectbox("Seleccionar jugador", filtrado["player"].unique())
    p = filtrado[filtrado["player"] == jugador].iloc[0]

    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("Rating", f"{p['rating']:.2f}")
    f2.metric("Goles", f"{p['goals']:.0f}")
    f3.metric("Goles /90", f"{p['goals_per90']:.2f}")
    f4.metric("Asistencias", f"{p['assists']:.0f}")
    f5.metric("Minutos", f"{p['minutesPlayed']:.0f}")

    if pd.notna(p["Edad"]):
        st.markdown(f"**{p['player']}** · {p['team']} · {p['posicion']} · {p['Edad']:.0f} años")
    else:
        st.markdown(f"**{p['player']}** · {p['team']} · {p['posicion']}")

    ficha_metricas = ["expectedGoals_per90", "expectedAssists_per90", "keyPasses_per90",
                      "successfulDribbles_per90", "tackles_per90", "interceptions_per90",
                      "ballRecovery_per90", "yellowCards_per90"]
    comp = pd.DataFrame({
        "Métrica": [RENOMBRES[c] for c in ficha_metricas],
        "Jugador": [p[c] for c in ficha_metricas],
        "Promedio liga": [df[c].mean() for c in ficha_metricas],
    }).melt(id_vars="Métrica", var_name="Referencia", value_name="Valor")

    fig = px.bar(comp, x="Valor", y="Métrica", color="Referencia", barmode="group",
                 title="Jugador vs promedio de la liga (por 90)",
                 labels={"Valor": "Por 90", "Métrica": ""})
    fig.update_layout(height=420)
    st.plotly_chart(fig, width="stretch")
