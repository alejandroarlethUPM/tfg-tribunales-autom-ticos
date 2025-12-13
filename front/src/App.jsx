import { useState } from 'react'
import './App.css'

function App() {
  const [disponibilidad, setDisponibilidad] = useState(null)
  const [tfgs, setTfgs] = useState(null)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [zipUrl, setZipUrl] = useState(null)

  const handleFileChange = (e, type) => {
    const file = e.target.files[0]
    if (type === 'disponibilidad') {
      setDisponibilidad(file)
    } else {
      setTfgs(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!disponibilidad || !tfgs) {
      setError('Por favor sube ambos archivos Excel')
      return
    }

    setLoading(true)
    setError(null)
    setStats(null)
    setZipUrl(null)

    const formData = new FormData()
    formData.append('disponibilidad', disponibilidad)
    formData.append('tfgs', tfgs)
    formData.append('seed', 42)

    try {
      const response = await fetch('http://localhost:8000/procesar', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error en el servidor')
      }

      // Descargar ZIP
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'resultados_tribunales.zip'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Mostrar estadísticas (aquí podríamos parsear el JSON del ZIP)
      setStats({
        total_tribunales: 'Descargado',
        tribunales_optimos: 'Ver archivo',
        tribunales_vacios: 'CSV adjunto',
        total_alumnos_asignados: '✓',
        promedio_alumnos_tribunal: 'Completado'
      })
    } catch (err) {
      setError(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🎓 Asignación Automática de Tribunales TFG</h1>
        <p>Sistema de creación de tribunales para trabajos de fin de grado</p>
      </header>

      <main className="main">
        {/* Formulario de subida */}
        <section className="upload-section">
          <h2>Paso 1: Sube los archivos Excel</h2>
          <form onSubmit={handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="disponibilidad">
                📋 Disponibilidad de Profesores
              </label>
              <input
                type="file"
                id="disponibilidad"
                accept=".xlsx"
                onChange={(e) => handleFileChange(e, 'disponibilidad')}
                disabled={loading}
              />
              {disponibilidad && <p className="file-name">✓ {disponibilidad.name}</p>}
            </div>

            <div className="form-group">
              <label htmlFor="tfgs">
                📚 TFGs Presentados
              </label>
              <input
                type="file"
                id="tfgs"
                accept=".xlsx"
                onChange={(e) => handleFileChange(e, 'tfgs')}
                disabled={loading}
              />
              {tfgs && <p className="file-name">✓ {tfgs.name}</p>}
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="btn-submit"
            >
              {loading ? '⏳ Procesando...' : '🚀 Generar Tribunales'}
            </button>
          </form>
        </section>

        {/* Mostrar error */}
        {error && (
          <section className="error-section">
            <h2>❌ Error</h2>
            <p>{error}</p>
          </section>
        )}

        {/* Mostrar estadísticas */}
        {stats && (
          <section className="stats-section">
            <h2>✅ Resultados</h2>
            <div className="download-section">
              <p>📦 ¡Tribunales generados exitosamente!</p>
              <p className="info">El archivo ZIP ha sido descargado automáticamente</p>
              <p className="success-msg">Contiene los CSVs con las asignaciones por grado</p>
            </div>
          </section>
        )}

        {/* Instrucciones */}
        {!stats && (
          <section className="info-section">
            <h2>📖 Instrucciones</h2>
            <ol>
              <li>Descarga el Excel de disponibilidad de profesores</li>
              <li>Descarga el Excel con los TFGs presentados</li>
              <li>Sube ambos archivos en este formulario</li>
              <li>Haz clic en "Generar Tribunales"</li>
              <li>Descarga los CSVs con las asignaciones por grado</li>
            </ol>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Sistema de Asignación de Tribunales TFG - 2025</p>
      </footer>
    </div>
  )
}

export default App
