"""
API FastAPI para procesar tribunales desde la web.
Recibe Excel de entrada, ejecuta el pipeline y devuelve ZIP con CSV resultados.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import os
from pathlib import Path
import zipfile
import json
import io

# Importar funciones del pipeline
import sys
sys.path.append(os.path.dirname(__file__))

from main import run_pipeline

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
app = FastAPI(
    title="API Tribunales TFG",
    description="Asignación automática de tribunales para TFGs",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde localhost:5173 (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/salud")
async def health_check():
    """Endpoint para verificar que la API está corriendo."""
    return {"status": "ok", "mensaje": "API de tribunales activa"}


@app.post("/procesar")
async def procesar_tribunales(
    disponibilidad: UploadFile = File(...),
    tfgs: UploadFile = File(...),
    seed: int = 42
):
    """
    Procesa los archivos Excel de disponibilidad y TFGs.
    Devuelve ZIP con CSVs generados.
    
    Parameters:
        - disponibilidad: Excel con disponibilidad de profesores
        - tfgs: Excel con TFGs presentados
        - seed: Semilla para reproducibilidad (default: 42)
    
    Returns:
        - ZIP file con CSVs + estadísticas.json
    """
    temp_input_dir = None
    temp_output_dir = None
    
    try:
        # 1. Crear directorios temporales
        temp_input_dir = tempfile.mkdtemp()
        temp_output_dir = tempfile.mkdtemp()
        
        # 2. Guardar archivos subidos
        disponibilidad_path = Path(temp_input_dir) / "disponibilidad_TFG.xlsx"
        tfgs_path = Path(temp_input_dir) / "TFGs_presentados_enviar.xlsx"
        
        with open(disponibilidad_path, "wb") as f:
            f.write(await disponibilidad.read())
        
        with open(tfgs_path, "wb") as f:
            f.write(await tfgs.read())
        
        # 3. Ejecutar pipeline
        stats = run_pipeline(str(temp_input_dir) + "/", str(temp_output_dir) + "/", seed=seed)
        
        # 4. Crear ZIP en memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Agregar CSVs
            for csv_file in Path(temp_output_dir).glob("asignaciones_*.csv"):
                with open(csv_file, "rb") as f:
                    zipf.writestr(csv_file.name, f.read())
            # Agregar estadísticas
            stats_json = json.dumps(stats, indent=2, ensure_ascii=False)
            zipf.writestr("estadisticas.json", stats_json)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=resultados_tribunales.zip"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando: {str(e)}")
    
    finally:
        # Cerrar explícitamente los uploads y limpiar temporales (ignorar bloqueos en Windows)
        try:
            await disponibilidad.close()
        except Exception:
            pass
        try:
            await tfgs.close()
        except Exception:
            pass

        if temp_input_dir and os.path.exists(temp_input_dir):
            shutil.rmtree(temp_input_dir, ignore_errors=True)
        if temp_output_dir and os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir, ignore_errors=True)


@app.get("/descargar")
async def descargar_resultados():
    """
    Endpoint para descargar el ZIP con resultados.
    (En producción, guardarías el ZIP en servidor y lo servirías aquí)
    """
    return JSONResponse(
        {"mensaje": "Usar el ZIP devuelto en /procesar"}
    )


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
