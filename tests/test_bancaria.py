"""Pruebas automatizadas de las operaciones bancarias con pytest.

Cada prueba sigue, de manera explícita o implícita, el patrón AAA:
Arrange (preparar), Act (actuar) y Assert (comprobar).
"""


from decimal import Decimal

import pytest

from bancaria import (
    Cuenta,
    ErrorBancario,
    SaldoInsuficienteError,
    ingresar,
    retirar,
    transferir,
    validar_saldo,
)


@pytest.fixture
def origen() -> Cuenta:
    """Crea una cuenta de origen nueva y aislada para cada prueba."""
    return Cuenta("ES001", "Ana", "100.00")


@pytest.fixture
def destino() -> Cuenta:
    """Crea una cuenta de destino nueva y aislada para cada prueba."""
    return Cuenta("ES002", "Luis", "25.00")


def test_ingresar(origen: Cuenta) -> None:
    # Act y Assert: se ejecuta el ingreso y se verifica el saldo devuelto.
    assert ingresar(origen, "20.50") == Decimal("120.50")


def test_validar_saldo(origen: Cuenta) -> None:
    # Se prueban los límites: el saldo exacto es suficiente, un céntimo más no.
    assert validar_saldo(origen, "100") is True
    assert validar_saldo(origen, "100.01") is False


def test_retirar(origen: Cuenta) -> None:
    # La fixture ya ha realizado el Arrange creando una cuenta con 100 euros.
    assert retirar(origen, 40) == Decimal("60.00")


def test_retirar_sin_saldo_no_modifica_la_cuenta(origen: Cuenta) -> None:
    # pytest.raises comprueba que el bloque lanza la excepción indicada.
    with pytest.raises(SaldoInsuficienteError):
        retirar(origen, "100.01")

    # También comprobamos que la operación fallida no haya cambiado el saldo.
    assert origen.saldo == Decimal("100.00")


def test_transferir(origen: Cuenta, destino: Cuenta) -> None:
    # Act: se mueven 30,25 euros desde origen hasta destino.
    saldos = transferir(origen, destino, "30.25")

    # Assert: el dinero retirado de una cuenta aparece en la otra.
    assert saldos == (Decimal("69.75"), Decimal("55.25"))


def test_transferencia_sin_saldo_no_modifica_cuentas(
    origen: Cuenta, destino: Cuenta
) -> None:
    # Una transferencia sin fondos debe detenerse antes de modificar las cuentas.
    with pytest.raises(SaldoInsuficienteError):
        transferir(origen, destino, 101)

    assert origen.saldo == Decimal("100.00")
    assert destino.saldo == Decimal("25.00")


# parametrize ejecuta la misma prueba una vez por cada elemento de la lista. Así
# se cubren varios casos inválidos sin duplicar funciones de prueba.
@pytest.mark.parametrize("importe", [0, -1, "0.001", "texto"])
def test_rechaza_importes_no_positivos(origen: Cuenta, importe: int | str) -> None:
    with pytest.raises(ErrorBancario):
        ingresar(origen, importe)


def test_rechaza_transferencia_a_la_misma_cuenta(origen: Cuenta) -> None:
    # Una cuenta no puede ser simultáneamente origen y destino.
    with pytest.raises(ErrorBancario):
        transferir(origen, origen, 10)
