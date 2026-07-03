# ============================================================
# ESCRITOR DEL SEMÁFORO FINAL
# Inserta los resultados del conciliador en PostgreSQL
# ============================================================

import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from db import get_connection
from datetime import date


def crear_corrida(id_proveedor: int, mes_pasado: date, mes_actual: date) -> int:
    """
    Registra el inicio de una corrida en historial_corridas.
    Calcula automáticamente la version_corrida para ese proveedor+mes.
    Regresa el id_corrida generado.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ¿Cuántas corridas existen ya para este proveedor+mes?
        cursor.execute("""
            SELECT COALESCE(MAX(version_corrida), 0) + 1
            FROM historial_corridas
            WHERE mes_actual = %s AND id_proveedor = %s
        """, (mes_actual, id_proveedor))

        version = cursor.fetchone()[0]

        # Insertar nueva corrida
        cursor.execute("""
            INSERT INTO historial_corridas 
                (mes_pasado, mes_actual, id_proveedor, version_corrida, estado_ejecucion)
            VALUES (%s, %s, %s, %s, 'INICIADO')
            RETURNING id_corrida
        """, (mes_pasado, mes_actual, id_proveedor, version))

        id_corrida = cursor.fetchone()[0]
        conn.commit()

        print(f"🚀 Corrida iniciada: id={id_corrida} | versión={version}")
        return id_corrida

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def guardar_costos_historico(
    df: pd.DataFrame,
    id_corrida: int,
    id_proveedor: int,
    mes_reportado: date
) -> int:
    """
    Inserta los costos normalizados en costos_proveedores_historico.
    Regresa cuántos registros se insertaron.
    """
    if df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    try:
        registros = [
            (id_corrida, id_proveedor, row['sku_pim'],
             float(row['costo_neto']), mes_reportado)
            for _, row in df.iterrows()
        ]

        cursor.executemany("""
            INSERT INTO costos_proveedores_historico
                (id_corrida, id_proveedor, sku_pim, costo_neto, mes_reportado)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, registros)

        conn.commit()
        total = cursor.rowcount
        print(f"💾 Costos históricos guardados: {total} registros")
        return total

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def guardar_semaforo(
    df: pd.DataFrame,
    id_corrida: int,
    id_proveedor: int,
    id_canal: int
) -> int:
    """
    Inserta los resultados finales en semaforo_pricing_final.
    Solo llegan aquí los SKUs que pasaron el cruce con publicaciones.
    """
    if df.empty:
        print("⚠️  Semáforo vacío, nada que guardar.")
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    try:
        registros = [
            (
                id_corrida,
                id_proveedor,
                id_canal,
                row['sku_pim'],
                float(row['costo_anterior']),
                float(row['costo_actual']),
                float(row['variacion_nominal']),
                float(row['variacion_porcentual']),
                row['estado_costo'],
                bool(row.get('encontrado_en_publicaciones', False))
            )
            for _, row in df.iterrows()
        ]

        cursor.executemany("""
            INSERT INTO semaforo_pricing_final (
                id_corrida, id_proveedor, id_canal, sku_pim,
                costo_anterior, costo_actual,
                variacion_nominal, variacion_porcentual,
                estado_costo, encontrado_en_publicaciones
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, registros)

        conn.commit()
        total = cursor.rowcount
        print(f"🚦 Semáforo guardado: {total} registros")
        return total

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def guardar_diagnostico(
    df: pd.DataFrame,
    categoria: str,
    id_corrida: int,
    id_proveedor: int
) -> int:
    """
    Inserta SKUs excluidos en diagnostico_skus.
    categoria: 'SOLO_LISTA_ANTERIOR' | 'SOLO_LISTA_NUEVA' |
               'SOLO_EN_REPORTE' | 'SIN_MATCH_TOTAL'
    """
    if df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    try:
        sku_col = 'sku_pim' if 'sku_pim' in df.columns else df.columns[0]

        registros = [
            (id_corrida, id_proveedor, str(row[sku_col]), categoria)
            for _, row in df.iterrows()
        ]

        cursor.executemany("""
            INSERT INTO diagnostico_skus
                (id_corrida, id_proveedor, sku_raw, categoria_exclusion)
            VALUES (%s, %s, %s, %s)
        """, registros)

        conn.commit()
        total = cursor.rowcount
        print(f"🔍 Diagnóstico [{categoria}]: {total} SKUs")
        return total

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def cerrar_corrida(id_corrida: int, total_skus: int, exitoso: bool = True):
    """
    Actualiza el estado final de la corrida en historial_corridas.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        estado = 'EXITOSO' if exitoso else 'FALLIDO'
        cursor.execute("""
            UPDATE historial_corridas
            SET estado_ejecucion = %s,
                total_skus_procesados = %s
            WHERE id_corrida = %s
        """, (estado, total_skus, id_corrida))

        conn.commit()
        print(f"{'✅' if exitoso else '❌'} Corrida {id_corrida} cerrada: {estado} | {total_skus} SKUs")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()