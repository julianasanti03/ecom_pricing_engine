# ============================================================
# NORMALIZACIÓN DE SKUs
# Traducción directa de la lógica original en Apps Script
# ============================================================

import re

def norm_sku(value: str) -> str:
    """
    Normalización base de SKU:
    - Reemplaza espacios invisibles (NBSP)
    - Unifica familia de guiones tipográficos a guion estándar
    - Colapsa espacios múltiples
    - Trim y mayúsculas
    """
    if not value:
        return ""
    s = str(value)
    s = s.replace('\u00A0', ' ')
    s = re.sub(r'[\u2010-\u2015]', '-', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().upper()


def sku_no_spaces(value: str) -> str:
    """
    Elimina TODOS los espacios internos del SKU.
    Modo: remover_espacios = TRUE en reglas_proveedores.
    """
    s = fix_scientific(value)
    if not s:
        return ""
    s = s.replace('\u00A0', '')
    s = re.sub(r'\s+', '', s)
    return s


def sku_to_number_text(value: str) -> str:
    """
    Convierte SKUs puramente numéricos eliminando ceros a la izquierda.
    Ej: '000123' -> '123', '000' -> '0'
    Si tiene letras, cae a sku_no_spaces.
    Modo: 'CONVERTIR A NUMERO' en Dataset.
    """
    s = fix_scientific(value)
    if not s:
        return ""
    s = s.replace('\u00A0', '').strip()
    s = re.sub(r'\s+', '', s)

    if re.match(r'^\d+$', s):
        trimmed = re.sub(r'^0+(?=\d)', '', s)
        return trimmed if trimmed else '0'
    return sku_no_spaces(s)


def fix_scientific(value) -> str:
    """
    Rescata valores que Python o Sheets convirtió a notación científica.
    Ej: '2.5E+11' -> '250000000000'
    """
    if value is None:
        return ""
    if isinstance(value, float):
        if value != value:
            return ""
        return str(int(round(value)))
    s = str(value).strip()
    if not s:
        return ""
    if re.search(r'[eE][+\-]?\d+', s):
        try:
            n = float(s)
            return str(int(round(n)))
        except:
            return s
    return s


def add_prefix(sku: str, prefix: str, remove_spaces: bool) -> str:
    """
    Agrega prefijo al SKU si no lo tiene ya.
    Respeta el modo de espacios del proveedor.
    """
    if not sku:
        return ""
    p = re.sub(r'\s+', '', str(prefix or ''))
    if not p:
        return sku
    if sku.upper().startswith(p.upper()):
        return sku
    return f"{p}{sku}"


def apply_sku_mode(value: str, mode: str) -> str:
    """
    Aplica el modo de limpieza según reglas_proveedores.remover_espacios
    mode: 'KEEP' | 'NOSPACES' | 'TONUM'
    """
    if mode == 'NOSPACES':
        return sku_no_spaces(value)
    if mode == 'TONUM':
        return sku_to_number_text(value)
    # KEEP: solo limpieza básica
    s = fix_scientific(value)
    return s.replace('\u00A0', ' ').strip() if s else ""


def is_valid_sku(sku: str) -> bool:
    """
    Valida que el SKU no sea una celda vacía o encabezado.
    """
    s = str(sku or '').strip()
    if not s:
        return False
    u = s.upper()
    if u in ('GRUPO', 'GRUPO:'):
        return False
    if u.endswith(':'):
        return False
    return True


def canon_proveedor(name: str) -> str:
    """
    Normaliza nombre de proveedor para comparación tolerante a errores.
    Elimina acentos, espacios extra y caracteres especiales.
    """
    import unicodedata
    s = str(name or '').strip().upper()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^A-Z0-9 ]', '', s)
    return s