# operaciones.py

def sumar(a, b):
    return a + b

def restar(a, b):
    return a - b

def multiplicar(a, b):
    return a * b

def dividir(a, b):
    if b == 0:
        raise ValueError("El divisor no puede ser cero.")
    return a / b

if __name__ == "__main__":
    print(sumar(5, 3))
    print(restar(5, 3))
    print(multiplicar(5, 3))
    print(dividir(5, 3))
