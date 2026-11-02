"""Interfaz de consola para interactuar con la simulación bancaria.

Este archivo se ocupa de pedir y mostrar datos. Las reglas bancarias permanecen
en bancaria.py, siguiendo el principio de separación de responsabilidades.
"""

from decimal import Decimal

from bancaria import Cuenta, ErrorBancario, ingresar, retirar, transferir


def mostrar_cuentas(cuentas: dict[str, Cuenta]) -> None:
    """Muestra por pantalla el número, titular y saldo de cada cuenta."""
    print("\nCuentas:")
    for cuenta in cuentas.values():
        # :.2f obliga a mostrar siempre dos decimales, incluso si son ceros.
        print(f"  {cuenta.numero} - {cuenta.titular}: {cuenta.saldo:.2f} €")


def pedir_cuenta(cuentas: dict[str, Cuenta], mensaje: str) -> Cuenta:
    """Solicita un número de cuenta y devuelve la cuenta correspondiente."""
    # strip elimina espacios accidentales antes y después de la entrada.
    numero = input(mensaje).strip()
    if numero not in cuentas:
        raise ErrorBancario("La cuenta indicada no existe.")
    return cuentas[numero]


def ejecutar() -> None:
    """Ejecuta el menú principal hasta que el usuario elija salir."""
    # El diccionario permite localizar una cuenta rápidamente por su número.
    # Los datos son de ejemplo y solo existen mientras el programa está abierto.
    cuentas = {
        "ES001": Cuenta("ES001", "Ana", Decimal("1000.00")),
        "ES002": Cuenta("ES002", "Luis", Decimal("500.00")),
    }

    # El bucle mantiene activo el menú hasta ejecutar la instrucción break.
    while True:
        mostrar_cuentas(cuentas)
        print("\n1. Ingresar\n2. Retirar\n3. Transferir\n4. Salir")
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "4":
            print("Hasta pronto.")
            break

        try:
            # Cada opción delega la operación real en las funciones de
            # bancaria.py; esta capa solo recoge datos y muestra resultados.
            if opcion == "1":
                cuenta = pedir_cuenta(cuentas, "Número de cuenta: ")
                ingresar(cuenta, input("Importe: "))
                print("Ingreso realizado correctamente.")
            elif opcion == "2":
                cuenta = pedir_cuenta(cuentas, "Número de cuenta: ")
                retirar(cuenta, input("Importe: "))
                print("Retirada realizada correctamente.")
            elif opcion == "3":
                origen = pedir_cuenta(cuentas, "Cuenta de origen: ")
                destino = pedir_cuenta(cuentas, "Cuenta de destino: ")
                transferir(origen, destino, input("Importe: "))
                print("Transferencia realizada correctamente.")
            else:
                print("Opción no válida.")
        except ErrorBancario as error:
            # Los errores previstos se muestran sin finalizar el programa.
            print(f"Error: {error}")


# Esta condición evita abrir el menú si main.py se importa desde otro módulo.
if __name__ == "__main__":
    ejecutar()
