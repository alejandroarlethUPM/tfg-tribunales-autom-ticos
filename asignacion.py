import pandas as pd
from mapping import extraer_correos

def cargar_estudiantes(file_tfgs):
    """
    Carga estudiantes de todas las hojas del Excel de TFGs.
    
    Args:
        file_tfgs (pd.ExcelFile): objeto ExcelFile con TFGs por departamento
    
    Returns:
        dict: diccionario alumno_id → {nombre, tutores, departamento}
    """
    estudiantes = {}
    for hoja in file_tfgs.sheet_names:
        df = pd.read_excel(file_tfgs, sheet_name=hoja, header=0)
        for i in range(df.shape[0]):
            correos = extraer_correos(df.iloc[i, 7])
            trabajo_id = df.iloc[i, 2]  # columna 2 = alumno (nombre y apellidos)
            estudiantes[trabajo_id] = {
                'nombre': df.iloc[i, 3],
                'tutores': correos,
                'departamento': hoja,
                'grado': df.iloc[i, -1],  # última columna: grado del estudiante
            }
    return estudiantes


def asignar_alumnos_a_tribunales(tribunales, estudiantes, dept_tribunal):
    """
    Asigna alumnos de un departamento a los tribunales.
    
    Args:
        tribunales (dict): diccionario turno → set de profesores
        estudiantes (dict): diccionario alumno_id → datos
        dept_tribunal (str): nombre del departamento
    
    Returns:
        dict: diccionario turno → {alumno_id: datos}
    """
    asignacion = {t: {} for t in tribunales}
    disponibles = {k: v for k, v in estudiantes.items() if v['departamento'] == dept_tribunal}
    
    for turno, profes in {t: list(p) for t, p in tribunales.items()}.items():
        if not profes:
            continue
        
        asignados = {}
        for trabajo, datos in list(disponibles.items()):
            if len(asignados) == 6:
                break
            # No asignar si el tutor está en el tribunal
            if any(t in profes for t in datos['tutores']):
                continue
            # Asignar
            asignados[trabajo] = datos
            del disponibles[trabajo]
        
        asignacion[turno] = asignados
    
    return asignacion