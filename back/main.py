from mapping import build_profesor_departamento  # agregar extraer_correos
from tribunales import crear_tribunales_depto, distribuir_tribunales
from data_io import load_disponibilidad, load_tfgs_por_dptos, read_sheet, get_sheet_names, get_num_rows
from asignacion import cargar_estudiantes, asignar_alumnos_a_tribunales
from optimizacion import rebalancear_tribunales
from agrupacion import agrupar_tfgs_por_departamentos
from exportar import exportar_csv_por_grado

# Suprimir warnings de openpyxl
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Para evitar la creación de archivos .pyc
import sys
sys.dont_write_bytecode = True


# ============================================================================
# CONFIGURACIÓN
# ============================================================================
# Usar rutas relativas para API (se sobrescriben en run_pipeline)
PATH = "C:/Users/A/Desktop/TFG/src/back/data/"
FILENAME_DISPONIBILIDAD = "disponibilidad_TFG.xlsx"
FILENAME = "TFGs_presentados_enviar.xlsx"
FILENAME_TFGS = "TFGs_por_dptos.xlsx"
# Salida de CSVs por grado
OUTPUT_DIR = "C:/Users/A/Desktop/TFG/src/back/outputs/"

# Parámetros de tribunales
INIT_FRANJA = 4  # columna donde comienzan las franjas horarias
NUM_FRANJAS = 5  # número total de franjas horarias
MAX_ESTUDIANTES_POR_TRIBUNAL = 6  # máximo de estudiantes por tribunal
MIN_ESTUDIANTES_POR_TRIBUNAL = 4  # mínimo de estudiantes por tribunal


