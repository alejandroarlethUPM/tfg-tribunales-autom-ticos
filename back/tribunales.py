import random as rnd
import math

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


def agrupar_profesores_en_tribunales(profesores_set):
    """
    Agrupa profesores en tribunales de 3 miembros.
    
    Args:
        profesores_set (set): conjunto de profesores asignados a un turno
        num_tribunales (int): número de tribunales esperados en este turno
    
    Returns:
        list: lista de sets, cada uno con 3 profesores
    """
    profesores_list = list(profesores_set)
    tribunales = []

    for i in range(len(profesores_list) // 3):
        inicio = i * 3
        fin = min(inicio + 3, len(profesores_list))
        if inicio < len(profesores_list):
            tribunal = set(profesores_list[inicio:fin])
            tribunales.append(tribunal)
    
    return tribunales


def crear_tribunales_depto(df_depto, init_franja, num_trib_por_franja):
    """
    Crea tribunales para un departamento específico.
    Agrupa profesores de 3 en 3 por tribunal.
    
    Args:
        df_depto (pd.DataFrame): datos de disponibilidad del departamento
        init_franja (int): columna donde comienzan las franjas
        num_trib_por_franja (list): número de tribunales por franja
    
    Returns:
        dict: diccionario turno → list[set de profesores]
              Ejemplo: {"9:00": [{p1,p2,p3}, {p4,p5,p6}]}
    """
    keys = df_depto.keys()
    turnos = keys[init_franja:init_franja + len(num_trib_por_franja)]
    
    # Debug: mostrar turnos que se están considerando
    # print(f"    Turnos a considerar: {list(turnos)}")
    
    # Construir disponibilidad y participación
    disponibilidad = {}
    participacion = {}
    peso_profesor = {}
    for i in range(df_depto.shape[0]):
        correo = df_depto[keys[1]][i]
        participacion[correo] = df_depto[keys[2]][i]
        valor_peso = df_depto[keys[3]][i] if len(keys) > 3 else 0
        peso_profesor[correo] = valor_peso
        disp = set()
        for turno in turnos:
            valor = df_depto[turno][i]
            if valor == "Sí":
                disp.add(turno)
            # Debug para primer profesor
            '''
            if i == 0:
                print(f"      df_depto[{turno}][{i}] = {repr(valor)}")
            '''
        disponibilidad[correo] = disp

    # Calcular profesores necesarios por turno
    num_prof = {turnos[i]: 3*num_trib_por_franja[i] for i in range(len(num_trib_por_franja))}
    profesores_por_turno = {turno: set() for turno in turnos}

    def compute_holgura():
        """Calcula holgura (disponibles - necesarios) por turno"""
        return {turno: sum(1 for p in disponibilidad if turno in disponibilidad[p]) - num_prof[turno]
                for turno in num_prof}

    holgura = compute_holgura()
    if (min([holgura[turno] for turno in holgura])<0):
        print("Atención: No hay suficientes profesores para cubrir los tribunales necesarios.")
        print("  Detalles de holgura por turno:")
        for turno in holgura:
            disponibles = sum(1 for p in disponibilidad if turno in disponibilidad[p])
            necesarios = num_prof[turno]
            print(f"    {turno}: {disponibles} disponibles - {necesarios} necesarios = {holgura[turno]}")
            # Listar profesores disponibles en este turno
            profes_turno = [p for p in disponibilidad if turno in disponibilidad[p]]
            print(f"      Profesores: {profes_turno[:5]}...")  # mostrar primeros 5

    prof_needed = sum(num_prof.values())

    def peso_prof(correo):
        #Calcula peso: participación previa + peso dado en Excel.
        return participacion[correo] + peso_profesor.get(correo, 0)

    # Algoritmo greedy de asignación de profesores
    # Priorizar turnos que aún necesitan profesores, asignando primero a los que más lo necesitan
    while prof_needed > 0 and num_prof:
        # Turnos con mayor déficit de profesores (menor holgura)
        menor = min(holgura.values())
        turnos_criticos = [t for t in holgura if holgura[t] == menor]
        turno_activo = rnd.choice(turnos_criticos)
        # print(f"    Holgura actual: {menor}, turno {turno_activo}")

        # Profesores disponibles en este turno
        select_prof = [p for p in disponibilidad if turno_activo in disponibilidad[p]]
        if not select_prof:
            print(f"    [WARN] No hay profesores disponibles para el turno {turno_activo}. Saltando turno.")
            break
        
        # Filtrar por menor peso (participación + carga de tutorías)
        min_peso = min(peso_prof(p) for p in select_prof)
        select_prof = [p for p in select_prof if peso_prof(p) == min_peso]
        
        # Filtrar por menor disponibilidad
        min_disp = min(len(disponibilidad[p]) for p in select_prof)
        select_prof = [p for p in select_prof if len(disponibilidad[p]) == min_disp]

        # Seleccionar profesor aleatorio
        prof = rnd.choice(select_prof)
        profesores_por_turno[turno_activo].add(prof)
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

    # Agrupar profesores en tribunales de 3
    tribunales_agrupados = {}
    for i, turno in enumerate(turnos):
        profesores = profesores_por_turno[turno]
        # print(profesores)
        tribunales_agrupados[turno] = agrupar_profesores_en_tribunales(profesores)
        # Debug: mostrar si se crearon menos tribunales de los esperados

    tribunales_creados = len(tribunales_agrupados[turno])

    if tribunales_creados < prof_needed // 3:
        print(f"    [WARN] {turno}: Esperado {prof_needed // 3} tribunales, creado {tribunales_creados} (profesores disponibles: {len(profesores)})")
    
    return tribunales_agrupados