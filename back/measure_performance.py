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

def measure_performance(prueba_name, data_dir, output_dir):
    """Mide el rendimiento del pipeline"""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Ejecutar
    inicio = time.time()
    stats = run_pipeline(data_dir, output_dir, seed=42)
    elapsed = time.time() - inicio
    
    return elapsed, stats

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MEDICIN DE RENDIMIENTO - SISTEMA DE ASIGNACION DE TRIBUNALES")
    print("="*70)
    
    # Prueba1: caso real (28 TFGs, 205 profesores)
    print("\nEjecutando prueba1 (28 TFGs, 205 profesores)...")
    elapsed, stats = measure_performance(
        "prueba1",
        "data/prueba1/",
        "outputs/timing_prueba1/"
    )
    
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    print(f"Tiempo total de ejecucion: {elapsed:.2f} segundos")
    print(f"Datos procesados: 28 TFGs, 205 profesores")
    if stats:
        print(f"Tribunales creados: {stats.get('total_tribunales', 'N/A')}")
        print(f"Alumnos asignados por departamento:")
        for depto, count in stats.get('alumnos_por_depto', {}).items():
            print(f"  - {depto}: {count}")
    print("="*70)
