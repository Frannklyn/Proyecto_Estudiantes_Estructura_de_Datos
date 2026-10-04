from models import Estudiante, CAMPOS_ESTUDIANTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

gestor = GestorJSON("data/estudiantes.json")

CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")
NOTA_MINIMA = 0
NOTA_MAXIMA = 20


def normalizar(campo, valor):
    texto = str(valor).strip()
    if campo == "carnet":
        return texto.upper()
    return texto


def emails_registrados(excepto_id=None):
    return {
        registro["email"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def carnets_registrados(excepto_id=None):
    return {
        registro["carnet"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def siguiente_id():
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


def crear_estudiante(datos):
    try:
        valores = {campo: normalizar(campo, datos.get(campo, "")) for campo in CAMPOS_ESTUDIANTE}
        faltantes = [campo for campo in CAMPOS_OBLIGATORIOS if not valores[campo]]
        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"
        if valores["email"].lower() in emails_registrados():
            return False, "Ese email ya está registrado"
        if valores["carnet"].lower() in carnets_registrados():
            return False, "Ese carnet ya está registrado"
        estudiante = Estudiante(siguiente_id(), **valores)
        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"
        return True, f"Estudiante {estudiante.obtener_nombre_completo()} creado con id {estudiante.id}"
    except Exception as error:
        return False, f"Error inesperado: {error}"


def obtener_todos():
    return [Estudiante.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(id_estudiante):
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


def buscar_estudiantes(termino):
    termino = termino.strip().lower()
    if not termino:
        return []
    encontrados = []
    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(Estudiante.desde_diccionario(registro))
                break
    return encontrados


def actualizar_estudiante(id_estudiante, cambios):
    try:
        desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
        if not cambios:
            return False, "No se indicó ningún cambio"
        cambios = {campo: normalizar(campo, valor) for campo, valor in cambios.items()}
        vacios = [campo for campo, valor in cambios.items() if not valor]
        if vacios:
            return False, f"Los campos no pueden quedar vacíos: {', '.join(sorted(vacios))}"
        if "email" in cambios:
            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"
            if cambios["email"].lower() in emails_registrados(excepto_id=id_estudiante):
                return False, "Ese email ya lo usa otro estudiante"
        if "carnet" in cambios:
            if cambios["carnet"].lower() in carnets_registrados(excepto_id=id_estudiante):
                return False, "Ese carnet ya lo usa otro estudiante"
        registros = gestor.leer()
        posicion = None
        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                posicion = indice
                break
        if posicion is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        registros[posicion].update(cambios)
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"
        return True, f"Estudiante {id_estudiante} actualizado ({len(cambios)} campo/s)"
    except Exception as error:
        return False, f"Error inesperado: {error}"


def eliminar_estudiante(id_estudiante):
    registros = gestor.leer()
    quedan = [registro for registro in registros if registro["id"] != id_estudiante]
    if len(quedan) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"
    if not gestor.guardar(quedan):
        return False, "No se pudo escribir el archivo"
    return True, f"Estudiante {id_estudiante} eliminado"


def agregar_nota(id_estudiante, materia, nota):
    try:
        materia = " ".join(str(materia).split()).capitalize()
        if not materia:
            return False, "La materia es obligatoria"
        try:
            valor = float(str(nota).strip().replace(",", "."))
        except ValueError:
            return False, "La nota debe ser un número"
        if not NOTA_MINIMA <= valor <= NOTA_MAXIMA:
            return False, f"La nota debe estar entre {NOTA_MINIMA} y {NOTA_MAXIMA}"
        if valor.is_integer():
            valor = int(valor)
        registros = gestor.leer()
        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                estudiante = Estudiante.desde_diccionario(registro)
                estudiante.agregar_nota(materia, valor)
                registros[indice] = estudiante.a_diccionario()
                if not gestor.guardar(registros):
                    return False, "No se pudo escribir el archivo"
                return True, f"Nota {valor} registrada en {materia} para {estudiante.obtener_nombre_completo()}"
        return False, f"No existe un estudiante con id {id_estudiante}"
    except Exception as error:
        return False, f"Error inesperado: {error}"


def promedio_estudiante(id_estudiante):
    estudiante = obtener_por_id(id_estudiante)
    if estudiante is None:
        return False, f"No existe un estudiante con id {id_estudiante}"
    if not estudiante.notas:
        return False, f"{estudiante.obtener_nombre_completo()} todavía no tiene notas"
    return True, estudiante.obtener_promedio()


def materias_ofertadas():
    materias = set()
    for estudiante in obtener_todos():
        materias |= estudiante.materias
    return materias


def estudiantes_en_comun(id_a, id_b):
    if id_a == id_b:
        return False, "Debe indicar dos estudiantes distintos"
    estudiante_a = obtener_por_id(id_a)
    estudiante_b = obtener_por_id(id_b)
    if estudiante_a is None:
        return False, f"No existe un estudiante con id {id_a}"
    if estudiante_b is None:
        return False, f"No existe un estudiante con id {id_b}"
    return True, estudiante_a.materias_en_comun(estudiante_b)


def estadisticas():
    estudiantes = obtener_todos()
    dominios = {e.email.split("@")[1].lower() for e in estudiantes if "@" in e.email}
    con_notas = [e for e in estudiantes if e.notas]
    sin_notas = [e.obtener_nombre_completo() for e in estudiantes if not e.notas]
    promedio_general = 0
    if con_notas:
        promedio_general = round(sum(e.obtener_promedio() for e in con_notas) / len(con_notas), 2)
    return {
        "total": len(estudiantes),
        "dominios": sorted(dominios),
        "materias": sorted(materias_ofertadas()),
        "sin_notas": sin_notas,
        "promedio_general": promedio_general,
    }
