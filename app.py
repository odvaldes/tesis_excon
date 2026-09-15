el modelo."
    )


# ============================================================
# 15. TABLA DE ÓRDENES / SKU PRIORIZADOS
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
# 16. NOTAS METODOLÓGICAS
# ============================================================

with st.expander("Notas metodológicas"):
    st.markdown(
        """
        - La unidad de análisis del modelo es **SKU–centro de costo–mes**.
        - La **cobertura** se toma del scoring cuando está disponible; en caso contrario,
          se recupera desde `Dataset_Scoring_Actual_EXCON` del Notebook 2 mediante
          **SKU + centro de costo**. Si Notebook 2 contiene stock y consumo promedio
          mensual de 12 meses, se calcula como **Stock / consumo promedio mensual 12m**.
        - El IRI corresponde a la probabilidad calibrada de inmovilización,
          expresada entre 0 y 100.
        - Las categorías propuestas son: Muy Bajo, Bajo, Medio, Alto y Muy Alto.
        - La clasificación VEP debe validarse con las áreas de Maquinaria,
          Operaciones y Logística.
        - Las recomendaciones son señales de apoyo a la decisión y no sustituyen
          la validación técnica de materiales críticos.
        """
    )
