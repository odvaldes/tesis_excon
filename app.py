
# -*- coding: utf-8 -*-
"""
NOTEBOOK 4 / APP STREAMLIT
SIAD - Sistema Inteligente de Apoyo a la Decisión
EXCON - Riesgo de inmovilización por SKU

Ejecutar:
    streamlit run Notebook_4_SIAD_Streamlit.py
"""
from pathlib import Path
from io import BytesIO
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="SIAD | EXCON",
    page_icon="📦",
    layout="wide",
)

RUTA_DATOS = Path(r"C:\Modelo IA")
RUTA_SALIDA = RUTA_DATOS / "salidas_modelo"

# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------
def leer_primero_disponible(nombre):
    rutas = [
        RUTA_SALIDA / f"{nombre}.parquet",
        RUTA_SALIDA / f"{nombre}.pkl",
        RUTA_SALIDA / f"{nombre}.xlsx",
    ]
    for ruta in rutas:
        if ruta.exists():
            if ruta.suffix == ".parquet":
                return pd.read_parquet(ruta)
            if ruta.suffix == ".pkl":
                return pd.read_pickle(ruta)
            return pd.read_excel(ruta, engine="openpyxl")
    raise FileNotFoundError(
        f"No se encontró {nombre} en {RUTA_SALIDA}. "
        "Ejecute primero los Notebooks 1, 2 y 3."
    )

def columna_existente(df, candidatos):
    for c in candidatos:
        if c in df.columns:
            return c
    return None

def num(serie):
    return pd.to_numeric(serie, errors="coerce")

def moneda_clp(valor):
    if valor is None or pd.isna(valor):
        return "—"
    return "$" + f"{float(valor):,.0f}".replace(",", ".")

def clasificar_iri_final(iri):
    if pd.isna(iri):
        return "SIN INFORMACIÓN"
    if iri <= 40:
        return "BAJO"
    if iri <= 80:
        return "MEDIO"
    return "ALTO"

def es_vep_critico(valor):
    if pd.isna(valor):
        return False
    texto = str(valor).strip().upper()
    return texto in {"V", "VITAL", "CRITICO", "CRÍTICO", "VEP", "1", "SI", "SÍ"}

def recomendacion_final(fila, col_cobertura=None):
    iri = fila.get("IRI", np.nan)
    vep = fila.get("vep", "NO_CLASIFICADO")
    abc = str(fila.get("abc", "")).upper()
    cobertura = np.nan
    if col_cobertura:
        cobertura = pd.to_numeric(pd.Series([fila.get(col_cobertura)]), errors="coerce").iloc[0]

    if pd.isna(iri):
        return "REVISAR INFORMACIÓN ANTES DE DECIDIR"

    if iri >= 81:
        if es_vep_critico(vep):
            return "REVISIÓN TÉCNICA: VALIDAR STOCK MÍNIMO POR CRITICIDAD VEP"
        if pd.notna(cobertura) and cobertura > 2:
            return "PRIORIZAR REDISTRIBUCIÓN Y REVISAR ANTES DE UNA NUEVA COMPRA"
        return "REVISAR STOCK CORPORATIVO Y JUSTIFICAR NUEVA COMPRA"

    if iri >= 41:
        if es_vep_critico(vep):
            return "REVISAR CON ÁREA TÉCNICA ANTES DE AJUSTAR STOCK"
        if pd.notna(cobertura) and cobertura > 2:
            return "REVISAR STOCK CORPORATIVO Y ALTERNATIVAS DE TRANSFERENCIA"
        if abc == "A":
            return "REVISAR CANTIDAD Y STOCK CORPORATIVO ANTES DE COMPRAR"
        return "REVISAR STOCK Y CANTIDAD SOLICITADA"

    return "CONTINUAR EVALUACIÓN NORMAL DE COMPRA"

def exportar_excel(df):
    salida = BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Priorizacion_SIAD")
    return salida.getvalue()

