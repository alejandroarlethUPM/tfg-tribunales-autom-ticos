import random
from collections import defaultdict, Counter


def rebalancear_tribunales(asignaciones, todos_estudiantes, 
                           disponibilidad_profesores, profesor_departamento,
                           min_alumnos=4, max_alumnos=6):
    """
    Redistribuye alumnos entre tribunales con pocos estudiantes.
    Después reajusta profesores según departamentos de alumnos.
    
    Args:
        asignaciones (dict): turno → list[{'profesores': set, 'alumnos': dict}]
                            Estructura plana sin dimensión de departamento
        todos_estudiantes (dict): alumno_id → {departamento, tutores, ...}
        disponibilidad_profesores (dict): {turno: {departamento: [(profesor, disponibilidad_count)]}}
        profesor_departamento (dict): {profesor: departamento}
        min_alumnos (int): objetivo mínimo de alumnos por tribunal
        max_alumnos (int): máximo de alumnos por tribunal
    
    Returns:
        dict: asignaciones rebalanceadas con misma estructura que entrada
    """
    
    # 1. Construir mapeo alumno → departamento
    alumno_depto = {}
    for alumno_id, datos in todos_estudiantes.items():
        alumno_depto[alumno_id] = datos.get('departamento', 'desconocido')
    
    # 2. Identificar tribunales con pocos alumnos y recolectar pool global
    tribunales_info = []
    pool_alumnos = []
    
    for turno, lista_asignaciones in asignaciones.items():
        # Iterar sobre cada tribunal (con índice)
        for idx_trib, tribunal_data in enumerate(lista_asignaciones):
            profesores = tribunal_data['profesores']
            alumnos = tribunal_data['alumnos']
            
            num_prof = len(profesores)
            num_alum = len(alumnos)
            
            # Solo considerar tribunales con profesores
            if num_prof > 0:
                tribunales_info.append({
                    'turno': turno,
                    'idx_trib': idx_trib,
                    'profesores': profesores,
                    'num_alumnos': num_alum,
                    'num_prof': num_prof
                })
                
                # Si tiene <=3 alumnos, todos van al pool
                if num_alum <= 3:
                    for alumno_id, datos in alumnos.items():
                        dept = alumno_depto.get(alumno_id, datos.get('departamento', 'desconocido'))
                        pool_alumnos.append({
                            'id': alumno_id,
                            'datos': datos,
                            'depto': dept
                        })
    
    print(f"\n  Tribunales con <=3 alumnos: {sum(1 for t in tribunales_info if t['num_alumnos'] <= 3)}")
    print(f"  Alumnos a redistribuir: {len(pool_alumnos)}")
    
    # 2b. Buscar alumnos que no fueron asignados a ningún tribunal
    alumnos_asignados = set()
    for turno, lista_asignaciones in asignaciones.items():
        for tribunal_data in lista_asignaciones:
            alumnos_asignados.update(tribunal_data['alumnos'].keys())
    
    alumnos_no_asignados = [
        alumno_id for alumno_id in todos_estudiantes.keys()
        if alumno_id not in alumnos_asignados
    ]
    
    if alumnos_no_asignados:
        print(f"  Alumnos sin asignar a ningún tribunal: {len(alumnos_no_asignados)}")
        for alumno_id in alumnos_no_asignados:
            datos = todos_estudiantes[alumno_id]
            dept = alumno_depto.get(alumno_id, datos.get('departamento', 'desconocido'))
            pool_alumnos.append({
                'id': alumno_id,
                'datos': datos,
                'depto': dept
            })
    
    # 3. Filtrar y ordenar tribunales que necesitan rebalanceo
    tribunales_rebalancear = sorted(
        [t for t in tribunales_info if t['num_alumnos'] <= 3],
        key=lambda t: t['num_alumnos']
    )
    
    # 4. Crear nuevas asignaciones (copiar las existentes primero)
    nuevas_asignaciones = {}
    for turno, lista_asignaciones in asignaciones.items():
        nuevas_asignaciones[turno] = []
        for tribunal_data in lista_asignaciones:
            profesores = tribunal_data['profesores']
            alumnos = tribunal_data['alumnos']
            num_prof = len(profesores)
            num_alum = len(alumnos)
            
            # Copiar tribunales con >3 alumnos o sin profesores
            if num_alum > 3 or num_prof == 0:
                nuevas_asignaciones[turno].append({
                    'profesores': set(profesores),
                    'alumnos': dict(alumnos)
                })
            else:
                # Vaciar los que vamos a rebalancear
                nuevas_asignaciones[turno].append({
                    'profesores': set(profesores),
                    'alumnos': {}
                })
    
    # 5. Mezclar alumnos aleatoriamente
    random.shuffle(pool_alumnos)
    
    print(f"\n  Redistribuyendo {len(pool_alumnos)} alumnos entre tribunales...")
    
    # 6. FASE A: Llenar tribunales que ya tienen alumnos (>3 y <max_alumnos)
    print(f"\n  FASE A: Llenando tribunales con 4-{max_alumnos-1} alumnos...")
    tribunales_para_llenar = sorted(
        [t for t in tribunales_info if 3 < t['num_alumnos'] < max_alumnos],
        key=lambda t: t['num_alumnos']
    )
    
    idx = 0
    tribunales_modificados = set()  # Rastrear (turno, idx_trib) modificados
    
    for trib in tribunales_para_llenar:
        turno = trib['turno']
        idx_trib = trib['idx_trib']
        profesores = trib['profesores']
        
        tribunal_data = nuevas_asignaciones[turno][idx_trib]
        num_alumnos_actual = len(tribunal_data['alumnos'])
        asignados = 0
        
        # Intentar llenar hasta max_alumnos
        while idx < len(pool_alumnos) and num_alumnos_actual + asignados < max_alumnos:
            alumno = pool_alumnos[idx]
            
            # Verificar restricción: tutor no en tribunal
            if not any(t in profesores for t in alumno['datos']['tutores']):
                alumno_id = alumno['id']
                tribunal_data['alumnos'][alumno_id] = alumno['datos']
                asignados += 1
                pool_alumnos.pop(idx)
            else:
                idx += 1
                if idx >= len(pool_alumnos):
                    break
        
        if asignados > 0:
            print(f"    {turno} [Trib {idx_trib+1}]: +{asignados} alumnos (total: {num_alumnos_actual + asignados})")
            tribunales_modificados.add((turno, idx_trib))
        idx = 0
    
    # 7. FASE B: Redistribuir entre tribunales con <=3 alumnos
    print(f"\n  FASE B: Redistribuyendo en tribunales con <=3 alumnos...")
    
    idx = 0
    for trib in tribunales_rebalancear:
        turno = trib['turno']
        idx_trib = trib['idx_trib']
        profesores = trib['profesores']
        
        tribunal_data = nuevas_asignaciones[turno][idx_trib]
        asignados = 0
        
        # Intentar llenar hasta min_alumnos
        while idx < len(pool_alumnos) and len(tribunal_data['alumnos']) < min_alumnos:
            alumno = pool_alumnos[idx]
            
            # Verificar restricción: tutor no en tribunal
            if not any(t in profesores for t in alumno['datos']['tutores']):
                alumno_id = alumno['id']
                tribunal_data['alumnos'][alumno_id] = alumno['datos']
                asignados += 1
                pool_alumnos.pop(idx)
            else:
                idx += 1
                if idx >= len(pool_alumnos):
                    break
        
        if asignados > 0:
            print(f"    {turno} [Trib {idx_trib+1}]: {len(tribunal_data['alumnos'])} alumnos asignados")
            tribunales_modificados.add((turno, idx_trib))
        idx = 0
    
    # 8. FASE C: Tomar alumnos de tribunales con 6 para llenar los que tienen <=3
    print(f"\n  FASE C: Tomando alumnos de tribunales completos (6 alumnos)...")
    
    tribunales_con_6 = [t for t in tribunales_info if t['num_alumnos'] == max_alumnos]
    tribunales_incompletos = []
    
    for turno, lista_asignaciones in nuevas_asignaciones.items():
        for idx_trib, tribunal_data in enumerate(lista_asignaciones):
            num_alum = len(tribunal_data['alumnos'])
            if 0 < num_alum < min_alumnos:
                tribunales_incompletos.append({
                    'turno': turno,
                    'idx_trib': idx_trib,
                    'num_alumnos': num_alum,
                    'profesores': tribunal_data['profesores']
                })
    
    if tribunales_incompletos and tribunales_con_6:
        print(f"    Tribunales completos disponibles: {len(tribunales_con_6)}")
        print(f"    Tribunales incompletos: {len(tribunales_incompletos)}")
        
        for trib_incompleto in tribunales_incompletos:
            turno_dest = trib_incompleto['turno']
            idx_dest = trib_incompleto['idx_trib']
            profes_dest = trib_incompleto['profesores']
            tribunal_dest = nuevas_asignaciones[turno_dest][idx_dest]
            
            # Cuántos alumnos necesita
            necesarios = min_alumnos - len(tribunal_dest['alumnos'])
            
            # Buscar alumnos en tribunales con 6
            for trib_origen in tribunales_con_6:
                if necesarios <= 0:
                    break
                
                turno_origen = trib_origen['turno']
                idx_origen = trib_origen['idx_trib']
                tribunal_origen = nuevas_asignaciones[turno_origen][idx_origen]
                
                # Sacar alumnos que no sean tutores en destino
                alumnos_movibles = [
                    (alumno_id, datos) 
                    for alumno_id, datos in tribunal_origen['alumnos'].items()
                    if not any(t in profes_dest for t in datos.get('tutores', []))
                ]
                
                # Mover alumnos
                moved = 0
                for alumno_id, datos in alumnos_movibles[:necesarios]:
                    tribunal_dest['alumnos'][alumno_id] = datos
                    del tribunal_origen['alumnos'][alumno_id]
                    moved += 1
                    necesarios -= 1
                
                if moved > 0:
                    print(f"      {turno_origen} [Trib {idx_origen+1}] → {turno_dest} [Trib {idx_dest+1}]: {moved} alumnos movidos")
        
        # Intentar asignar hasta max_alumnos
        while idx < len(pool_alumnos) and asignados < max_alumnos:
            alumno = pool_alumnos[idx]
            
            # Verificar restricción: tutor no en tribunal
            if not any(t in profesores for t in alumno['datos']['tutores']):
                alumno_id = alumno['id']
                tribunal_data['alumnos'][alumno_id] = alumno['datos']
                asignados += 1
                pool_alumnos.pop(idx)
            else:
                idx += 1
                if idx >= len(pool_alumnos):
                    idx = 0
        
        if asignados > 0:
            print(f"    {turno} [Trib {idx_trib+1}]: {asignados} alumnos asignados")
            tribunales_modificados.add((turno, idx_trib))
        idx = 0

    '''
    # 8. Reajustar profesores según departamentos de alumnos asignados (solo tribunales modificados)
    print(f"\n  Reajustando profesores según departamentos de alumnos...")
    
    for turno, lista_asignaciones in nuevas_asignaciones.items():
        for idx_trib, tribunal_data in enumerate(lista_asignaciones):
            # Solo reajustar si este tribunal fue modificado
            if (turno, idx_trib) not in tribunales_modificados:
                continue
            
            alumnos_nuevo = tribunal_data['alumnos']
            
            if len(alumnos_nuevo) == 0:
                continue
            
            # Contar alumnos por departamento
            alumnos_por_depto = Counter()
            for alumno_id in alumnos_nuevo.keys():
                alumno_d = alumno_depto.get(alumno_id, 'desconocido')
                alumnos_por_depto[alumno_d] += 1
            
            # Buscar profesores disponibles en este turno
            if turno not in disponibilidad_profesores:
                continue
            
            num_prof_necesarios = 3
            profesores_finales = []
            tutores_en_alumnos = set()
            for datos_alumno in alumnos_nuevo.values():
                tutores_en_alumnos.update(datos_alumno.get('tutores', []))
            
            # Asignar profesores por departamento según proporción de alumnos
            for depto_alumno, num_alumnos in alumnos_por_depto.most_common():
                num_prof_asignar = max(1, round(num_prof_necesarios * num_alumnos / len(alumnos_nuevo)))
                
                # Buscar profesores del departamento disponibles en este turno
                if depto_alumno not in disponibilidad_profesores[turno]:
                    continue
                
                # Filtrar profesores: no deben ser tutores y no deben estar ya asignados
                candidatos = [
                    (prof, disp_count) 
                    for prof, disp_count in disponibilidad_profesores[turno][depto_alumno]
                    if prof not in tutores_en_alumnos and prof not in profesores_finales
                ]
                
                if not candidatos:
                    continue
                
                # Ordenar por menor disponibilidad (menos turnos disponibles = más comprometido)
                candidatos.sort(key=lambda x: x[1])
                
                # Seleccionar los mejores candidatos
                for i in range(min(num_prof_asignar, len(candidatos))):
                    profesores_finales.append(candidatos[i][0])
                    if len(profesores_finales) >= num_prof_necesarios:
                        break
                
                if len(profesores_finales) >= num_prof_necesarios:
                    break
            
            # Si no llegamos a 3, intentar con cualquier profesor disponible
            if len(profesores_finales) < num_prof_necesarios:
                for depto in disponibilidad_profesores[turno]:
                    for prof, disp_count in disponibilidad_profesores[turno][depto]:
                        if prof not in tutores_en_alumnos and prof not in profesores_finales:
                            profesores_finales.append(prof)
                            if len(profesores_finales) >= num_prof_necesarios:
                                break
                    if len(profesores_finales) >= num_prof_necesarios:
                        break
            
            # Actualizar profesores en las asignaciones
            if profesores_finales:
                tribunal_data['profesores'] = set(profesores_finales[:num_prof_necesarios])
                print(f"    {turno} [Trib {idx_trib+1}]: Profesores reajustados (principal: {alumnos_por_depto.most_common(1)[0][0]})")
    '''    
    # 9. Si quedan alumnos sin asignar (casos extremos)
    if pool_alumnos:
        print(f"\n  ⚠️  Alumnos sin asignar tras rebalanceo: {len(pool_alumnos)}")
    
    return nuevas_asignaciones
