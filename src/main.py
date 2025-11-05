from registro.registrar import registrar_usuario
#from reconocimiento.reconocimiento import reconocer
from reconocimiento.rec import reconocer

def main():
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Registrar Usuario")
        print("2. Acceder / Reconocer Usuario")
        print("3. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            reconocer()
        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción inválida, intenta de nuevo.")

if __name__ == "__main__":
    main()
