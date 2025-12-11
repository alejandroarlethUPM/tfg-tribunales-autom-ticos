"""
Este programa agrupa los TFGs por departamento. La intención es intentar que los
tribunales que se formen sean lo más afines posibles.

Tiene dos inputs:
  1. El excel con la disponiblidad de los profesores de TODOS los departamentos.
  Aquí únicamente usamos la lista de sus correos electrónicos y el departamento
  al que están adscritos
  2. El excel con los TFGs que tienen que ser defendidos. Estos se han
  descargado de la aplicación en TFGs entregados.
El output es un excel donde cada hoja contiene los TFGs de cada departamento.

TODO: en el excel con los TFGs, el dato de los tutores aparecen (cuando hay
cotutela) dos direcciones de correo. Se tiene en cuenta el primero que aparece.
Esto es un problema porque puede ocurrir que tutor y cotutor no sean del mismo
departamento y se adscriba la tutela al departamento del cotutor y no del tutor,
que es el objetivo.

"""

import pandas as pd

import random as rnd

"""
Vamos a crear una base de datos de profesores agrupados por el departamento al que pertenecen

Nos será útil para determinar de qué departamento es ciertos TFGs para asignarle así un tribunal más o menos afín
"""

path = "C:/Users/A/Desktop/TFG/src/"

# Escribimos dobles barras invertidas al final para que lo entiende python

filename = "disponibilidad_TFG.xlsx"

file = path + filename

# file = "C:/Users/Jon/Nextcloud/TFG_Coordinación/Tribunales/disponibilidad_TFG.xlsx"

""" 
Las claves de las columnas
  0 = apellidos y nombre del profesor
  1 = correo electrónico del profesor
  2 = el número de veces que ha participado en un tribunal
  3 - 5 = primer día
  6 - 9 = segundo día
  10 - 12 = tercer día
"""

df = pd.ExcelFile(file)
# Se imprimen los departamentos
print(df.sheet_names)

profesores = dict()
# Se recorren todas las hojas (todos los departamentos) excepto la última
for sheetname in df.sheet_names[:-1]:
    # Se lee la hoja en cuestión
    # Tiene tres filas de encabezado antes de empezar con los datos: Nombre, correo y número de veces que ha participado
    pf = pd.read_excel(file, header=[0,1,2], sheet_name=sheetname)
    # keys = pf.keys()
    dpto = list()
    # pf.shape devuelve una tupla con el número de filas y columnas, pf.shape[0], número de filas
    for i in range(pf.shape[0]):
        # Se incluyen todos los profesores (segunda columna) de un departamento
        # pf.keys()[1] = Correo @fi.upm.es
        # pf.keys()[1][i] Intentaría acceder al iésimo carácter del nombre de la columna
        dpto.append(pf[pf.keys()[1]][i])
    # Se incluye la lista de profesores por departamento
    profesores.update({sheetname: dpto})

# Se crea una lista de los departamentos
dptos = profesores.keys()

"""
Cargamos nuevo fichero donde están los TFGs que se han presentado en este semestre
"""

filename = "TFGs_presentados_enviar.xlsx"

file = path + filename

"""
Claves de las columnas:
    0 = Entrega (ID)
    1 = Trabajo (ID)
    2 = Alumno (nombre y apellidos)
    3 = AlumnoEmail (correo @alumnos.upm.es)
    4 = Matricula (correo sin @)
    5 = Título (del trabajo)
    6 = Tutor-es (correo y nombre de los tutores)
"""

st = pd.read_excel(file, header=0)

# Cargamos todos los TFGs que tienen que defender este semestre

defensas = list()
for i in range(st.shape[0]):
    tfg = dict()
    for key in st.keys()[:7]:
        tfg.update({key: st[key][i]})
    defensas.append(tfg)

# Agrupamos por los departamentos los TFGs

defensas_gather = dict()
for dpto in dptos:
    defensas_gather.update( {dpto: list()} ) # Crea una lista por cada departamento para agrupar los tfgs

for tfg in defensas:
    found = False
    print("\n\tTutor de la propuesta: ", tfg[st.keys()[6]])
    for dpto in dptos:
        for prof in profesores[dpto]:   # Se recorren todos los profesores por cada departamento
            if prof in tfg[st.keys()[6]]:   # Se ve si el profesor es tutor de un trabajo
                found = True
                print("\t\tTrabajo tutorizado por el profesor ", prof, " del departamento ", dpto)
                defensas_gather[dpto].append(tfg)
                break
        if found: 
            break

print("\n\n\n")

# Se imprime la cantidad de TFGs que dirige cada departamento
for key in defensas_gather:
    print(" El departamento ", key," ha dirigido ", len(defensas_gather[key]), " trabajos.")


filename = "TFGs_por_dptos.xlsx"

file = path + filename

# writer = pd.ExcelWriter(file, engine = 'openpyxl')
writer = pd.ExcelWriter(file, engine = 'xlsxwriter')

# Se escribe, siendo cada hoja un departamento, los TFGs que dirige cada una
for dpto in defensas_gather:
    df = pd.DataFrame(defensas_gather[dpto])
    df.to_excel(writer, sheet_name=dpto)

writer.close()