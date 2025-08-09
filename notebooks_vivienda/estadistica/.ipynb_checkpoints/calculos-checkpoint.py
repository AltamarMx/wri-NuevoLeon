import pandas as pd

def calcular_porcentajes_por_est_socio_m2(original: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula los porcentajes de 'factor_sem' agrupados por 'est_socio' y 'm2'
    respecto al total global de 'factor_sem' en el DataFrame 'vivienda'.

    Parámetros:
    -----------
    original : pd.DataFrame
        DataFrame que contiene al menos las columnas 'est_socio', 'm2' y 'factor_sem'.
    vivienda : pd.DataFrame
        DataFrame que contiene al menos la columna 'factor_sem' para obtener el total global.

    Retorna:
    --------
    pd.DataFrame
        Una tabla con índices en el orden ['Bajo', 'Medio bajo', 'Medio alto', 'Alto'],
        columnas en el orden ['30', '31_55', '56_75', '76_100', '101_150', '151_200', '200_+', 'No sabe'],
        los valores ya redondeados a 1 decimal, y una columna 'Total' que suma cada fila.
    """
    # 1) Agrupar por est_socio y m2, sumar factor_sem y convertir a porcentaje del total global
    pct = (
        original
        .groupby(['est_socio', 'm2'])['factor_sem']
        .sum()
        .div(original['factor_sem'].sum())   # divide entre el total global de 'vivienda'
        .mul(100)                            # convierte a porcentaje
        .unstack('m2')                       # pivotea para tener columnas por cada valor de 'm2'
        .round(1)                            # redondear a 1 decimal
    )

    # 2) Definir el orden de columnas y filas
    m2_order = ['30', '31_55', '56_75', '76_100', '101_150', '151_200', '200_+', 'No sabe']
    est_order = ['Bajo', 'Medio bajo', 'Medio alto', 'Alto']

    # 3) Reindexar para forzar el orden de columnas e índices
    pct = pct.reindex(index=est_order, columns=m2_order)

    # 4) Agregar la columna 'Total' sumando cada fila
    pct['Total'] = pct.sum(axis=1)

    return pct

import pandas as pd

def generar_tabla_porcentajes(
    vivienda: pd.DataFrame,
    devolver_styler: bool = True
) -> pd.DataFrame or pd.io.formats.style.Styler:
    """
    Recibe un DataFrame 'vivienda' con columnas ['clima', 'm2', 'est_socio', 'factor_sem'].
    - Construye un DataFrame pivoteado con los porcentajes de 'factor_sem' por (clima, m2, est_socio),
      ordenado según 'm2' y 'est_socio', y con una columna 'Total'.
    - Si 'devolver_styler=True', también aplica formato y devuelve un Styler; 
      en caso contrario, retorna solo el DataFrame pivotado.

    Parámetros:
    -----------
    vivienda : pd.DataFrame
        Debe contener al menos las columnas 'clima', 'm2', 'est_socio' y 'factor_sem'.
    devolver_styler : bool, opcional (por defecto False)
        Si es True, la función devuelve un `Styler` ya formateado. 
        Si es False, devuelve únicamente el DataFrame con valores numéricos.

    Retorna:
    --------
    pd.DataFrame o pd.io.formats.style.Styler
        - Si devolver_styler=False: el DataFrame con índices ['clima','m2'], columnas de
          las categorías de 'est_socio', más 'Total', redondeado a 2 decimales.
        - Si devolver_styler=True: el mismo DataFrame pero envuelto en un Styler con formato,
          degradado de color por fila y barra en la columna 'Total'.
    """
    # 1) Cálculo de porcentajes en un DataFrame “largo”
    df_largo = (
        vivienda
        .groupby(['clima', 'm2', 'est_socio'])['factor_sem']
        .sum()
        .div(vivienda['factor_sem'].sum())  # divide entre el total global
        .mul(100)                           # convierte a porcentaje
        .reset_index(name='factor_sem')
    )

    # 2) Define orden deseado para 'm2' y 'est_socio'
    m2_order = ['30', '31_55', '56_75', '76_100', '101_150', '151_200', '200_+', 'No sabe']
    est_order = ['Bajo', 'Medio bajo', 'Medio alto', 'Alto']

    # 3) Convierte 'm2' en Categorical para respetar el orden al pivotear
    df_largo['m2'] = pd.Categorical(df_largo['m2'], categories=m2_order, ordered=True)

    # 4) Pivotear manteniendo el orden de columnas en 'est_socio'
    df_pivot = (
        df_largo
        .pivot(index=['clima', 'm2'], columns='est_socio', values='factor_sem')
        .reindex(columns=est_order)
    )

    # 5) Agrega columna 'Total' y redondea valores
    df_pivot['Total'] = df_pivot.sum(axis=1)
    df_pivot = df_pivot.round(2)  # redondeo a 2 decimales

    if not devolver_styler:
        # Devuelvo solo el DataFrame
        return df_pivot

    # 6) Si piden Styler, aplicamos formato y devolvemos el Styler
    styled = (
        df_pivot
        .style
        .format("{:.1f}")
        .background_gradient(axis=0)
        .bar(subset=['Total'], color='#FFA07A')
    )
    return styled

def generar_tabla(
    vivienda: pd.DataFrame,
    devolver_styler: bool = True
) -> pd.DataFrame or pd.io.formats.style.Styler:
    """
    Recibe un DataFrame 'vivienda' con columnas ['clima', 'm2', 'est_socio', 'factor_sem'].
    - Construye un DataFrame pivoteado con los totales de 'factor_sem' por (clima, m2, est_socio),
      ordenado según 'm2' y 'est_socio', y con una columna 'Total'.
    - Si 'devolver_styler=True', también aplica formato y devuelve un Styler; 
      en caso contrario, retorna solo el DataFrame pivotado.

    Parámetros:
    -----------
    vivienda : pd.DataFrame
        Debe contener al menos las columnas 'clima', 'm2', 'est_socio' y 'factor_sem'.
    devolver_styler : bool, opcional (por defecto False)
        Si es True, la función devuelve un `Styler` ya formateado. 
        Si es False, devuelve únicamente el DataFrame con valores numéricos.

    Retorna:
    --------
    pd.DataFrame o pd.io.formats.style.Styler
        - Si devolver_styler=False: el DataFrame con índices ['clima','m2'], columnas de
          las categorías de 'est_socio', más 'Total', redondeado a 2 decimales.
        - Si devolver_styler=True: el mismo DataFrame pero envuelto en un Styler con formato,
          degradado de color por fila y barra en la columna 'Total'.
    """
    # 1) Cálculo de porcentajes en un DataFrame “largo”
    df_largo = (
        vivienda
        .groupby(['clima', 'm2', 'est_socio'])['factor_sem']
        .sum()
        # .div(vivienda['factor_sem'].sum())  # divide entre el total global
        # .mul(100)                           # convierte a porcentaje
        .reset_index(name='factor_sem')
    )

    # 2) Define orden deseado para 'm2' y 'est_socio'
    m2_order = ['30', '31_55', '56_75', '76_100', '101_150', '151_200', '200_+', 'No sabe']
    est_order = ['Bajo', 'Medio bajo', 'Medio alto', 'Alto']

    # 3) Convierte 'm2' en Categorical para respetar el orden al pivotear
    df_largo['m2'] = pd.Categorical(df_largo['m2'], categories=m2_order, ordered=True)

    # 4) Pivotear manteniendo el orden de columnas en 'est_socio'
    df_pivot = (
        df_largo
        .pivot(index=['clima', 'm2'], columns='est_socio', values='factor_sem')
        .reindex(columns=est_order)
    )

    # 5) Agrega columna 'Total' y redondea valores
    df_pivot['Total'] = df_pivot.sum(axis=1)
    # df_pivot = df_pivot.round(2)  # redondeo a 2 decimales

    if not devolver_styler:
        # Devuelvo solo el DataFrame
        return df_pivot

    # 6) Si piden Styler, aplicamos formato y devolvemos el Styler
    styled = (
        df_pivot
        .style
        .format("{:.0f}")
        .background_gradient(axis=0)
        .bar(subset=['Total'], color='#FFA07A')
    )
    return styled