@st.cache_data(show_spinner=False)
def cargar_datos():
    scoring = leer_primero_disponible("Scoring_Actual_IRI_EXCON")
    try:
        metricas = pd.read_excel(RUTA_SALIDA / "Metricas_Test_EXCON.xlsx")
    except Exception:
        try:
            metricas = pd.read_excel(RUTA_SALIDA / "05_metricas_test.xlsx")
        except Exception:
            metricas = pd.DataFrame()
    try:
        importancia = pd.read_excel(RUTA_SALIDA / "Importancia_Variables_EXCON.xlsx")
    except Exception:
        try:
            importancia = pd.read_excel(RUTA_SALIDA / "06_importancia_variables.xlsx")
        except Exception:
            importancia = pd.DataFrame()
    return scoring, metricas, importancia

# ---------------------------------------------------------------------
# Carga y preparación
# ---------------------------------------------------------------------
try:
    df, metricas, importancia = cargar_datos()
except Exception as e:
    st.error(str(e))
    st.info("Ejecute primero `python SIAD_pipeline.py` o los Notebooks 1, 2 y 3.")
    st.stop()

if "IRI" not in df.columns and "probabilidad_inmovilizacion" in df.columns:
    df["IRI"] = num(df["probabilidad_inmovilizacion"]) * 100

df["IRI"] = num(df["IRI"]).clip(0, 100)
df["nivel_iri_siad"] = df["IRI"].apply(clasificar_iri_final)

col_stock = columna_existente(df, [
    "stock_contable_actual",
    "stock_actual_total",
    "stock_estimado_positivo",
    "stock_estimado",
])
col_valor = columna_existente(df, [
    "valor_stock_contable_actual",
    "valor_stock_actual_total",
    "valor_stock",
])
col_cobertura = columna_existente(df, [
    "cobertura_meses",
    "cobertura_12m",
    "meses_cobertura",
    "cobertura",
])
col_rotacion = columna_existente(df, ["rotacion_12m", "rotacion"])
col_antiguedad = columna_existente(df, [
    "meses_sin_salida",
    "antiguedad_meses",
    "dias_sin_salida",
])
col_consumo = columna_existente(df, [
    "valor_consumo_12m",
    "salida_12m",
    "promedio_salida_12m",
])
col_compras = columna_existente(df, [
    "cantidad_comprada",
    "entrada_12m",
    "entrada_6m",
])
col_transfer = columna_existente(df, [
    "transferencias_12m",
    "cantidad_transferida",
    "numero_transferencias",
])

if col_stock:
    df[col_stock] = num(df[col_stock])
if col_valor:
    df[col_valor] = num(df[col_valor])
if col_cobertura:
    df[col_cobertura] = num(df[col_cobertura])

df["recomendacion_siad"] = df.apply(
    lambda fila: recomendacion_final(fila, col_cobertura),
    axis=1
)

df["candidato_transferencia"] = (
    (df["IRI"] >= 41)
    & ((df[col_stock] > 0) if col_stock else True)
    & ((df[col_cobertura] > 2) if col_cobertura else False)
    & (~df.get("vep", pd.Series("", index=df.index)).apply(es_vep_critico))
)

# ---------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------
st.title("Sistema Inteligente de Apoyo a la Decisión (SIAD)")
st.caption(
    "Gestión predictiva de inventario EXCON · Riesgo de inmovilización por SKU"
)
st.markdown(
    """
El SIAD utiliza información histórica de **consumo, stock, antigüedad, cobertura,
compras y transferencias** para estimar el riesgo de que un material quede
inmovilizado. El modelo entrega una probabilidad por SKU y la transforma en un
**Índice de Riesgo de Inmovilización (IRI)**. La recomendación final incorpora
reglas de negocio y mantiene la decisión en el responsable de abastecimiento.
"""
)

