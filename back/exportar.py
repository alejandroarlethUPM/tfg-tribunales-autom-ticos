import os
import csv

def exportar_csv_por_grado(todos_tribunales, todas_asignaciones, output_dir):
	"""Genera un CSV por grado con las asignaciones finales."""

	os.makedirs(output_dir, exist_ok=True)

	# Recolectar filas por grado
	rows_por_grado = {}
	for departamento, tribunales in todos_tribunales.items():
		asignacion = todas_asignaciones.get(departamento, {})
		for turno, profes_set in tribunales.items():
			profesores = list(profes_set)
			alumnos = asignacion.get(turno, {})
			for alumno_id, datos in alumnos.items():
				grado = datos.get('grado', 'Desconocido')
				fila = {
					'grado': grado,
					'alumno_id': alumno_id,
					'nombre': datos.get('nombre', ''),
					'departamento_alumno': datos.get('departamento', ''),
					'departamento_tribunal': departamento,
					'turno': str(turno),
					'profesores': ', '.join(profesores),
					'tutores': ', '.join(datos.get('tutores', [])),
				}
				rows_por_grado.setdefault(grado, []).append(fila)

	# Escribir un CSV por grado
	for grado, rows in rows_por_grado.items():
		nombre_archivo = os.path.join(output_dir, f"asignaciones_{grado}.csv")
		with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
			# Usamos ';' como separador para que Excel en español no junte todo en una sola celda
			writer = csv.DictWriter(
				f,
				fieldnames=list(rows[0].keys()),
				delimiter=';',
				quoting=csv.QUOTE_MINIMAL
			)
			writer.writeheader()
			writer.writerows(rows)
		print(f"CSV generado: {nombre_archivo} ({len(rows)} registros)")
