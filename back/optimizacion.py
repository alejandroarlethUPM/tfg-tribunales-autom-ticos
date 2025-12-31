import random

def rebalancear_tribunales(todos_tribunales, todas_asignaciones, min_alumnos=4, max_alumnos=6):
    """
    Redistribuye alumnos entre tribunales con pocos estudiantes.
    Mezcla departamentos y turnos si es necesario para alcanzar mínimo de 4 alumnos.
    
    Args:
        todos_tribunales (dict): departamento → {turno → set profesores}
        todas_asignaciones (dict): departamento → {turno → {alumno: datos}}
        min_alumnos (int): objetivo mínimo de alumnos por tribunal
        max_alumnos (int): máximo de alumnos por tribunal
    
    Returns:
        dict: nuevas asignaciones optimizadas
    """
    from collections import defaultdict
    
    # 1. Identificar tribunales con pocos alumnos y recolectar pool global
    tribunales_info = []
    pool_alumnos = []
    
    for dept, asignacion in todas_asignaciones.items():
        tribunales = todos_tribunales[dept]
        for turno, alumnos in asignacion.items():
            num_prof = len(tribunales[turno])
            num_alum = len(alumnos)
            
            # Solo considerar tribunales con profesores
            if num_prof > 0:
                tribunales_info.append({
                    'departamento': dept,
                    'turno': turno,
                    'profesores': list(tribunales[turno]),
                    'num_alumnos': num_alum,
                    'num_prof': num_prof
                })
                
                # Si tiene <=3 alumnos, todos van al pool
                if num_alum <= 3:
                    for alumno_id, datos in alumnos.items():
                        pool_alumnos.append({
                            'id': alumno_id,
                            'datos': datos
                        })
    
    print(f"\n  Tribunales con <=3 alumnos: {sum(1 for t in tribunales_info if t['num_alumnos'] <= 3)}")
    print(f"  Alumnos a redistribuir: {len(pool_alumnos)}")
    
    # 2. Filtrar tribunales que necesitan rebalanceo
    tribunales_rebalancear = [t for t in tribunales_info if t['num_alumnos'] <= 3]
    
    # 3. Crear nuevas asignaciones (copiar las existentes primero)
    nuevas_asignaciones = {}
    for dept, asig in todas_asignaciones.items():
        nuevas_asignaciones[dept] = {}
        for turno, alumnos in asig.items():
            num_prof = len(todos_tribunales[dept][turno])
            num_alum = len(alumnos)
            # Copiar tribunales con >3 alumnos o sin profesores
            if num_alum > 3 or num_prof == 0:
                nuevas_asignaciones[dept][turno] = dict(alumnos)
            else:
                # Vaciar los que vamos a rebalancear
                nuevas_asignaciones[dept][turno] = {}
    
    # 4. Mezclar alumnos aleatoriamente
    random.shuffle(pool_alumnos)
    
    print(f"\n  Redistribuyendo {len(pool_alumnos)} alumnos entre {len(tribunales_rebalancear)} tribunales...")
    
    # 5. Redistribuir globalmente (sin restricción de turno)
    idx = 0

    for trib in tribunales_rebalancear:
        dept = trib['departamento']
        turno = trib['turno']
        profesores = trib['profesores']
        asignados = 0
        
        # Intentar asignar hasta max_alumnos
        while idx < len(pool_alumnos) and asignados < max_alumnos:
            alumno = pool_alumnos[idx]
            
            # Verificar restricción: tutor no en tribunal
            if not any(t in profesores for t in alumno['datos']['tutores']):
                nuevas_asignaciones[dept][turno][alumno['id']] = alumno['datos']
                asignados += 1
                pool_alumnos.pop(idx)  # Eliminar alumno del pool
            else:
                # Intentar con el siguiente alumno
                idx += 1
                if idx >= len(pool_alumnos):
                    idx = 0  # Volver al principio del pool
        
        print(f"    {dept} - {turno}: {asignados} alumnos asignados")
        idx = 0  # Resetear para el siguiente tribunal
    
    # 6. Si quedan alumnos sin asignar (casos extremos), forzar asignación
    if pool_alumnos:
        print(f"\n  ⚠️  Alumnos sin asignar tras rebalanceo")
        for alumno in pool_alumnos:
            print(alumno)
    return nuevas_asignaciones
