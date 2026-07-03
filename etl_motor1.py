# ============================================================
# ETL MOTOR 1 - ORQUESTADOR PRINCIPAL
# Equivalente a ETL1_Run_All() en Apps Script
# Corre los 4 pasos del pipeline en orden
# ============================================================

import sys
import os
from datetime import date

sys.path.append('src/ingestion')
sys.path.append('src/transform')
sys.path.append('src/output')
sys.path.append('src/utils')

from file_reader import read_csv, clean_dataframe, validate_file_prefix
from price_rules import apply_price_rules
from conciliador import conciliar_skus, cruzar_con_publicaciones
from semaforo_writer import (
    crear_corrida,
    guardar_costos_historico,
    guardar_semaforo,
    guardar_diagnostico,
    cerrar_corrida
)
from db import get_connection


def get_reglas_proveedor(prefijo: str) -> dict:
    """Lee las reglas del proveedor desde reglas_proveedores."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_proveedor, nombre_proveedor, prefijo, descuento,
               tipo_aplicacion, aplica_tipo_cambio, tipo_cambio_fijo,
               remover_espacios
        FROM reglas_proveedores
        WHERE UPPER(prefijo) = UPPER(%s)
    """, (prefijo,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise ValueError(f"No se encontró proveedor con prefijo '{prefijo}'")

    return {
        'id_proveedor':       row[0],
        'nombre_proveedor':   row[1],
        'prefijo':            row[2],
        'descuento':          float(row[3]),
        'tipo_aplicacion':    row[4],
        'aplica_tipo_cambio': row[5],
        'tipo_cambio_fijo':   float(row[6]) if row[6] else 1.0,
        'remover_espacios':   row[7]
    }


def get_publicaciones(id_canal: int):
    """Lee publicaciones activas del canal desde la BD."""
    import pandas as pd
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sku_pim_normalizado
        FROM publicaciones_marketplace
        WHERE id_canal = %s AND status_publicacion = 'ACTIVO'
    """, (id_canal,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(rows, columns=['sku_pim_normalizado'])


def run_etl(
    archivo_anterior: str,
    archivo_actual: str,
    mes_pasado: date,
    mes_actual: date,
    id_canal: int
):
    """
    Orquesta el pipeline completo del Motor 1.

    archivo_anterior: ruta al CSV del mes pasado  (ej: input/ZF_2026_04.csv)
    archivo_actual:   ruta al CSV del mes actual   (ej: input/ZF_2026_05.csv)
    mes_pasado:       date del mes anterior
    mes_actual:       date del mes actual
    id_canal:         canal de marketplace a cruzar
    """

    print("=" * 60)
    print("🚀 MOTOR 1 - SEMÁFORO DE PRECIOS")
    print("=" * 60)

    id_corrida = None

    try:
        # --------------------------------------------------
        # PASO 1: Leer reglas del proveedor desde BD
        # --------------------------------------------------
        print("\n📋 PASO 1: Leyendo reglas del proveedor...")
        prefijo = os.path.basename(archivo_actual).split('_')[0].upper()
        reglas = get_reglas_proveedor(prefijo)
        sku_mode = 'NOSPACES' if reglas['remover_espacios'] else 'KEEP'

        print(f"   Proveedor: {reglas['nombre_proveedor']}")
        print(f"   Tipo aplicación: {reglas['tipo_aplicacion']}")
        print(f"   Aplica TC: {reglas['aplica_tipo_cambio']}")

        # --------------------------------------------------
        # PASO 2: Leer y normalizar archivos
        # --------------------------------------------------
        print("\n🧹 PASO 2: Normalizando archivos...")

        df_ant_raw = read_csv(archivo_anterior)
        df_act_raw = read_csv(archivo_actual)

        df_anterior = clean_dataframe(df_ant_raw.copy(), sku_mode, reglas['prefijo'])
        df_actual   = clean_dataframe(df_act_raw.copy(), sku_mode, reglas['prefijo'])

        # Aplicar reglas de precio
        df_anterior['costo_neto'] = df_anterior['costo_neto'].apply(
            lambda p: apply_price_rules(p, reglas)
        )
        df_actual['costo_neto'] = df_actual['costo_neto'].apply(
            lambda p: apply_price_rules(p, reglas)
        )

        # Registrar corrida en BD
        id_corrida = crear_corrida(
            reglas['id_proveedor'], mes_pasado, mes_actual
        )

        # Guardar costos históricos del mes actual
        guardar_costos_historico(
            df_actual, id_corrida,
            reglas['id_proveedor'], mes_actual
        )

        # --------------------------------------------------
        # PASO 3: Cruce con publicaciones
        # --------------------------------------------------
        print("\n🔀 PASO 3: Cruzando con publicaciones del marketplace...")
        df_publicaciones = get_publicaciones(id_canal)
        print(f"   Publicaciones activas en canal {id_canal}: {len(df_publicaciones)}")

        # --------------------------------------------------
        # PASO 4: Conciliación y semáforo
        # --------------------------------------------------
        print("\n📊 PASO 4: Conciliando SKUs y generando semáforo...")
        resultado = conciliar_skus(df_anterior, df_actual)
        cruce = cruzar_con_publicaciones(
            resultado['semaforo'], df_publicaciones
        )

        # Guardar semáforo final
        guardar_semaforo(
            cruce['encontrados'],
            id_corrida,
            reglas['id_proveedor'],
            id_canal
        )

        # Guardar diagnósticos
        guardar_diagnostico(
            resultado['solo_anterior'],
            'SOLO_LISTA_ANTERIOR',
            id_corrida, reglas['id_proveedor']
        )
        guardar_diagnostico(
            resultado['solo_actual'],
            'SOLO_LISTA_NUEVA',
            id_corrida, reglas['id_proveedor']
        )
        guardar_diagnostico(
            cruce['no_en_reporte'],
            'SOLO_EN_REPORTE',
            id_corrida, reglas['id_proveedor']
        )

        # Cerrar corrida exitosa
        total = len(df_actual)
        cerrar_corrida(id_corrida, total, exitoso=True)

        print("\n" + "=" * 60)
        print("✅ MOTOR 1 COMPLETADO EXITOSAMENTE")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if id_corrida:
            cerrar_corrida(id_corrida, 0, exitoso=False)
        raise


if __name__ == "__main__":
    # Configuración de prueba
    run_etl(
        archivo_anterior='input/ZF_2026_04.csv',
        archivo_actual='input/ZF_2026_05.csv',
        mes_pasado=date(2026, 4, 1),
        mes_actual=date(2026, 5, 1),
        id_canal=1
    )