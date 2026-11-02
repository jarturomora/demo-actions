"""Lógica de negocio de una pequeña simulación bancaria.

Este módulo no contiene código de la interfaz de usuario. De esta forma, las
operaciones bancarias pueden utilizarse desde la consola, desde una futura
interfaz gráfica o directamente desde las pruebas.
"""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import TypeAlias


# Un alias de tipo documenta todos los formatos que aceptan nuestras funciones.
# Internamente siempre convertiremos los importes a Decimal.
Importe: TypeAlias = Decimal | int | float | str

# Decimal("0.01") representa la precisión de un céntimo. Se usa para redondear
# todos los importes a las dos posiciones decimales habituales en euros.
DOS_DECIMALES = Decimal("0.01")


class ErrorBancario(ValueError):
    """Error base para una operación bancaria no válida.

    Heredar de ValueError indica que el problema está en un valor recibido.
    Tener una excepción propia permite que la interfaz capture únicamente los
    errores esperados del dominio bancario.
    """


class SaldoInsuficienteError(ErrorBancario):
    """Error específico para una cuenta sin saldo suficiente."""


def _normalizar_importe(importe: Importe) -> Decimal:
    """Convierte un importe a Decimal y comprueba que sea positivo.

    El guion bajo inicial indica que es una función auxiliar de uso interno.
    Centralizar aquí la validación evita repetirla en cada operación bancaria.
    """
    try:
        # Primero se convierte a str para que un float como 0.1 no arrastre su
        # representación binaria aproximada al construir el Decimal.
        cantidad = Decimal(str(importe))
    except (InvalidOperation, ValueError) as error:
        # "from error" conserva la causa original para facilitar la depuración.
        raise ErrorBancario("El importe debe ser un número válido.") from error

    # También se rechazan valores especiales de Decimal como NaN e infinito.
    if not cantidad.is_finite() or cantidad <= 0:
        raise ErrorBancario("El importe debe ser mayor que cero.")

    try:
        # quantize ajusta el número a la precisión indicada: dos decimales.
        cantidad = cantidad.quantize(DOS_DECIMALES)
    except InvalidOperation as error:
        raise ErrorBancario("El importe está fuera del rango permitido.") from error

    # Una cantidad positiva muy pequeña podría redondearse a cero céntimos.
    if cantidad == 0:
        raise ErrorBancario("El importe mínimo es 0.01.")
    return cantidad


@dataclass
class Cuenta:
    """Cuenta bancaria identificada por un número y con saldo en euros.

    @dataclass genera automáticamente métodos como __init__ y __repr__, lo que
    permite concentrar la clase en sus datos y reglas de validación.
    """

    numero: str
    titular: str
    # default_factory crea el saldo por defecto al construir cada nueva cuenta.
    saldo: Decimal = field(default_factory=lambda: Decimal("0.00"))

    def __post_init__(self) -> None:
        """Valida y normaliza el saldo después del __init__ generado."""
        try:
            saldo = Decimal(str(self.saldo))
        except (InvalidOperation, ValueError) as error:
            raise ErrorBancario("El saldo inicial debe ser un número válido.") from error

        # En este simulador no se permiten descubiertos ni saldos especiales.
        if not saldo.is_finite() or saldo < 0:
            raise ErrorBancario("El saldo inicial no puede ser negativo.")
        self.saldo = saldo.quantize(DOS_DECIMALES)


def validar_saldo(cuenta: Cuenta, importe: Importe) -> bool:
    """Devuelve True si la cuenta dispone del importe indicado.

    El importe también se valida: debe ser numérico y mayor que cero.
    """
    cantidad = _normalizar_importe(importe)
    # La comparación incluye la igualdad: se puede retirar todo el saldo.
    return cuenta.saldo >= cantidad


def ingresar(cuenta: Cuenta, importe: Importe) -> Decimal:
    """Ingresa dinero y devuelve el nuevo saldo."""
    # Validamos antes de modificar la cuenta para no dejar un estado incorrecto.
    cantidad = _normalizar_importe(importe)
    cuenta.saldo += cantidad
    return cuenta.saldo


def retirar(cuenta: Cuenta, importe: Importe) -> Decimal:
    """Retira dinero y devuelve el nuevo saldo."""
    cantidad = _normalizar_importe(importe)

    # La validación de saldo se reutiliza tanto aquí como en las transferencias.
    if not validar_saldo(cuenta, cantidad):
        raise SaldoInsuficienteError(
            f"Saldo insuficiente en la cuenta {cuenta.numero}."
        )
    # La resta solo ocurre después de superar todas las validaciones.
    cuenta.saldo -= cantidad
    return cuenta.saldo


def transferir(origen: Cuenta, destino: Cuenta, importe: Importe) -> tuple[Decimal, Decimal]:
    """Transfiere dinero y devuelve los saldos de origen y destino."""
    # Se comparan tanto los objetos como sus números para impedir una
    # transferencia a la misma cuenta, aunque existan dos objetos diferentes.
    if origen is destino or origen.numero == destino.numero:
        raise ErrorBancario("Las cuentas de origen y destino deben ser distintas.")

    cantidad = _normalizar_importe(importe)
    if not validar_saldo(origen, cantidad):
        raise SaldoInsuficienteError(
            f"Saldo insuficiente en la cuenta {origen.numero}."
        )

    # Ambas modificaciones se hacen juntas y únicamente tras validar todo. Así,
    # una operación fallida no cambia ninguna de las dos cuentas.
    origen.saldo -= cantidad
    destino.saldo += cantidad
    return origen.saldo, destino.saldo