# ---------------------------------------------------------------------
# Filtros
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")
    niveles = st.multiselect(
        "Nivel IRI",
        ["BAJO", "MEDIO", "ALTO"],
        default=["BAJO", "MEDIO", "ALTO"],
    )
    centros = []
    if "centro_costo" in df.columns:
        centros = sorted(df["centro_costo"].dropna().astype(str).unique())
        centros_sel = st.multiselect("Centro de costo", centros)
    else:
        centros_sel = []

    abc_sel = []
    if "abc" in df.columns:
        opciones_abc = sorted(df["abc"].dropna().astype(str).unique())
        abc_sel = st.multiselect("Clasificación ABC", opciones_abc)

    texto_sku = st.text_input("Buscar SKU / descripción")

f = df[df["nivel_iri_siad"].isin(niveles)].copy()
if centros_sel and "centro_costo" in f.columns:
    f = f[f["centro_costo"].astype(str).isin(centros_sel)]
if abc_sel and "abc" in f.columns:
    f = f[f["abc"].astype(str).isin(abc_sel)]
if texto_sku:
    mascara = pd.Series(False, index=f.index)
    if "sku" in f.columns:
        mascara |= f["sku"].astype(str).str.contains(texto_sku, case=False, na=False)
    if "descripcion_producto" in f.columns:
        mascara |= f["descripcion_producto"].astype(str).str.contains(texto_sku, case=False, na=False)
    f = f[mascara]

# ---------------------------------------------------------------------
# KPI principales
# ---------------------------------------------------------------------
sku_total = f["sku"].nunique() if "sku" in f.columns else len(f)
iri_promedio = f["IRI"].mean()
alto = f.loc[f["nivel_iri_siad"] == "ALTO", "sku"].nunique() if "sku" in f.columns else (f["nivel_iri_siad"] == "ALTO").sum()
medio = f.loc[f["nivel_iri_siad"] == "MEDIO", "sku"].nunique() if "sku" in f.columns else (f["nivel_iri_siad"] == "MEDIO").sum()
candidatos = f.loc[f["candidato_transferencia"], "sku"].nunique() if "sku" in f.columns else f["candidato_transferencia"].sum()
valor_stock = f[col_valor].sum() if col_valor else np.nan
valor_riesgo = f.loc[f["nivel_iri_siad"].isin(["MEDIO", "ALTO"]), col_valor].sum() if col_valor else np.nan

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("SKU analizados", f"{sku_total:,.0f}".replace(",", "."))
k2.metric("IRI promedio", f"{iri_promedio:.1f}" if pd.notna(iri_promedio) else "—")
k3.metric("SKU riesgo alto", f"{alto:,.0f}".replace(",", "."))
k4.metric("SKU riesgo medio", f"{medio:,.0f}".replace(",", "."))
k5.metric("Candidatos a transferencia", f"{candidatos:,.0f}".replace(",", "."))
k6.metric("Valor stock analizado", moneda_clp(valor_stock))

if col_valor:
    st.caption(
        f"Valor de stock asociado a riesgo medio/alto: **{moneda_clp(valor_riesgo)}**"
    )