# ============================================================================
# PIPELINE FUNCTION (reutilizable desde API)
# ============================================================================
def run_pipeline(input_dir, output_dir, seed=42):
    """
    Ejecuta el pipeline completo de creación de tribunales.
    
    Args:
        input_dir (str): ruta al directorio con los Excel de entrada
        output_dir (str): ruta al directorio donde guardar los CSV
        seed (int): semilla para reproducibilidad
    
    Returns:
        dict: estadísticas finales
    """
    import random
    import os
    random.seed(seed)
    
    # Crear directorio output si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Usar input_dir como base
    path = input_dir
    
    # 0. AGRUPAR TFGs POR DEPARTAMENTOS
    print("="*80)
    print("PASO 0: AGRUPANDO TFGs POR DEPARTAMENTOS")
    print("="*80)
    agrupar_tfgs_por_departamentos(path, FILENAME_DISPONIBILIDAD)
    
    print("\n" + "="*80)
    print("SISTEMA DE CREACIÓN DE TRIBUNALES Y ASIGNACIÓN DE ESTUDIANTES")
    print("="*80)
    
    # 1. CARGAR DISPONIBILIDAD DE PROFESORES
    file_disponibilidad = load_disponibilidad(path, FILENAME_DISPONIBILIDAD)
    
    # 2. CONSTRUIR MAPEO PROFESOR → DEPARTAMENTO
    profesor_departamento, profesores_por_dpto = build_profesor_departamento(
        file_disponibilidad, path, FILENAME_DISPONIBILIDAD
    )
    #print(f"    Total de profesores mapeados: {len(profesor_departamento)}")
    #print(f"    Departamentos: {list(profesores_por_dpto.keys())}")
    
    # 3. CARGAR ESTUDIANTES
    file_tfgs = load_tfgs_por_dptos(path, FILENAME_TFGS)
    estudiantes = cargar_estudiantes(file_tfgs)
    #print(f"    Total de estudiantes cargados: {len(estudiantes)}")
    
    # Contar la cantidad de estudiantes por departamento
    estudiantes_por_dpto = {}
    for _, datos in estudiantes.items():
        dpto = datos['departamento']
        if dpto not in estudiantes_por_dpto:
            estudiantes_por_dpto[dpto] = 0
        estudiantes_por_dpto[dpto] += 1
    
    #print("    Estudiantes por departamento:")
    for dpto, count in estudiantes_por_dpto.items():
        #print(f"      - {dpto}: {count}")
        pass
    
    # ========================================================================
    # PROCESAMIENTO POR DEPARTAMENTO
    # ========================================================================
    todos_tribunales = dict()
    todas_asignaciones = dict()
    
    for departamento in get_sheet_names(file_disponibilidad)[:-1]:  # excluir última hoja
        #print(f"\n{'='*80}")
        #print(f"PROCESANDO DEPARTAMENTO: {departamento}")
        #print(f"{'='*80}")
        
        # ---- A. Calcular número de tribunales necesarios ----
        num_estudiantes_dpto = estudiantes_por_dpto.get(departamento, 0)
        
        if num_estudiantes_dpto == 0:
            #print(f"No hay estudiantes en {departamento}, saltando...")
            continue
        
        num_tribunales_necesarios = (num_estudiantes_dpto + MAX_ESTUDIANTES_POR_TRIBUNAL - 1) // MAX_ESTUDIANTES_POR_TRIBUNAL
        #print(f"\n  Estudiantes: {num_estudiantes_dpto}")
        #print(f"  Tribunales necesarios: {num_tribunales_necesarios}")

        # ---- B. Distribuir tribunales entre franjas ----
        num_trib_por_franja = distribuir_tribunales(num_tribunales_necesarios, NUM_FRANJAS)
        #print(f"  Distribución por franja: {num_trib_por_franja}")

        # ---- C. Leer disponibilidad del departamento ----
        df_depto = read_sheet(file_disponibilidad, departamento, header=[0, 1, 2])
        #print(f"  Profesores en el departamento: {get_num_rows(df_depto)}")

        # ---- D. Crear tribunales ----
        #print(f"\n  Creando tribunales...")
        tribunales = crear_tribunales_depto(df_depto, INIT_FRANJA, num_trib_por_franja)
        
        # Estadísticas de tribunales
        for turno, profes in tribunales.items():
            #print(f"    {turno}: {len(profes)} profesores")
            pass
        
        # ---- E. Asignar estudiantes ----
        #print(f"\n  Asignando estudiantes...")
        asignacion = asignar_alumnos_a_tribunales(tribunales, estudiantes, departamento)
        
        # Estadísticas de asignación
        total_asignados = sum(len(alumnos) for alumnos in asignacion.values())
        #print(f"    Total asignados: {total_asignados}/{num_estudiantes_dpto}")
        
        # Guardar resultados
        todos_tribunales[departamento] = tribunales
        todas_asignaciones[departamento] = asignacion

    # ========================================================================
    # REBALANCEO DE TRIBUNALES
    # ========================================================================
    #print(f"\n{'='*80}")
    #print("REBALANCEANDO TRIBUNALES CON POCOS ALUMNOS")
    #print(f"{'='*80}")
    
    todas_asignaciones = rebalancear_tribunales(todos_tribunales, todas_asignaciones)

    # ========================================================================
    # EXPORTAR CSV POR GRADO
    # ========================================================================
    exportar_csv_por_grado(todos_tribunales, todas_asignaciones, output_dir)
    
    # ========================================================================
    # CALCULAR ESTADÍSTICAS FINALES
    # ========================================================================
    total_tribunales = 0
    total_alumnos_asignados = 0
    tribunales_completos = 0
    tribunales_vacios = 0
    
    for departamento in todos_tribunales.keys():
        tribunales = todos_tribunales[departamento]
        asignacion = todas_asignaciones[departamento]
        
        for turno in tribunales.keys():
            profes = list(tribunales[turno])
            alumnos = asignacion.get(turno, {})
            num_prof = len(profes)
            num_alum = len(alumnos)
            
            if num_prof > 0:
                if num_alum == 0:
                    tribunales_vacios += 1
                elif num_alum >= 4:
                    tribunales_completos += 1
                
                total_tribunales += 1
                total_alumnos_asignados += num_alum
    
    # Compilar estadísticas
    stats = {
        'total_tribunales': total_tribunales,
        'tribunales_optimos': tribunales_completos,
        'tribunales_vacios': tribunales_vacios,
        'total_alumnos_asignados': total_alumnos_asignados,
        'promedio_alumnos_tribunal': round(total_alumnos_asignados / total_tribunales, 2) if total_tribunales > 0 else 0
    }
    
    print(f"\n{'='*80}")
    print("ESTADÍSTICAS GLOBALES")
    print(f"{'='*80}")
    print(f"  Total tribunales activos: {stats['total_tribunales']}")
    print(f"  Tribunales óptimos (≥4 alumnos): {stats['tribunales_optimos']}")
    print(f"  Tribunales vacíos: {stats['tribunales_vacios']}")
    print(f"  Total alumnos asignados: {stats['total_alumnos_asignados']}")
    print(f"  Promedio alumnos/tribunal: {stats['promedio_alumnos_tribunal']}")
    
    print(f"\n{'='*80}")
    print("PROCESO COMPLETADO")
    print(f"{'='*80}\n")
    
    return stats


def main():
    """Ejecuta el pipeline con configuraci�n por defecto."""
    run_pipeline(PATH, OUTPUT_DIR, seed=42)


if __name__ == "__main__":
    main()
