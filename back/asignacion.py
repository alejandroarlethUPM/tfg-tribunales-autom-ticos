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
        tribunales (dict): diccionario turno → list[set de profesores]
                          Ejemplo: {"9:00": [{p1,p2,p3}, {p4,p5,p6}]}
        estudiantes (dict): diccionario alumno_id → datos
        dept_tribunal (str): nombre del departamento
    
    Returns:
        dict: diccionario turno → list[{'profesores': set, 'alumnos': dict}]
              Ejemplo: {"9:00": [
                  {'profesores': {p1,p2,p3}, 'alumnos': {alumno1: datos, ...}},
                  {'profesores': {p4,p5,p6}, 'alumnos': {alumno7: datos, ...}}
              ]}
    """
    asignacion = {t: [] for t in tribunales}
    disponibles = {k: v for k, v in estudiantes.items() if v['departamento'] == dept_tribunal}
    
    for turno, lista_tribunales in tribunales.items():
        asignaciones_turno = []
        
        for tribunal_prof in lista_tribunales:
            profes = list(tribunal_prof)
            
            if not profes:
                asignaciones_turno.append({
                    'profesores': set(),
                    'alumnos': {}
                })
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
            
            asignaciones_turno.append({
                'profesores': tribunal_prof,  # Mantener el set original
                'alumnos': asignados
            })
        
        asignacion[turno] = asignaciones_turno
    
    return asignacion