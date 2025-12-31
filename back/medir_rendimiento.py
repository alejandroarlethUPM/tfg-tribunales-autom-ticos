#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import os
import shutil
import warnings

# Suprimir warnings
warnings.filterwarnings("ignore")

# Agregar al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_pipeline

# Cambiar directorio
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def medir_rendimiento(nombre_prueba, directorio_datos, directorio_salida):
    """Mide el rendimiento del pipeline"""
    if os.path.exists(directorio_salida):
        shutil.rmtree(directorio_salida)
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Ejecutar
    inicio = time.time()
    estadisticas = run_pipeline(directorio_datos, directorio_salida, seed=42)
    tiempo_transcurrido = time.time() - inicio
    
    return tiempo_transcurrido, estadisticas

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MEDICIÓN DE RENDIMIENTO - SISTEMA DE ASIGNACIÓN DE TRIBUNALES")
    print("="*70)
    
    # Prueba1: caso real (28 TFGs, 205 profesores)
    print("\nEjecutando prueba1 (28 TFGs, 205 profesores)...")
    tiempo_transcurrido, estadisticas = medir_rendimiento(
        "prueba1",
        "data/prueba1/",
        "outputs/timing_prueba1/"
    )
    
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    print(f"Tiempo total de ejecución: {tiempo_transcurrido:.2f} segundos")
    print(f"Datos procesados: 28 TFGs, 205 profesores")
    if estadisticas:
        print(f"Tribunales creados: {estadisticas.get('total_tribunales', 'N/A')}")
        print(f"Alumnos asignados por departamento:")
        for depto, count in estadisticas.get('alumnos_por_depto', {}).items():
            print(f"  - {depto}: {count}")
    print("="*70)
