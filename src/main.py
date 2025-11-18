#ESTA OPCION SE UTILIZA YA PARA EL PROYECTO (YA PARA LA CAMARA EXTERNA) 
#from registro.registrar import registrar_usuario

#ESTA SE UTILIZA PARA HACER PRUEBAS CON EL REGISTRO
from registro.reg import registrar_usuario


#ESTA SE UTILIZA PARA HACER PRUEBAS CON LA CAMARA DE LA LAPTOP
#from reconocimiento.reconocimiento import reconocer

#ESTA SE UTILIZA PARA LA CAMARA EXTERNA (LA DE ANDRES)
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
