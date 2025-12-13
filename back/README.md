# Backend - API Tribunales TFG

API FastAPI para procesar tribunal y asignar estudiantes automáticamente.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`
Documentación interactiva: `http://localhost:8000/docs`

## Endpoints

### GET `/salud`
Verifica que la API esté activa.

**Respuesta:**
```json
{
  "status": "ok",
  "mensaje": "API de tribunales activa"
}
```

### POST `/procesar`
Procesa los archivos Excel y genera tribunales.

**Parámetros:**
- `disponibilidad` (file): Excel con disponibilidad de profesores
- `tfgs` (file): Excel con TFGs presentados
- `seed` (int, optional): Semilla para reproducibilidad (default: 42)

**Respuesta:**
- ZIP con CSVs de asignaciones por grado + estadísticas.json

## Configuración

Variables de entorno opcionales en `.env`:
```
API_HOST=0.0.0.0
API_PORT=8000
```

## Estructura

- `main.py`: Lógica principal del pipeline (función `run_pipeline()`)
- `api.py`: Endpoints FastAPI
- `agrupacion.py`: Agrupación de TFGs por departamento
- `mapping.py`: Mapeo profesor-departamento
- `tribunales.py`: Creación de tribunales
- `asignacion.py`: Asignación de estudiantes
- `optimizacion.py`: Rebalanceo de tribunales
- `exportar.py`: Exportación a CSV
- `data_io.py`: Lectura de archivos Excel
- `data/`: Directorio con archivos Excel de entrada
- `outputs/`: Directorio con CSVs generados
