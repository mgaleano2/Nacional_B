# Nacional B · Top Jugadores

Ranking y análisis de jugadores de la **Primera Nacional (Nacional B) 2026** con datos de la API de [Sofascore](https://www.sofascore.com/).

## App en línea

**https://nacional-b.streamlit.app**

## Estructura

| Archivo | Rol |
|---|---|
| `streamlit_nb.py` | App Streamlit: filtros (Posición, Equipo, Edad 15-45, Minutos, Rating), tabla, gráficos y ficha por jugador. |
| `nacional_b.py` | Scraper: baja stats de Sofascore y genera `data/top_jugadores_nb.csv` (posición, edad, columnas /90, filtro 300'). |
| `requirements.txt` | Dependencias para Streamlit Community Cloud. |

## Datos

`data/top_jugadores_nb.csv` — **734 jugadores × 52 columnas** (última actualización en `data/ultima_actualizacion.txt`).

## Correr local

```bash
python nacional_b.py --actualizar   # regenerar datos
streamlit run streamlit_nb.py       # levantar app
```

## Fuente

[Sofascore](https://www.sofascore.com/) · API pública (no oficial)
