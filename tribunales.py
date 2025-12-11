import random as rnd

def distribuir_tribunales(num_tribunales_necesarios, num_franjas):
    """
    Distribuye tribunales equitativamente entre franjas horarias.
    
    Args:
        num_estudiantes (int): número de estudiantes del departamento
        num_franjas (int): número de franjas horarias disponibles
    
    Returns:
        list: lista con número de tribunales por franja
    """
    dist = [0] * num_franjas
    for i in range(num_tribunales_necesarios):
        dist[i % num_franjas] += 1
    return dist


def crear_tribunales_depto(df_depto, init_franja, num_trib_por_franja):
    """
    Crea tribunales para un departamento específico.
    
    Args:
        df_depto (pd.DataFrame): datos de disponibilidad del departamento
        init_franja (int): columna donde comienzan las franjas
        num_trib_por_franja (list): número de tribunales por franja
    
    Returns:
        dict: diccionario turno → set de profesores
    """
    keys = df_depto.keys()
    turnos = keys[init_franja:init_franja + len(num_trib_por_franja)]
    
    # Construir disponibilidad y participación
    disponibilidad = {}
    participacion = {}
    for i in range(df_depto.shape[0]):
        correo = df_depto[keys[1]][i]
        participacion[correo] = df_depto[keys[2]][i]
        disp = set()
        for turno in turnos:
            if df_depto[turno][i] == "Sí":
                disp.add(turno)
        disponibilidad[correo] = disp

    # Calcular profesores necesarios por turno
    num_prof = {turnos[i]: 3*num_trib_por_franja[i] for i in range(len(num_trib_por_franja))}
    tribunales = {turno: set() for turno in turnos}

    def compute_holgura():
        """Calcula holgura (disponibles - necesarios) por turno"""
        return {turno: sum(1 for p in disponibilidad if turno in disponibilidad[p]) - num_prof[turno]
                for turno in num_prof}

    holgura = compute_holgura()
    if (min([holgura[turno] for turno in holgura])<0):
        print("Atención: No hay suficientes profesores para cubrir los tribunales necesarios.")

    prof_needed = sum(num_prof.values())

    # Algoritmo greedy de asignación de profesores
    while prof_needed > 0 and num_prof:
        menor = min(holgura.values())
        turno_activo = rnd.choice(list(filter(lambda t: holgura[t] == menor, holgura)))

        # Profesores disponibles en este turno
        select_prof = [p for p in disponibilidad if turno_activo in disponibilidad[p]]
        if not select_prof:
            break
        
        # Filtrar por menor participación
        min_part = min(participacion[p] for p in select_prof)
        select_prof = [p for p in select_prof if participacion[p] == min_part]
        
        # Filtrar por menor disponibilidad
        min_disp = min(len(disponibilidad[p]) for p in select_prof)
        select_prof = [p for p in select_prof if len(disponibilidad[p]) == min_disp]

        # Seleccionar profesor aleatorio
        prof = rnd.choice(select_prof)
        tribunales[turno_activo].add(prof)
        num_prof[turno_activo] -= 1
        
        # Limpiar turno si está completo
        if num_prof[turno_activo] == 0:
            del num_prof[turno_activo]
            del holgura[turno_activo]
        
        # Quitar profesor de disponibles
        del disponibilidad[prof]
        participacion[prof] += 1

        # Recalcular holgura
        if num_prof:
            holgura = compute_holgura()
        prof_needed -= 1

    return tribunales