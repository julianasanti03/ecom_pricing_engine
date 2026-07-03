# ============================================================
# CONCILIADOR DE SKUs
# Hace el full outer join entre lista anterior y lista actual
# Traduce la lógica de conciliarSKUs() de Apps Script
# ============================================================

import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from sku_normalizer import norm_sku, is_valid_sku


def conciliar_skus(df_anterior: pd.DataFrame, df_actual: pd.DataFrame) -> dict:
    """
    Compara dos listas de precios y clasifica cada SKU.

    df_anterior: DataFrame con columnas [sku_pim, costo_neto] del mes pasado
    df_actual:   DataFrame con columnas [sku_pim, costo_neto] del mes actual

    Regresa un dict con 4 categorías:
    {
        'semaforo':         SKUs en ambas listas → van al semáforo final
        'solo_anterior':    SKUs que desaparecieron → SOLO_LISTA_ANTERIOR
        'solo_actual':      SKUs nuevos → SOLO_LISTA_NUEVA
        'sin_precio_nuevo': SKUs en anterior sin actualización → precio anterior se repite
    }
    """

    # Construir índices en memoria (como los Sets de Apps Script)
    map_anterior = dict(zip(df_anterior['sku_pim'], df_anterior['costo_neto']))
    map_actual   = dict(zip(df_actual['sku_pim'],   df_actual['costo_neto']))

    set_anterior = set(map_anterior.keys())
    set_actual   = set(map_actual.keys())

    # Categorías
    semaforo       = []
    solo_anterior  = []
    solo_actual    = []

    # SKUs en AMBAS listas → semáforo
    en_ambas = set_anterior & set_actual
    for sku in en_ambas:
        costo_ant = map_anterior[sku]
        costo_act = map_actual[sku]
        semaforo.append({
            'sku_pim':        sku,
            'costo_anterior': costo_ant,
            'costo_actual':   costo_act
        })

    # SKUs SOLO en anterior → desaparecieron
    for sku in set_anterior - set_actual:
        solo_anterior.append({
            'sku_pim':        sku,
            'costo_anterior': map_anterior[sku],
            'costo_actual':   None
        })

    # SKUs SOLO en actual → nuevos
    for sku in set_actual - set_anterior:
        solo_actual.append({
            'sku_pim':      sku,
            'costo_actual': map_actual[sku]
        })

    # Convertir a DataFrames
    df_semaforo      = pd.DataFrame(semaforo)
    df_solo_anterior = pd.DataFrame(solo_anterior)
    df_solo_actual   = pd.DataFrame(solo_actual)

    # Calcular variaciones en el semáforo
    if not df_semaforo.empty:
        df_semaforo = calcular_variaciones(df_semaforo)

    # Log de resultados
    print(f"\n📊 Resultado de conciliación:")
    print(f"   En ambas listas (semáforo): {len(df_semaforo)}")
    print(f"   Solo en lista anterior:     {len(df_solo_anterior)}")
    print(f"   Solo en lista actual:       {len(df_solo_actual)}")
    print(f"   Total SKUs únicos:          {len(set_anterior | set_actual)}")

    return {
        'semaforo':      df_semaforo,
        'solo_anterior': df_solo_anterior,
        'solo_actual':   df_solo_actual
    }


def calcular_variaciones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula variación nominal, porcentual y estado de costo.
    Solo se aplica a SKUs que están en ambas listas.
    """
    df = df.copy()

    # Variación nominal: cuántos pesos subió o bajó
    df['variacion_nominal'] = df['costo_actual'] - df['costo_anterior']

    # Variación porcentual: qué % cambió
    df['variacion_porcentual'] = (
        (df['costo_actual'] / df['costo_anterior']) - 1
    ) * 100
    df['variacion_porcentual'] = df['variacion_porcentual'].round(4)

    # Estado: SUBIO, BAJO o IGUAL
    def estado(row):
        if row['variacion_nominal'] > 0:
            return 'SUBIO'
        elif row['variacion_nominal'] < 0:
            return 'BAJO'
        else:
            return 'IGUAL'

    df['estado_costo'] = df.apply(estado, axis=1)

    return df


def cruzar_con_publicaciones(
    df_semaforo: pd.DataFrame,
    df_publicaciones: pd.DataFrame
) -> dict:
    """
    Cruza el semáforo contra publicaciones activas del marketplace.
    Solo pasan al output final los SKUs que están publicados (ACTIVO).

    df_publicaciones: DataFrame con columna sku_pim_normalizado
    """
    if df_semaforo.empty:
        return {'encontrados': pd.DataFrame(), 'no_en_reporte': pd.DataFrame()}

    skus_publicados = set(df_publicaciones['sku_pim_normalizado'].dropna().unique())

    mask = df_semaforo['sku_pim'].isin(skus_publicados)

    df_encontrados    = df_semaforo[mask].copy()
    df_no_en_reporte  = df_semaforo[~mask].copy()

    df_encontrados['encontrado_en_publicaciones'] = True

    print(f"\n🔀 Cruce con publicaciones:")
    print(f"   Encontrados en marketplace: {len(df_encontrados)}")
    print(f"   No encontrados en reporte:  {len(df_no_en_reporte)}")

    return {
        'encontrados':   df_encontrados,
        'no_en_reporte': df_no_en_reporte
    }