# ============================================================
# APLICACIÓN DE REGLAS COMERCIALES POR PROVEEDOR
# Traduce la lógica de aplicarReglasDatasetEnLimpiarSkus_
# ============================================================

def apply_exchange_rate(price: float, tipo_cambio: float) -> float:
    """Convierte precio de USD a MXN."""
    return round(price * tipo_cambio, 2)


def apply_discount(price: float, descuento: float) -> float:
    """
    Aplica descuento porcentual al precio.
    descuento viene de BD como 0.15 (15%) o 15 (también 15%).
    """
    if descuento > 1:
        descuento = descuento / 100
    return round(price * (1 - descuento), 2)


def apply_multiplier(price: float, factor: float) -> float:
    """Multiplica el precio por un factor."""
    return round(price * factor, 2)


def apply_price_rules(price: float, rule: dict) -> float:
    """
    Aplica todas las reglas comerciales de un proveedor en orden correcto:
    1. Tipo de cambio (si aplica)
    2. Descuento o multiplicador según tipo_aplicacion

    rule es un dict con las columnas de reglas_proveedores:
    {
        'aplica_tipo_cambio': bool,
        'tipo_cambio_fijo': float,
        'tipo_aplicacion': str,  # 'DESCUENTO' | 'MULTIPLICAR' | 'YA_APLICADO' | 'NO_TIENE'
        'descuento': float
    }
    """
    if price is None or price != price:  # None o NaN
        return price

    # Paso 1: tipo de cambio
    if rule.get('aplica_tipo_cambio'):
        tc = rule.get('tipo_cambio_fijo', 1)
        if tc and tc > 0:
            price = apply_exchange_rate(price, tc)

    # Paso 2: regla comercial
    tipo = str(rule.get('tipo_aplicacion') or '').upper().strip()

    if tipo == 'DESCUENTO':
        descuento = rule.get('descuento', 0)
        if descuento:
            price = apply_discount(price, descuento)

    elif tipo == 'MULTIPLICAR':
        factor = rule.get('descuento', 1)  # reutiliza columna descuento como factor
        if factor:
            price = apply_multiplier(price, factor)

    # YA_APLICADO y NO_TIENE no tocan el precio
    return price