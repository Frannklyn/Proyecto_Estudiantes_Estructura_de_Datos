from models import CAMPOS_ESTUDIANTE
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import (
    crear_estudiante, obtener_todos, obtener_por_id, buscar_estudiantes,
    actualizar_estudiante, eliminar_estudiante, agregar_nota, promedio_estudiante,
    materias_ofertadas, estudiantes_en_comun, estadisticas
)


def pausa():
    input("\nPresione Enter para continuar...")


def pedir_id(texto="Id del estudiante: "):
    try:
        return int(input(texto))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_tabla(estudiantes):
    print(f"{'ID':<5}{'CARNET':<14}{'NOMBRE':<26}{'EMAIL':<28}{'PROMEDIO':<10}")
    print("-" * 83)
    for estudiante in estudiantes:
        print(f"{estudiante.id:<5}{estudiante.carnet:<14}"
              f"{estudiante.obtener_nombre_completo():<26}"
              f"{estudiante.email:<28}{estudiante.obtener_promedio():<10}")
    print("-" * 83)
    imprimir_info(f"Total: {len(estudiantes)} estudiante(s)")


def mostrar_detalle(estudiante):
    datos = estudiante.a_diccionario()
    for campo in CAMPOS_ESTUDIANTE:
        print(f"  {campo.capitalize():<12}: {datos[campo]}")
    print(f"  {'Promedio':<12}: {estudiante.obtener_promedio()}")
    print(f"  {'Materias':<12}: {', '.join(datos['materias']) if datos['materias'] else 'Sin materias'}")
    for materia, lista_notas in datos["notas"].items():
        print(f"    - {materia}: {', '.join(str(nota) for nota in lista_notas)}")


def opcion_crear():
    imprimir_titulo("REGISTRAR NUEVO ESTUDIANTE")
    datos = {}
    for campo in CAMPOS_ESTUDIANTE:
        datos[campo] = input(f"{campo.capitalize()}: ")
    exito, mensaje = crear_estudiante(datos)
    mostrar_resultado(exito, mensaje)
    pausa()


def opcion_ver_todos():
    imprimir_titulo("LISTA DE ESTUDIANTES")
    estudiantes = obtener_todos()
    if not estudiantes:
        imprimir_info("Todavía no hay estudiantes. Use la opción 1 para registrar el primero.")
    else:
        mostrar_tabla(estudiantes)
    pausa()


def opcion_buscar():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email o carnet: ")
    encontrados = buscar_estudiantes(termino)
    if not encontrados:
        imprimir_info(f"Ningún estudiante coincide con '{termino}'.")
    else:
        mostrar_tabla(encontrados)
    pausa()


def opcion_ver_por_id():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
    else:
        mostrar_detalle(estudiante)
    pausa()


def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()
    imprimir_info(f"Editando a {estudiante.obtener_nombre_completo()}")
    print("Deje en blanco el campo que no quiera cambiar.\n")
    cambios = {}
    for campo in CAMPOS_ESTUDIANTE:
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    exito, mensaje = actualizar_estudiante(id_estudiante, cambios)
    mostrar_resultado(exito, mensaje)
    pausa()


def opcion_eliminar():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()
    imprimir_info(f"Se eliminará: {estudiante}")
    if confirmar("¿Confirma la eliminación?"):
        exito, mensaje = eliminar_estudiante(id_estudiante)
        mostrar_resultado(exito, mensaje)
    else:
        imprimir_info("Operación cancelada")
    pausa()


def opcion_agregar_nota():
    imprimir_titulo("AGREGAR NOTA")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()
    imprimir_info(f"Estudiante: {estudiante.obtener_nombre_completo()}")
    materia = input("Materia: ")
    nota = input("Nota (0 a 20): ")
    exito, mensaje = agregar_nota(id_estudiante, materia, nota)
    mostrar_resultado(exito, mensaje)
    pausa()


def opcion_ver_promedio():
    imprimir_titulo("VER PROMEDIO")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    exito, resultado = promedio_estudiante(id_estudiante)
    if exito:
        imprimir_exito(f"Promedio del estudiante {id_estudiante}: {resultado}")
    else:
        imprimir_error(resultado)
    pausa()


def opcion_materias_en_comun():
    imprimir_titulo("MATERIAS EN COMÚN")
    id_a = pedir_id("Id del primer estudiante: ")
    if id_a is None:
        return pausa()
    id_b = pedir_id("Id del segundo estudiante: ")
    if id_b is None:
        return pausa()
    exito, resultado = estudiantes_en_comun(id_a, id_b)
    if not exito:
        imprimir_error(resultado)
    elif not resultado:
        imprimir_info("Los estudiantes no comparten ninguna materia")
    else:
        imprimir_exito(f"Materias en común: {', '.join(sorted(resultado))}")
    pausa()


def opcion_materias_ofertadas():
    imprimir_titulo("MATERIAS OFERTADAS")
    materias = materias_ofertadas()
    if not materias:
        imprimir_info("Todavía no hay materias inscritas")
    else:
        for materia in sorted(materias):
            print(f"  - {materia}")
        imprimir_info(f"Total: {len(materias)} materia(s)")
    pausa()


def opcion_estadisticas():
    imprimir_titulo("ESTADÍSTICAS")
    datos = estadisticas()
    print(f"  Estudiantes registrados : {datos['total']}")
    print(f"  Promedio general        : {datos['promedio_general']}")
    print(f"  Materias distintas      : {len(datos['materias'])} -> {', '.join(datos['materias'])}")
    print(f"  Dominios de email       : {', '.join(datos['dominios'])}")
    print(f"  Sin notas               : {len(datos['sin_notas'])}")
    pausa()


def salir():
    imprimir_info("¡Hasta luego! 👋")
    return "salir"


OPCIONES = {
    "1": ("Registrar estudiante", opcion_crear),
    "2": ("Ver todos", opcion_ver_todos),
    "3": ("Buscar", opcion_buscar),
    "4": ("Ver por id", opcion_ver_por_id),
    "5": ("Actualizar", opcion_actualizar),
    "6": ("Eliminar", opcion_eliminar),
    "7": ("Agregar nota", opcion_agregar_nota),
    "8": ("Ver promedio", opcion_ver_promedio),
    "9": ("Materias en común", opcion_materias_en_comun),
    "10": ("Materias ofertadas", opcion_materias_ofertadas),
    "11": ("Estadísticas", opcion_estadisticas),
    "0": ("Salir", salir),
}


def mostrar_menu():
    imprimir_titulo("SISTEMA DE GESTIÓN DE ESTUDIANTES")
    for tecla, (texto, _funcion) in OPCIONES.items():
        print(f"  {tecla}. {texto}")
    print()


def main():
    while True:
        mostrar_menu()
        tecla = input("Seleccione una opción: ").strip()
        if tecla not in OPCIONES:
            imprimir_error("Opción no válida")
            pausa()
            continue
        _texto, funcion = OPCIONES[tecla]
        if funcion() == "salir":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
