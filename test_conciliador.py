# ============================================================
# PRUEBA DEL CONCILIADOR DE SKUs
# ============================================================

import sys
import pandas as pd
sys.path.append('src/transform')
sys.path.append('src/utils')

from conciliador import conciliar_skus, cruzar_con_publicaciones

print("=== PRUEBAS DEL CONCILIADOR ===\n")

# Datos simulados: lista del mes anterior
df_anterior = pd.DataFrame([
    {'sku_pim': 'ZF-12345', 'costo_neto': 150.00},  # precio baja
    {'sku_pim': 'ZF-67890', 'costo_neto': 280.50},  # precio sube
    {'sku_pim': 'ZF-11111', 'costo_neto': 99.99},   # precio igual
    {'sku_pim': 'ZF-VIEJO', 'costo_neto': 50.00},   # desaparece
])

# Datos simulados: lista del mes actual
df_actual = pd.DataFrame([
    {'sku_pim': 'ZF-12345', 'costo_neto': 120.00},  # bajó
    {'sku_pim': 'ZF-67890', 'costo_neto': 310.00},  # subió
    {'sku_pim': 'ZF-11111', 'costo_neto': 99.99},   # igual
    {'sku_pim': 'ZF-NUEVO', 'costo_neto': 75.00},   # es nuevo
])

# Prueba 1: conciliación
print("1. Conciliación de listas:")
resultado = conciliar_skus(df_anterior, df_actual)

print("\n--- Semáforo ---")
print(resultado['semaforo'].to_string())

print("\n--- Solo en lista anterior ---")
print(resultado['solo_anterior'].to_string())

print("\n--- Solo en lista actual ---")
print(resultado['solo_actual'].to_string())

# Prueba 2: cruce con publicaciones
print("\n2. Cruce con publicaciones:")
df_publicaciones = pd.DataFrame([
    {'sku_pim_normalizado': 'ZF-12345'},
    {'sku_pim_normalizado': 'ZF-67890'},
    # ZF-11111 NO está publicado
])

cruce = cruzar_con_publicaciones(resultado['semaforo'], df_publicaciones)

print("\n--- Encontrados en marketplace ---")
print(cruce['encontrados'].to_string())

print("\n--- No encontrados en reporte ---")
print(cruce['no_en_reporte'].to_string())

print("\n=== FIN DE PRUEBAS ===")