# ---------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Resumen ejecutivo",
    "Priorización de SKU",
    "Análisis del riesgo",
    "Desempeño del modelo",
])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        dist = (
            f.groupby("nivel_iri_siad", as_index=False)
            .agg(SKU=("sku", "nunique") if "sku" in f.columns else ("IRI", "size"))
        )
        orden = ["BAJO", "MEDIO", "ALTO"]
        dist["nivel_iri_siad"] = pd.Categorical(dist["nivel_iri_siad"], orden, ordered=True)
        dist = dist.sort_values("nivel_iri_siad")
        fig = px.bar(
            dist,
            x="nivel_iri_siad",
            y="SKU",
            text_auto=True,
            labels={"nivel_iri_siad": "Nivel IRI"},
            title="SKU por nivel de riesgo",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.histogram(
            f,
            x="IRI",
            nbins=20,
            title="Distribución del Índice de Riesgo de Inmovilización",
            labels={"IRI": "IRI (0–100)"},
        )
        fig.add_vline(x=40, line_dash="dash")
        fig.add_vline(x=80, line_dash="dash")
        st.plotly_chart(fig, use_container_width=True)

    if col_valor:
        top = f.sort_values(["IRI", col_valor], ascending=[False, False]).head(15).copy()
        etiqueta = "sku"
        if "descripcion_producto" in top.columns:
            top["etiqueta"] = top["sku"].astype(str) + " · " + top["descripcion_producto"].astype(str).str.slice(0, 45)
            etiqueta = "etiqueta"
        fig = px.bar(
            top.sort_values("IRI"),
            x="IRI",
            y=etiqueta,
            orientation="h",
            hover_data=[col_valor],
            title="Top 15 materiales por IRI",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    columnas_tabla = [
        c for c in [
            "sku", "descripcion_producto", "centro_costo", "abc", "vep",
            "IRI", "nivel_iri_siad", col_stock, col_valor, col_cobertura,
            col_rotacion, col_antiguedad, col_consumo, col_compras, col_transfer,
            "recomendacion_siad"
        ] if c and c in f.columns
    ]
    tabla = f.sort_values(
        ["IRI"] + ([col_valor] if col_valor else []),
        ascending=[False] + ([False] if col_valor else [])
    )[columnas_tabla]

    st.dataframe(tabla, use_container_width=True, hide_index=True, height=530)
    st.download_button(
        "Descargar priorización SIAD en Excel",
        data=exportar_excel(tabla),
        file_name="SIAD_priorizacion_SKU.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.info(
        "La recomendación es apoyo a la decisión. Un IRI alto no implica por sí solo "
        "reducir stock: la criticidad VEP, la cobertura y la disponibilidad operacional "
        "deben ser revisadas por el responsable de abastecimiento."
    )

with tab3:
    campos = [c for c in [col_cobertura, col_rotacion, col_antiguedad, col_consumo] if c]
    if campos:
        variable = st.selectbox("Variable para contrastar con IRI", campos)
        hover = [c for c in ["sku", "descripcion_producto", "centro_costo", "abc", "vep"] if c in f.columns]
        fig = px.scatter(
            f,
            x=variable,
            y="IRI",
            color="nivel_iri_siad",
            hover_data=hover,
            title=f"IRI versus {variable}",
        )
        fig.add_hline(y=40, line_dash="dash")
        fig.add_hline(y=80, line_dash="dash")
        st.plotly_chart(fig, use_container_width=True)

    if "centro_costo" in f.columns:
        resumen_cc = (
            f.groupby("centro_costo", as_index=False)
            .agg(
                sku=("sku", "nunique") if "sku" in f.columns else ("IRI", "size"),
                iri_promedio=("IRI", "mean"),
                sku_alto=("nivel_iri_siad", lambda x: (x == "ALTO").sum()),
            )
            .sort_values(["sku_alto", "iri_promedio"], ascending=False)
        )
        st.subheader("Riesgo por centro de costo")
        st.dataframe(resumen_cc, use_container_width=True, hide_index=True)

with tab4:
    if metricas.empty:
        st.warning("No se encontró el archivo de métricas del Notebook 3.")
    else:
        st.subheader("Métricas del modelo")
        st.dataframe(metricas, use_container_width=True, hide_index=True)

    if importancia.empty:
        st.warning("No se encontró el archivo de importancia de variables.")
    else:
        var_col = columna_existente(importancia, ["variable", "feature"])
        imp_col = columna_existente(importancia, ["importancia_media", "importancia", "importance"])
        if var_col and imp_col:
            top_imp = importancia.sort_values(imp_col, ascending=False).head(15)
            fig = px.bar(
                top_imp.sort_values(imp_col),
                x=imp_col,
                y=var_col,
                orientation="h",
                title="Variables con mayor importancia predictiva",
            )
            st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(
    "SIAD · EXCON | La predicción estima riesgo de inmovilización por SKU; "
    "las reglas de negocio convierten el riesgo en una recomendación y la decisión final permanece en el profesional."
)
