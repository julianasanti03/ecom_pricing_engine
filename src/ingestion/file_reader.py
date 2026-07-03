# ============================================================
# LECTOR DE ARCHIVOS DE PROVEEDORES
# Lee CSVs locales o Google Sheets y los convierte a DataFrame
# Un DataFrame es básicamente una tabla en memoria, como un Sheet
# ============================================================

import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from sku_normalizer import norm_sku, is_valid_sku


def read_csv(filepath: str) -> pd.DataFrame:
    """
    Lee un archivo CSV del proveedor.
    Espera exactamente 2 columnas: SKU y PRECIO, en ese orden.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No se encontró el archivo: {filepath}")

    df = pd.read_csv(
        filepath,
        header=0,
        dtype=str,
        encoding='utf-8-sig'
    )

    cols = df.columns.tolist()
    df = df.rename(columns={
        cols[0]: 'sku_raw',
        cols[1]: 'precio_raw'
    })

    df = df[['sku_raw', 'precio_raw']].copy()
    df = df.dropna(how='all')

    print(f"📂 Archivo leído: {filepath}")
    print(f"   Filas crudas: {len(df)}")

    return df


def clean_dataframe(df: pd.DataFrame, sku_mode: str, prefix: str) -> pd.DataFrame:
    """
    Aplica normalización de SKUs y limpieza de precios.
    sku_mode: 'KEEP' | 'NOSPACES' | 'TONUM'
    prefix: prefijo del proveedor desde reglas_proveedores
    """
    from sku_normalizer import apply_sku_mode, add_prefix, fix_scientific

    def clean_sku(raw):
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return None
        if str(raw).strip() == '' or str(raw).strip().upper() == 'NAN':
            return None
        sku = apply_sku_mode(str(raw), sku_mode)
        sku = add_prefix(sku, prefix, sku_mode != 'KEEP')
        return sku if is_valid_sku(sku) else None

    def clean_price(raw):
        if not raw or str(raw).strip() == '':
            return None
        cleaned = str(raw).replace('$', '').replace(',', '').strip()
        try:
            return float(cleaned)
        except:
            return None

    df['sku_pim'] = df['sku_raw'].apply(clean_sku)
    df['costo_neto'] = df['precio_raw'].apply(clean_price)

    antes = len(df)
    df = df.dropna(subset=['sku_pim', 'costo_neto'])
    despues = len(df)

    print(f"   SKUs válidos: {despues} (descartados: {antes - despues})")

    return df[['sku_pim', 'costo_neto']].copy()


def validate_file_prefix(filepath: str, prefix: str) -> bool:
    """
    Verifica que el nombre del archivo corresponda al proveedor esperado.
    """
    filename = os.path.basename(filepath).upper()
    return filename.startswith(prefix.upper())