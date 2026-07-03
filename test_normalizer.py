# ============================================================
# PRUEBA DE NORMALIZACIÓN DE SKUs
# ============================================================

import sys
sys.path.append('src/utils')
from sku_normalizer import norm_sku, sku_no_spaces, sku_to_number_text, fix_scientific, is_valid_sku

print("=== PRUEBAS DE NORMALIZACIÓN ===\n")

# Prueba 1: espacios invisibles y guiones tipográficos
print("1. Espacios y guiones:")
print(f"   '{norm_sku('  zf‐12345  ')}' → esperado: 'ZF-12345'")

# Prueba 2: notación científica
print("\n2. Notación científica:")
print(f"   '{fix_scientific('2.5E+11')}' → esperado: '250000000000'")
print(f"   '{fix_scientific(1.23e5)}' → esperado: '123000'")

# Prueba 3: quitar espacios
print("\n3. Sin espacios:")
print(f"   '{sku_no_spaces('ZF 123 45')}' → esperado: 'ZF12345'")

# Prueba 4: convertir a número
print("\n4. Convertir a número:")
print(f"   '{sku_to_number_text('000123')}' → esperado: '123'")
print(f"   '{sku_to_number_text('000')}' → esperado: '0'")
print(f"   '{sku_to_number_text('ZF-123')}' → esperado: 'ZF-123'")

# Prueba 5: validación
print("\n5. Validación de SKUs:")
print(f"   is_valid_sku('ZF-123'): {is_valid_sku('ZF-123')} → esperado: True")
print(f"   is_valid_sku('GRUPO:'): {is_valid_sku('GRUPO:')} → esperado: False")
print(f"   is_valid_sku(''): {is_valid_sku('')} → esperado: False")

print("\n=== FIN DE PRUEBAS ===")