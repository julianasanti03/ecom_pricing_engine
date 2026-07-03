# ============================================================
# PRUEBA DEL ESCRITOR DEL SEMÁFORO
# ============================================================

import sys
import pandas as pd
from datetime import date
sys.path.append('src/output')
sys.path.append('src/utils')

from semaforo_writer import (
    crear_corrida,
    guardar_costos_historico,
    guardar_semaforo,
    guardar_diagnostico,
    cerrar_corrida
)

print("=== PRUEBA DEL SEMÁFORO WRITER ===\n")

# Datos de prueba
ID_PROVEEDOR = 1  # Zapatas Finas SA
ID_CANAL = 1      # Mercado Libre Cuenta Principal
MES_PASADO = date(2026, 4, 1)
MES_ACTUAL = date(2026, 5, 1)

# Paso 1: crear corrida
print("1. Creando corrida...")
id_corrida = crear_corrida(ID_PROVEEDOR, MES_PASADO, MES_ACTUAL)

# Paso 2: guardar costos históricos
print("\n2. Guardando costos históricos...")
df_costos = pd.DataFrame([
    {'sku_pim': 'ZF-12345', 'costo_neto': 120.00},
    {'sku_pim': 'ZF-67890', 'costo_neto': 310.00},
    {'sku_pim': 'ZF-11111', 'costo_neto': 99.99},
])
guardar_costos_historico(df_costos, id_corrida, ID_PROVEEDOR, MES_ACTUAL)

# Paso 3: guardar semáforo
print("\n3. Guardando semáforo...")
df_semaforo = pd.DataFrame([
    {
        'sku_pim': 'ZF-12345',
        'costo_anterior': 150.00,
        'costo_actual': 120.00,
        'variacion_nominal': -30.00,
        'variacion_porcentual': -20.00,
        'estado_costo': 'BAJO',
        'encontrado_en_publicaciones': True
    },
    {
        'sku_pim': 'ZF-67890',
        'costo_anterior': 280.50,
        'costo_actual': 310.00,
        'variacion_nominal': 29.50,
        'variacion_porcentual': 10.52,
        'estado_costo': 'SUBIO',
        'encontrado_en_publicaciones': True
    },
])
guardar_semaforo(df_semaforo, id_corrida, ID_PROVEEDOR, ID_CANAL)

# Paso 4: guardar diagnóstico
print("\n4. Guardando diagnóstico...")
df_solo_anterior = pd.DataFrame([{'sku_pim': 'ZF-VIEJO'}])
df_solo_actual   = pd.DataFrame([{'sku_pim': 'ZF-NUEVO'}])

guardar_diagnostico(df_solo_anterior, 'SOLO_LISTA_ANTERIOR', id_corrida, ID_PROVEEDOR)
guardar_diagnostico(df_solo_actual,   'SOLO_LISTA_NUEVA',    id_corrida, ID_PROVEEDOR)

# Paso 5: cerrar corrida
print("\n5. Cerrando corrida...")
cerrar_corrida(id_corrida, total_skus=3, exitoso=True)

print("\n=== FIN DE PRUEBA ===")