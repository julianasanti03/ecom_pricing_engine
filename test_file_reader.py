# ============================================================
# PRUEBA DEL LECTOR DE ARCHIVOS
# ============================================================

import sys
import os
sys.path.append('src/ingestion')
sys.path.append('src/utils')

from file_reader import read_csv, clean_dataframe, validate_file_prefix

print("=== PRUEBAS DEL LECTOR DE ARCHIVOS ===\n")

filepath = 'input/ZF_2026_05.csv'
prefix = 'ZF'

# Prueba 1: validar prefijo
print("1. Validación de prefijo:")
print(f"   ZF_2026_05.csv con prefijo ZF: {validate_file_prefix(filepath, prefix)} → esperado: True")
print(f"   ZF_2026_05.csv con prefijo AB: {validate_file_prefix(filepath, 'AB')} → esperado: False")

# Prueba 2: leer CSV crudo
print("\n2. Lectura cruda del CSV:")
df_raw = read_csv(filepath)
print(df_raw.to_string())

# Prueba 3: limpiar con modo NOSPACES
print("\n3. Limpieza con modo NOSPACES:")
df_clean = clean_dataframe(df_raw.copy(), sku_mode='NOSPACES', prefix=prefix)
print(df_clean.to_string())

# Prueba 4: limpiar con modo TONUM
print("\n4. Limpieza con modo TONUM:")
df_clean2 = clean_dataframe(df_raw.copy(), sku_mode='TONUM', prefix=prefix)
print(df_clean2.to_string())

print("\n=== FIN DE PRUEBAS ===")