import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="AW-Bikes | Business Intelligence",
    page_icon="🚲",
    layout="wide"
)

st.title("🚲 AW-Bikes — Business Intelligence Pilot")
st.caption(
    "Análisis de clientes, comportamiento de compra y oportunidades de segmentación comercial"
)

# ============================================================
# 1. CARGA DE DATOS
# ============================================================
default = Path("datos_actividad1.xlsx")

if not default.exists():
    st.error("No se encontró el archivo datos_actividad1.xlsx en el directorio de la aplicación.")
    st.stop()

df = pd.read_excel(default, sheet_name="Hoja2")

# ============================================================
# 2. NORMALIZACIÓN
# ============================================================
df["BikeBuyer"] = pd.to_numeric(df["BikeBuyer"], errors="coerce")
df["AvgMonthSpend"] = pd.to_numeric(df["AvgMonthSpend"], errors="coerce")
df["YearlyIncome"] = pd.to_numeric(df["YearlyIncome"], errors="coerce")

df["BikeBuyerText"] = df["BikeBuyer"].map({
    1: "Sí",
    0: "No"
})

# ============================================================
# 3. FILTROS
# ============================================================
st.sidebar.header("🔎 Filtros")

countries = sorted(df["CountryRegionName"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "País",
    countries,
    default=countries
)

buyer_options = ["Sí", "No"]

selected_buyers = st.sidebar.multiselect(
    "Compra de bicicleta",
    buyer_options,
    default=buyer_options
)

view = df[
    df["CountryRegionName"].isin(selected_countries)
    & df["BikeBuyerText"].isin(selected_buyers)
].copy()

if view.empty:
    st.warning("No existen registros para los filtros seleccionados.")
    st.stop()

# ============================================================
# 4. GRÁFICA 1 — TASA DE COMPRA POR OCUPACIÓN
# ============================================================
st.header("1. Tasa de compra por ocupación")

occ = (
    view.groupby("Occupation")
    .agg(
        Clientes=("CustomerID", "size"),
        Compradores=("BikeBuyer", "sum"),
        Tasa_compra=("BikeBuyer", "mean"),
        Gasto_medio=("AvgMonthSpend", "mean")
    )
    .reset_index()
)

occ["Tasa_pct"] = occ["Tasa_compra"] * 100
occ = occ.sort_values("Tasa_pct", ascending=True)

fig1 = px.bar(
    occ,
    x="Tasa_pct",
    y="Occupation",
    orientation="h",
    text="Tasa_pct",
    labels={
        "Tasa_pct": "Tasa de compra (%)",
        "Occupation": "Ocupación"
    },
    title="¿Qué perfiles profesionales presentan mayor tasa de compra?"
)

fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig1.update_layout(
    xaxis_range=[0, max(100, occ["Tasa_pct"].max() * 1.15)],
    height=480
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "Insight: esta gráfica permite identificar diferencias de comportamiento entre "
    "perfiles profesionales y formular hipótesis para campañas segmentadas."
)

# ============================================================
# 5. GRÁFICA 2 — TASA DE COMPRA POR EDUCACIÓN
# ============================================================
st.header("2. Tasa de compra por nivel educativo")

edu = (
    view.groupby("Education")
    .agg(
        Clientes=("CustomerID", "size"),
        Tasa_compra=("BikeBuyer", "mean"),
        Gasto_medio=("AvgMonthSpend", "mean")
    )
    .reset_index()
)

edu["Tasa_pct"] = edu["Tasa_compra"] * 100
edu = edu.sort_values("Tasa_pct", ascending=True)

fig2 = px.bar(
    edu,
    x="Tasa_pct",
    y="Education",
    orientation="h",
    text="Tasa_pct",
    labels={
        "Tasa_pct": "Tasa de compra (%)",
        "Education": "Nivel educativo"
    },
    title="Tasa de compra según nivel educativo"
)

fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig2.update_layout(
    xaxis_range=[0, max(100, edu["Tasa_pct"].max() * 1.15)],
    height=450
)

st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# 6. GRÁFICA 3 — VEHÍCULOS
# ============================================================
st.header("3. Tasa de compra según número de vehículos")

cars = (
    view.groupby("NumberCarsOwned")
    .agg(
        Clientes=("CustomerID", "size"),
        Tasa_compra=("BikeBuyer", "mean"),
        Gasto_medio=("AvgMonthSpend", "mean")
    )
    .reset_index()
)

cars["Tasa_pct"] = cars["Tasa_compra"] * 100

# Evitamos que grupos muy pequeños dominen la lectura
cars = cars[cars["Clientes"] >= 100].sort_values("NumberCarsOwned")

fig3 = px.bar(
    cars,
    x="NumberCarsOwned",
    y="Tasa_pct",
    text="Tasa_pct",
    labels={
        "NumberCarsOwned": "Número de vehículos",
        "Tasa_pct": "Tasa de compra (%)"
    },
    title="¿Cómo cambia la compra según el número de vehículos?"
)

fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig3.update_layout(height=450)

st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# 7. GRÁFICA 4 — HIJOS EN CASA
# ============================================================
st.header("4. Tasa de compra según hijos en el hogar")

children = (
    view.groupby("NumberChildrenAtHome")
    .agg(
        Clientes=("CustomerID", "size"),
        Tasa_compra=("BikeBuyer", "mean"),
        Gasto_medio=("AvgMonthSpend", "mean")
    )
    .reset_index()
)

children["Tasa_pct"] = children["Tasa_compra"] * 100
children = children[children["Clientes"] >= 100]
children = children.sort_values("NumberChildrenAtHome")

fig4 = px.bar(
    children,
    x="NumberChildrenAtHome",
    y="Tasa_pct",
    text="Tasa_pct",
    labels={
        "NumberChildrenAtHome": "Hijos en el hogar",
        "Tasa_pct": "Tasa de compra (%)"
    },
    title="Tasa de compra según hijos en el hogar"
)

fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig4.update_layout(height=450)

st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# 8. GRÁFICA 5 — MAPA DE OPORTUNIDAD
# ============================================================
st.header("5. ⭐ Mapa de oportunidad comercial")

segment = (
    view.groupby("Occupation")
    .agg(
        Clientes=("CustomerID", "size"),
        Tasa_compra=("BikeBuyer", "mean"),
        Gasto_medio=("AvgMonthSpend", "mean")
    )
    .reset_index()
)

segment["Tasa_pct"] = segment["Tasa_compra"] * 100

fig5 = px.scatter(
    segment,
    x="Tasa_pct",
    y="Gasto_medio",
    size="Clientes",
    hover_name="Occupation",
    text="Occupation",
    labels={
        "Tasa_pct": "Tasa de compra (%)",
        "Gasto_medio": "Gasto medio mensual en recambios",
        "Clientes": "Número de clientes"
    },
    title="Mapa de oportunidad: conversión vs. valor económico"
)

fig5.update_traces(
    textposition="top center",
    textfont_size=10
)

fig5.update_layout(height=550)

st.plotly_chart(fig5, use_container_width=True)

st.success(
    "Lectura recomendada: los segmentos ubicados hacia la derecha presentan mayor "
    "tasa de compra y los ubicados hacia arriba mayor gasto medio. El tamaño del punto "
    "representa el volumen de clientes. Esta combinación permite seleccionar hipótesis "
    "para un piloto comercial."
)

# ============================================================
# 9. TABLA DE SEGMENTOS
# ============================================================
st.header("📋 Resumen de segmentos")

segment_table = segment.copy()

segment_table["Tasa de compra"] = segment_table["Tasa_pct"].map(
    lambda x: f"{x:.1f}%"
)

segment_table["Gasto medio"] = segment_table["Gasto_medio"].map(
    lambda x: f"${x:,.2f}"
)

segment_table = segment_table[
    ["Occupation", "Clientes", "Tasa de compra", "Gasto medio"]
].rename(
    columns={
        "Occupation": "Ocupación"
    }
)

st.dataframe(
    segment_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# 10. CONCLUSIÓN EJECUTIVA
# ============================================================
st.header("💡 Lectura ejecutiva")

st.markdown(
    """
**¿Qué aporta este análisis al proyecto?**

1. Permite identificar diferencias de comportamiento entre segmentos.
2. Permite combinar **volumen de clientes + tasa de compra + gasto**.
3. Permite seleccionar segmentos para un **piloto comercial controlado**.
4. Convierte la información existente en indicadores que pueden actualizarse
   automáticamente cuando se cargue una nueva versión del Excel.

> Importante: las diferencias observadas son asociaciones descriptivas. Antes de
> convertirlas en reglas comerciales, AW-Bikes debería validarlas mediante campañas
> piloto y, cuando sea posible, un grupo de control.
"""
)

st.caption(
    "AW-Bikes BI Pilot — Prototipo académico desarrollado con Python, Pandas, Plotly y Streamlit."
)
