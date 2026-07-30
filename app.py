

# -*- coding: utf-8 -*-
"""
Dashboard Streamlit - Gestión Predictiva de Inventario EXCON
Notebook 4 / Aplicación Streamlit

Archivos esperados dentro de la carpeta salidas_modelo:
- Dataset_Modelo_EXCON.parquet o .pkl o .xlsx
- Dataset_Scoring_Actual_EXCON.parquet o .pkl o .xlsx
- Comparacion_Modelos_EXCON.xlsx
- Metricas_Test_EXCON.xlsx
- Importancia_Variables_EXCON.xlsx
- Resultados_Test_IRI_EXCON.xlsx
- Scoring_Actual_IRI_EXCON.parquet o .pkl o .xlsx
- Resumen_Notebook_3_EXCON.xlsx
- Reporte_Notebook_2.xlsx
"""

from pathlib import Path
import io
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="EXCON | Gestión Predictiva de Inventario",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(120,120,120,0.08);
        border: 1px solid rgba(120,120,120,0.18);
        padding: 14px;
        border-radius: 12px;
    }
    .small-note {
        font-size: 0.86rem;
        opacity: 0.75;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

RUTA_APP = Path(__file__).resolve().parent
RUTAS_BUSQUEDA = [
    RUTA_APP / "salidas_modelo",
    RUTA_APP / "data",
    RUTA_APP,
]


# ============================================================
# 2. FUNCIONES DE CARGA
# ============================================================

def buscar_archivo(nombre_base: str):
    """
    Busca un archivo con extensiones parquet, pkl o xlsx.
    """
    extensiones = [".parquet", ".pkl", ".xlsx"]

    for carpeta in RUTAS_BUSQUEDA:
        for extension in extensiones:
            ruta = carpeta / f"{nombre_base}{extension}"
            if ruta.exists():
                return ruta

    return None


@st.cache_data(show_spinner=False)
def leer_tabla(ruta_str: str, hoja: str | int | None = None):
    ruta = Path(ruta_str)
    extension = ruta.suffix.lower()

    if extension == ".parquet":
        return pd.read_parquet(ruta)

    if extension == ".pkl":
        return pd.read_pickle(ruta)

    if extension == ".xlsx":
        return pd.read_excel(
            ruta,
            sheet_name=0 if hoja is None else hoja,
            engine="openpyxl",
        )

    raise ValueError(f"Formato no soportado: {extension}")


@st.cache_data(show_spinner=False)
def leer_excel_hoja(ruta_str: str, hoja: str):
    return pd.read_excel(
        ruta_str,
        sheet_name=hoja,
        engine="openpyxl",
    )


def cargar_opcional(nombre_base: str):
    ruta = buscar_archivo(nombre_base)
    if ruta is None:
        return None, None

    try:
        return leer_tabla(str(ruta)), ruta
    except Exception:
        return None, ruta


def primera_columna_existente(df: pd.DataFrame, candidatas: list[str]):
    if df is None:
        return None

    for columna in candidatas:
        if columna in df.columns:
            return columna

    return None


def normalizar_columnas(df: pd.DataFrame | None):
    if df is None:
        return None

    copia = df.copy()
    copia.columns = [
        str(c).strip()
        .lower()
        .replace(" ", "_")
        .replace("°", "o")
        for c in copia.columns
    ]
    return copia


def formato_entero(valor):
    try:
        return f"{int(round(float(valor))):,}".replace(",", ".")
    except Exception:
        return "N/D"


def formato_porcentaje(valor):
    try:
        valor = float(valor)
        if abs(valor) <= 1:
            valor *= 100
        return f"{valor:.2f}%"
    except Exception:
        return "N/D"


def formato_moneda(valor):
    try:
        return "$" + f"{float(valor):,.0f}".replace(",", ".")
    except Exception:
        return "N/D"


def convertir_excel(df: pd.DataFrame):
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")

    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# 3. CARGA DE RESULTADOS NOTEBOOK 2 Y 3
# ============================================================

dataset_modelo, ruta_dataset_modelo = cargar_opcional(
    "Dataset_Modelo_EXCON"
)
dataset_scoring, ruta_dataset_scoring = cargar_opcional(
    "Dataset_Scoring_Actual_EXCON"
)
scoring_iri, ruta_scoring_iri = cargar_opcional(
    "Scoring_Actual_IRI_EXCON"
)
comparacion_modelos, ruta_comparacion = cargar_opcional(
    "Comparacion_Modelos_EXCON"
)
metricas_test, ruta_metricas = cargar_opcional(
    "Metricas_Test_EXCON"
)
importancia_variables, ruta_importancia = cargar_opcional(
    "Importancia_Variables_EXCON"
)
resultados_test, ruta_resultados_test = cargar_opcional(
    "Resultados_Test_IRI_EXCON"
)
resumen_nb3, ruta_resumen_nb3 = cargar_opcional(
    "Resumen_Notebook_3_EXCON"
)

# Reporte del Notebook 2 puede contener varias hojas.
ruta_reporte_nb2 = buscar_archivo("Reporte_Notebook_2")
resumen_nb2 = None
variables_nb2 = None

if ruta_reporte_nb2 is not None and ruta_reporte_nb2.suffix.lower() == ".xlsx":
    try:
        resumen_nb2 = leer_excel_hoja(
            str(ruta_reporte_nb2),
            "Resumen",
        )
    except Exception:
        pass

    try:
        variables_nb2 = leer_excel_hoja(
            str(ruta_reporte_nb2),
            "Variables",
        )
    except Exception:
        pass

dataset_modelo = normalizar_columnas(dataset_modelo)
dataset_scoring = normalizar_columnas(dataset_scoring)
scoring_iri = normalizar_columnas(scoring_iri)
comparacion_modelos = normalizar_columnas(comparacion_modelos)
metricas_test = normalizar_columnas(metricas_test)
importancia_variables = normalizar_columnas(importancia_variables)
resultados_test = normalizar_columnas(resultados_test)
resumen_nb2 = normalizar_columnas(resumen_nb2)
resumen_nb3 = normalizar_columnas(resumen_nb3)


# ============================================================
# 4. ENCABEZADO Y ESTADO DE CARGA
# ============================================================

st.title("Sistema Inteligente de Apoyo a la Decisión")
st.subheader("Gestión predictiva de inventario — EXCON")

st.caption(
    "Dashboard de indicadores, riesgo de inmovilización, "
    "distribución de órdenes y resultados del modelo predictivo."
)

archivos_cargados = {
    "Dataset modelo": ruta_dataset_modelo,
    "Dataset scoring": ruta_dataset_scoring,
    "Scoring IRI": ruta_scoring_iri,
    "Comparación modelos": ruta_comparacion,
    "Métricas test": ruta_metricas,
    "Importancia variables": ruta_importancia,
    "Resultados test": ruta_resultados_test,
    "Resumen Notebook 2": ruta_reporte_nb2,
    "Resumen Notebook 3": ruta_resumen_nb3,
}

with st.sidebar:
    st.header("Estado de datos")

    for nombre, ruta in archivos_cargados.items():
        if ruta is not None:
            st.success(f"{nombre}: cargado")
        else:
            st.warning(f"{nombre}: no encontrado")

    st.divider()
    st.caption(
        "La aplicación busca archivos dentro de "
        "`salidas_modelo/`, `data/` o la carpeta raíz."
    )


# ============================================================
# 5. SELECCIÓN DE BASE PRINCIPAL PARA EL DASHBOARD
# ============================================================

base_dashboard = None
nombre_base_dashboard = None

if scoring_iri is not None and not scoring_iri.empty:
    base_dashboard = scoring_iri.copy()
    nombre_base_dashboard = "Scoring actual con IRI"
elif resultados_test is not None and not resultados_test.empty:
    base_dashboard = resultados_test.copy()
    nombre_base_dashboard = "Resultados test con IRI"
elif dataset_scoring is not None and not dataset_scoring.empty:
    base_dashboard = dataset_scoring.copy()
    nombre_base_dashboard = "Dataset scoring actual"
elif dataset_modelo is not None and not dataset_modelo.empty:
    base_dashboard = dataset_modelo.copy()
    nombre_base_dashboard = "Dataset de entrenamiento"

if base_dashboard is None:
    st.error(
        "No fue posible cargar una base para el dashboard. "
        "Sube los archivos generados por los Notebooks 2 y 3 "
        "a la carpeta `salidas_modelo` del repositorio."
    )
    st.stop()

st.sidebar.info(f"Base activa: {nombre_base_dashboard}")


# ============================================================
# 6. IDENTIFICACIÓN FLEXIBLE DE COLUMNAS
# ============================================================

col_iri = primera_columna_existente(
    base_dashboard,
    ["iri"],
)
col_nivel_iri = primera_columna_existente(
    base_dashboard,
    ["nivel_iri"],
)
col_objetivo = primera_columna_existente(
    base_dashboard,
    ["inmovilizado", "prediccion"],
)
col_sku = primera_columna_existente(
    base_dashboard,
    ["sku", "no_producto", "n_producto"],
)
col_centro = primera_columna_existente(
    base_dashboard,
    ["centro_costo", "centro_costo_final"],
)
col_grupo = primera_columna_existente(
    base_dashboard,
    ["grupo_inventario", "categoria_producto"],
)
col_abc = primera_columna_existente(
    base_dashboard,
    ["abc"],
)
col_stock = primera_columna_existente(
    base_dashboard,
    [
        "stock_contable_actual",
        "stock_actual_total",
        "stock_estimado_positivo",
        "stock_estimado",
    ],
)
col_valor = primera_columna_existente(
    base_dashboard,
    [
        "valor_stock_contable_actual",
        "valor_stock_actual_total",
        "valor_linea_compra",
        "valor_consumo_12m",
        "valor_movimiento_mes",
    ],
)
col_orden = primera_columna_existente(
    base_dashboard,
    [
        "id_union",
        "id_pedido_original",
        "numero_pedido",
        "pedido_key",
    ],
)
col_cantidad = primera_columna_existente(
    base_dashboard,
    [
        "cantidad_comprada",
        "stock_actual_total",
        "stock_estimado_positivo",
        "salida_12m",
    ],
)
col_fecha = primera_columna_existente(
    base_dashboard,
    ["mes", "fecha_compra", "fecha_emision_pedido"],
)
col_descripcion = primera_columna_existente(
    base_dashboard,
    [
        "descripcion_producto",
        "descripcion_linea",
        "descripcion_inventario",
    ],
)


# ============================================================
# 7. FILTROS
# ============================================================

st.sidebar.header("Filtros")

base_filtrada = base_dashboard.copy()

if col_centro is not None:
    opciones = sorted(
        base_filtrada[col_centro]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    seleccion = st.sidebar.multiselect(
        "Centro de costo",
        opciones,
    )

    if seleccion:
        base_filtrada = base_filtrada[
            base_filtrada[col_centro].astype(str).isin(seleccion)
        ]

if col_grupo is not None:
    opciones = sorted(
        base_filtrada[col_grupo]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    seleccion = st.sidebar.multiselect(
        "Grupo o categoría",
        opciones,
    )

    if seleccion:
        base_filtrada = base_filtrada[
            base_filtrada[col_grupo].astype(str).isin(seleccion)
        ]

if col_abc is not None:
    opciones = sorted(
        base_filtrada[col_abc]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    seleccion = st.sidebar.multiselect(
        "Clasificación ABC",
        opciones,
    )

    if seleccion:
        base_filtrada = base_filtrada[
            base_filtrada[col_abc].astype(str).isin(seleccion)
        ]

if col_nivel_iri is not None:
    orden_niveles = [
        "MUY BAJO",
        "BAJO",
        "MEDIO",
        "ALTO",
        "MUY ALTO",
    ]

    existentes = (
        base_filtrada[col_nivel_iri]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    opciones = [
        nivel for nivel in orden_niveles
        if nivel in existentes
    ]

    seleccion = st.sidebar.multiselect(
        "Nivel IRI",
        opciones,
    )

    if seleccion:
        base_filtrada = base_filtrada[
            base_filtrada[col_nivel_iri].astype(str).isin(seleccion)
        ]

if col_iri is not None and base_filtrada[col_iri].notna().any():
    min_iri = float(
        pd.to_numeric(
            base_filtrada[col_iri],
            errors="coerce",
        ).min()
    )
    max_iri = float(
        pd.to_numeric(
            base_filtrada[col_iri],
            errors="coerce",
        ).max()
    )

    rango_iri = st.sidebar.slider(
        "Rango IRI",
        min_value=float(math.floor(min_iri)),
        max_value=float(math.ceil(max_iri)),
        value=(
            float(math.floor(min_iri)),
            float(math.ceil(max_iri)),
        ),
    )

    base_filtrada = base_filtrada[
        pd.to_numeric(
            base_filtrada[col_iri],
            errors="coerce",
        ).between(
            rango_iri[0],
            rango_iri[1],
        )
    ]


# ============================================================
# 8. INDICADORES PRINCIPALES
# ============================================================

st.markdown("### Indicadores principales")

total_registros = len(base_filtrada)
total_sku = (
    base_filtrada[col_sku].nunique()
    if col_sku is not None
    else np.nan
)
total_ordenes = (
    base_filtrada[col_orden].nunique()
    if col_orden is not None
    else total_registros
)

if col_objetivo is not None:
    objetivo_num = pd.to_numeric(
        base_filtrada[col_objetivo],
        errors="coerce",
    )
    total_inmovilizadas = int(
        objetivo_num.fillna(0).eq(1).sum()
    )
    tasa_inmovilizacion = (
        objetivo_num.mean()
        if objetivo_num.notna().any()
        else np.nan
    )
elif col_iri is not None:
    iri_num = pd.to_numeric(
        base_filtrada[col_iri],
        errors="coerce",
    )
    total_inmovilizadas = int(
        iri_num.ge(60).sum()
    )
    tasa_inmovilizacion = (
        iri_num.ge(60).mean()
        if iri_num.notna().any()
        else np.nan
    )
else:
    total_inmovilizadas = np.nan
    tasa_inmovilizacion = np.nan

iri_promedio = (
    pd.to_numeric(
        base_filtrada[col_iri],
        errors="coerce",
    ).mean()
    if col_iri is not None
    else np.nan
)

valor_en_riesgo = (
    pd.to_numeric(
        base_filtrada[col_valor],
        errors="coerce",
    ).fillna(0).sum()
    if col_valor is not None
    else np.nan
)

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Registros", formato_entero(total_registros))
c2.metric("SKU únicos", formato_entero(total_sku))
c3.metric("Órdenes", formato_entero(total_ordenes))
c4.metric("Inmovilizadas / riesgo alto", formato_entero(total_inmovilizadas))
c5.metric("Tasa de inmovilización", formato_porcentaje(tasa_inmovilizacion))
c6.metric("IRI promedio", f"{iri_promedio:.2f}" if pd.notna(iri_promedio) else "N/D")

if pd.notna(valor_en_riesgo):
    st.metric(
        "Valor asociado a la selección",
        formato_moneda(valor_en_riesgo),
    )


# ============================================================
# 9. HISTOGRAMA Y BOXPLOT DE ÓRDENES INMOVILIZADAS
# ============================================================

st.markdown("### Distribución de órdenes inmovilizadas")

if col_objetivo is not None:
    inmovilizadas = base_filtrada[
        pd.to_numeric(
            base_filtrada[col_objetivo],
            errors="coerce",
        ).eq(1)
    ].copy()
elif col_iri is not None:
    inmovilizadas = base_filtrada[
        pd.to_numeric(
            base_filtrada[col_iri],
            errors="coerce",
        ).ge(60)
    ].copy()
else:
    inmovilizadas = base_filtrada.copy()

variable_histograma = None

for candidata in [
    col_valor,
    col_cantidad,
    col_iri,
]:
    if candidata is not None:
        valores = pd.to_numeric(
            inmovilizadas[candidata],
            errors="coerce",
        )
        if valores.notna().sum() > 0:
            variable_histograma = candidata
            inmovilizadas[candidata] = valores
            break

if variable_histograma is None:
    st.warning(
        "No existe una variable numérica disponible para construir "
        "el histograma y el boxplot."
    )
else:
    etiqueta_variable = variable_histograma.replace("_", " ").title()

    col_grafico_1, col_grafico_2 = st.columns(2)

    with col_grafico_1:
        fig_hist = px.histogram(
            inmovilizadas,
            x=variable_histograma,
            nbins=40,
            marginal="rug",
            title=f"Histograma: {etiqueta_variable}",
            labels={
                variable_histograma: etiqueta_variable,
            },
        )

        fig_hist.update_layout(
            yaxis_title="Frecuencia",
            xaxis_title=etiqueta_variable,
            bargap=0.04,
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True,
        )

    with col_grafico_2:
        color_box = col_nivel_iri if col_nivel_iri is not None else None

        fig_box = px.box(
            inmovilizadas,
            y=variable_histograma,
            color=color_box,
            points="outliers",
            title=f"Boxplot: {etiqueta_variable}",
            labels={
                variable_histograma: etiqueta_variable,
            },
        )

        fig_box.update_layout(
            yaxis_title=etiqueta_variable,
            xaxis_title="",
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True,
        )


# ============================================================
# 10. DISTRIBUCIÓN DEL IRI Y RIESGO
# ============================================================

st.markdown("### Perfil de riesgo")

col_riesgo_1, col_riesgo_2 = st.columns(2)

with col_riesgo_1:
    if col_nivel_iri is not None:
        conteo_nivel = (
            base_filtrada[col_nivel_iri]
            .astype(str)
            .value_counts()
            .rename_axis("Nivel IRI")
            .reset_index(name="Cantidad")
        )

        fig_nivel = px.bar(
            conteo_nivel,
            x="Nivel IRI",
            y="Cantidad",
            text="Cantidad",
            title="Distribución por nivel IRI",
        )

        st.plotly_chart(
            fig_nivel,
            use_container_width=True,
        )
    elif col_iri is not None:
        fig_iri = px.histogram(
            base_filtrada,
            x=col_iri,
            nbins=30,
            title="Distribución del IRI",
        )

        st.plotly_chart(
            fig_iri,
            use_container_width=True,
        )
    else:
        st.info("No se encontró información de IRI.")

with col_riesgo_2:
    if col_abc is not None and col_iri is not None:
        resumen_abc = (
            base_filtrada
            .groupby(col_abc, as_index=False)
            .agg(
                IRI_promedio=(col_iri, "mean"),
                registros=(col_iri, "size"),
            )
        )

        fig_abc = px.bar(
            resumen_abc,
            x=col_abc,
            y="IRI_promedio",
            text_auto=".1f",
            title="IRI promedio por clasificación ABC",
        )

        st.plotly_chart(
            fig_abc,
            use_container_width=True,
        )
    elif col_centro is not None and col_iri is not None:
        resumen_centro = (
            base_filtrada
            .groupby(col_centro, as_index=False)
            .agg(
                IRI_promedio=(col_iri, "mean"),
                registros=(col_iri, "size"),
            )
            .sort_values(
                "IRI_promedio",
                ascending=False,
            )
            .head(15)
        )

        fig_centro = px.bar(
            resumen_centro,
            x=col_centro,
            y="IRI_promedio",
            text_auto=".1f",
            title="Centros de costo con mayor IRI promedio",
        )

        st.plotly_chart(
            fig_centro,
            use_container_width=True,
        )
    else:
        st.info("No se encontraron variables suficientes para este gráfico.")


# ============================================================
# 11. INDICADORES NOTEBOOK 2
# ============================================================

st.markdown("### Resultados del Notebook 2")

if resumen_nb2 is not None and not resumen_nb2.empty:
    st.dataframe(
        resumen_nb2,
        use_container_width=True,
        hide_index=True,
    )
else:
    indicadores_nb2 = []

    if dataset_modelo is not None:
        indicadores_nb2.extend([
            {
                "Indicador": "Filas dataset de entrenamiento",
                "Valor": len(dataset_modelo),
            },
            {
                "Indicador": "Número de variables",
                "Valor": len(dataset_modelo.columns),
            },
            {
                "Indicador": "SKU únicos",
                "Valor": (
                    dataset_modelo["sku"].nunique()
                    if "sku" in dataset_modelo.columns
                    else np.nan
                ),
            },
            {
                "Indicador": "Centros de costo",
                "Valor": (
                    dataset_modelo["centro_costo"].nunique()
                    if "centro_costo" in dataset_modelo.columns
                    else np.nan
                ),
            },
            {
                "Indicador": "Tasa de inmovilización",
                "Valor": (
                    dataset_modelo["inmovilizado"].mean()
                    if "inmovilizado" in dataset_modelo.columns
                    else np.nan
                ),
            },
        ])

    if indicadores_nb2:
        st.dataframe(
            pd.DataFrame(indicadores_nb2),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No se encontraron resultados del Notebook 2.")


# ============================================================
# 12. RESULTADOS DEL NOTEBOOK 3
# ============================================================

st.markdown("### Resultados del Notebook 3")

if metricas_test is not None and not metricas_test.empty:
    fila_metrica = metricas_test.iloc[0]

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    m1.metric(
        "ROC-AUC",
        f"{fila_metrica.get('roc_auc', np.nan):.3f}"
        if pd.notna(fila_metrica.get("roc_auc"))
        else "N/D",
    )
    m2.metric(
        "PR-AUC",
        f"{fila_metrica.get('pr_auc', np.nan):.3f}"
        if pd.notna(fila_metrica.get("pr_auc"))
        else "N/D",
    )
    m3.metric(
        "Precisión",
        f"{fila_metrica.get('precision', np.nan):.3f}"
        if pd.notna(fila_metrica.get("precision"))
        else "N/D",
    )
    m4.metric(
        "Recall",
        f"{fila_metrica.get('recall', np.nan):.3f}"
        if pd.notna(fila_metrica.get("recall"))
        else "N/D",
    )
    m5.metric(
        "F1",
        f"{fila_metrica.get('f1', np.nan):.3f}"
        if pd.notna(fila_metrica.get("f1"))
        else "N/D",
    )
    m6.metric(
        "F2",
        f"{fila_metrica.get('f2', np.nan):.3f}"
        if pd.notna(fila_metrica.get("f2"))
        else "N/D",
    )
else:
    st.info("No se encontró `Metricas_Test_EXCON.xlsx`.")

tab_modelos, tab_importancia, tab_matriz = st.tabs([
    "Comparación de modelos",
    "Importancia de variables",
    "Matriz de confusión",
])

with tab_modelos:
    if comparacion_modelos is not None and not comparacion_modelos.empty:
        columnas_grafico = [
            columna
            for columna in [
                "modelo",
                "roc_auc",
                "pr_auc",
                "precision",
                "recall",
                "f1",
                "f2",
            ]
            if columna in comparacion_modelos.columns
        ]

        st.dataframe(
            comparacion_modelos[columnas_grafico],
            use_container_width=True,
            hide_index=True,
        )

        metricas_largas = comparacion_modelos[
            columnas_grafico
        ].melt(
            id_vars=["modelo"],
            var_name="Métrica",
            value_name="Valor",
        )

        fig_modelos = px.bar(
            metricas_largas,
            x="modelo",
            y="Valor",
            color="Métrica",
            barmode="group",
            title="Comparación de modelos predictivos",
        )

        st.plotly_chart(
            fig_modelos,
            use_container_width=True,
        )
    else:
        st.info("No se encontró la comparación de modelos.")

with tab_importancia:
    if importancia_variables is not None and not importancia_variables.empty:
        columna_importancia = primera_columna_existente(
            importancia_variables,
            ["importancia_media", "importancia"],
        )
        columna_variable = primera_columna_existente(
            importancia_variables,
            ["variable"],
        )

        if columna_importancia and columna_variable:
            top_importancia = (
                importancia_variables
                .sort_values(
                    columna_importancia,
                    ascending=False,
                )
                .head(15)
                .sort_values(
                    columna_importancia,
                    ascending=True,
                )
            )

            fig_importancia = px.bar(
                top_importancia,
                x=columna_importancia,
                y=columna_variable,
                orientation="h",
                title="15 variables más relevantes",
            )

            st.plotly_chart(
                fig_importancia,
                use_container_width=True,
            )

            st.dataframe(
                importancia_variables.head(30),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("El archivo de importancia no tiene las columnas esperadas.")
    else:
        st.info("No se encontró el archivo de importancia de variables.")

with tab_matriz:
    if metricas_test is not None and not metricas_test.empty:
        fila = metricas_test.iloc[0]

        matriz = np.array([
            [
                fila.get("verdaderos_negativos", 0),
                fila.get("falsos_positivos", 0),
            ],
            [
                fila.get("falsos_negativos", 0),
                fila.get("verdaderos_positivos", 0),
            ],
        ])

        fig_matriz = go.Figure(
            data=go.Heatmap(
                z=matriz,
                x=[
                    "Predicho: No inmovilizado",
                    "Predicho: Inmovilizado",
                ],
                y=[
                    "Real: No inmovilizado",
                    "Real: Inmovilizado",
                ],
                text=matriz,
                texttemplate="%{text}",
                showscale=False,
            )
        )

        fig_matriz.update_layout(
            title="Matriz de confusión",
            xaxis_title="Predicción",
            yaxis_title="Clase real",
        )

        st.plotly_chart(
            fig_matriz,
            use_container_width=True,
        )
    else:
        st.info("No existen métricas para construir la matriz.")


# ============================================================
# 13. TABLA DE ÓRDENES / SKU PRIORIZADOS
# ============================================================

st.markdown("### Priorización de órdenes y materiales")

columnas_tabla = [
    columna
    for columna in [
        col_orden,
        col_sku,
        col_descripcion,
        col_centro,
        col_grupo,
        col_abc,
        col_stock,
        col_valor,
        col_iri,
        col_nivel_iri,
        "recomendacion",
    ]
    if columna is not None
    and columna in base_filtrada.columns
]

if columnas_tabla:
    tabla_priorizada = base_filtrada[columnas_tabla].copy()

    if col_iri is not None:
        tabla_priorizada = tabla_priorizada.sort_values(
            col_iri,
            ascending=False,
        )

    st.dataframe(
        tabla_priorizada.head(5000),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Descargar selección en Excel",
        data=convertir_excel(tabla_priorizada),
        file_name="priorizacion_inventario_excon.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
else:
    st.info("No existen columnas suficientes para construir la tabla.")


# ============================================================
# 14. NOTAS METODOLÓGICAS
# ============================================================

with st.expander("Notas metodológicas"):
    st.markdown(
        """
        - La unidad de análisis del modelo es **SKU–centro de costo–mes**.
        - El IRI corresponde a la probabilidad calibrada de inmovilización,
          expresada entre 0 y 100.
        - Las categorías propuestas son: Muy Bajo, Bajo, Medio, Alto y Muy Alto.
        - La clasificación VEP debe validarse con las áreas de Maquinaria,
          Operaciones y Logística.
        - Las recomendaciones son señales de apoyo a la decisión y no sustituyen
          la validación técnica de materiales críticos.
        """
    )
