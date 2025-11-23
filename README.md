# Flask + Vue.js AI Prompt Application

A simple web application with a Flask backend and Vue.js frontend that allows users to input prompts and receive AI-generated outputs.

## Project Structure

```
hackEPS_2025/
├── server/          # Flask backend
└── client/          # Vue.js frontend
```

## Prerequisites

- Python 3.12.3
- Node.js (v16 or higher recommended)
- npm or yarn
- Anaconda (optional, for environment management)

## Setup

### Option 1: Using Anaconda (Recommended)

1. **Create Conda Environment**

   ```bash
   conda create -n hackeps python=3.12.3
   conda activate hackeps
   ```
2. **Install Python Dependencies**

   ```bash
   cd server
   pip install -r requirements.txt
   ```
3. **Install Node Dependencies**

   ```bash
   cd ../client
   npm install
   ```

### Option 2: Using Python venv

1. **Create Virtual Environment**

   ```bash
   python -m venv venv
   ```
2. **Activate Virtual Environment**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
3. **Install Python Dependencies**

   ```bash
   cd server
   pip install -r requirements.txt
   ```
4. **Install Node Dependencies**

   ```bash
   cd ../client
   npm install
   ```

## Running the Application

### Start the Backend (Flask)

1. Activate your environment (conda or venv)
2. Navigate to the server directory:
   ```bash
   cd server
   python app.py
   ```

   The Flask server will start on `http://localhost:5000`

### Start the Frontend (Vue.js)

1. Open a new terminal
2. Navigate to the client directory:
   ```bash
   cd client
   npm run dev
   ```

   The Vue.js development server will start on `http://localhost:5173`

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Enter your prompt in the input field
3. Click the "Generate" button to get AI output
4. Use the "Refresh" button to clear the form and start over

## Development

### Backend Structure

- `server/app.py` - Main Flask application
- `server/requirements.txt` - Python dependencies

### Frontend Structure

- `client/src/App.vue` - Main Vue component
- `client/src/main.js` - Vue application entry point
- `client/package.json` - Node dependencies

## API Endpoints

- `POST /api/generate` - Submit a prompt and receive AI-generated output
  - Request body: `{ "prompt": "your prompt here" }`
  - Response: `{ "output": "AI generated response" }`




# Instrucciones para usar el Mapa de Calor

## Descripción

El mapa de calor compara las preferencias del usuario (generadas por la IA) con cada zona de Los Ángeles, mostrando visualmente las áreas más adecuadas según sus necesidades.

## Cómo usar

### 1. Generar Vector de Preferencias

En el panel izquierdo "AI Assistant":

1. Escribe una descripción de tus necesidades (ejemplo: "Soy estudiante, necesito una zona tranquila con buen internet y cerca de universidades")
2. Haz clic en "Generate"
3. La IA generará un vector de 11 valores que representa tus preferencias

### 2. Visualizar el Mapa de Calor

1. Después de generar el vector, el mapa de calor se carga automáticamente
2. En el panel derecho "Filtros", haz clic en "Mostrar Mapa de Calor"
3. El mapa mostrará colores que indican la coincidencia:
   - **Azul**: Baja coincidencia (30-40%)
   - **Cyan**: Coincidencia baja-media (40-50%)
   - **Verde**: Coincidencia media (50-60%)
   - **Amarillo-Verde**: Buena coincidencia (60-70%)
   - **Amarillo**: Muy buena coincidencia (70-80%)
   - **Naranja**: Excelente coincidencia (80-90%)
   - **Rojo**: Coincidencia perfecta (90-100%)

### 3. Explorar Resultados

- Haz clic en cualquier área coloreada para ver el porcentaje exacto de coincidencia
- Las zonas que no se muestran tienen menos del 30% de coincidencia
- Puedes activar/desactivar otros filtros para comparar

## Interpretación del Vector de Preferencias

El vector tiene 11 componentes (índices 0-10):
0. **Income** - Precio/nivel económico

1. **Crimes** - Seguridad (menor valor = más seguro)
2. **Connectivity** - Conectividad digital/internet
3. **Noise** - Contaminación acústica (mayor valor = menos ruido)
4. **Walkability** - Caminabilidad/ciudad de 15 minutos
5. **Accessibility** - Accesibilidad para personas con movilidad reducida
6. **Wellbeing** - Bienestar general/espacios verdes/pet-friendly
7. **Mobility** - Transporte público/bici/movilidad
8. **Education** - Centros educativos cercanos
9. **Community Vibe** - Ambiente de la comunidad/comercios
10. **Health** - Centros médicos/salud

## Métodos de Cálculo

El sistema ofrece **5 métodos diferentes** para calcular la similitud entre tus preferencias y las zonas de Los Ángeles. Puedes cambiar el método en el desplegable "Método" ubicado en la esquina inferior derecha del mapa.

### 1. 🎯 Coseno (Cosine Similarity) - **RECOMENDADO**

- **Descripción**: Mide el ángulo entre dos vectores, ignorando magnitudes
- **Ventajas**: Rápido, estable y funciona bien para comparar patrones
- **Uso ideal**: Búsquedas generales, casos donde importa más el "patrón" de preferencias que los valores exactos
- **Fórmula**: `similarity = dot(v1, v2) / (||v1|| * ||v2||)`
- **Rango**: 0 (vectores perpendiculares) a 1 (vectores paralelos)

### 2. 📊 Maximum Likelihood (ML)

- **Descripción**: Basado en distribución gaussiana, asume que los datos siguen una distribución normal
- **Ventajas**: Penaliza más las diferencias grandes, da resultados más "suaves"
- **Uso ideal**: Cuando quieres resultados más conservadores, penalizando zonas muy diferentes
- **Método**: Calcula distancia euclidiana normalizada y aplica transformación gaussiana (σ=0.3)
- **Rango**: 0 (muy diferentes) a 1 (idénticos)

### 3. 📏 Manhattan Distance

- **Descripción**: Suma de diferencias absolutas en cada dimensión (distancia L1)
- **Ventajas**: Más sensible a diferencias individuales en cada categoría
- **Uso ideal**: Cuando todas las dimensiones son igualmente importantes
- **Fórmula**: `distance = Σ|v1[i] - v2[i]|`, luego `similarity = 1 - distance/11`
- **Rango**: 0 (muy diferentes) a 1 (idénticos)

### 4. ⚖️ Weighted Euclidean (Ponderado)

- **Descripción**: Distancia euclidiana con pesos personalizados por dimensión
- **Ventajas**: Prioriza las dimensiones más importantes (crimes, accessibility, health, income)
- **Uso ideal**: Cuando la seguridad, accesibilidad y salud son prioritarias
- **Pesos aplicados**:
  - 🔴 **Seguridad (Crimes)**: 1.5 (máxima prioridad)
  - 🟡 **Accessibilidad**: 1.3 (alta prioridad)
  - 🟡 **Income**: 1.2 (alta prioridad)
  - 🟡 **Salud (Health)**: 1.2 (alta prioridad)
  - 🟢 **Resto**: 0.8-1.1 (prioridad normal)
- **Rango**: 0 (muy diferentes) a 1 (idénticos)

### 5. 📈 Pearson Correlation

- **Descripción**: Mide correlación lineal entre vectores
- **Ventajas**: Detecta patrones similares incluso con escalas diferentes
- **Uso ideal**: Cuando importa más la "tendencia" que los valores absolutos
- **Fórmula**: Coeficiente de correlación de Pearson, normalizado de [-1,1] a [0,1]
- **Rango**: 0 (no correlacionados/opuestos) a 1 (perfectamente correlacionados)

### Comparación Rápida

| Método             | Velocidad | Precisión | Sensibilidad | Mejor para                |
| ------------------- | --------- | ---------- | ------------ | ------------------------- |
| **Coseno**    | ⚡⚡⚡    | ⭐⭐⭐     | Media        | Uso general               |
| **ML**        | ⚡⚡      | ⭐⭐⭐⭐   | Alta         | Resultados conservadores  |
| **Manhattan** | ⚡⚡⚡    | ⭐⭐⭐     | Alta         | Balance dimensional       |
| **Weighted**  | ⚡⚡      | ⭐⭐⭐⭐⭐ | Muy alta     | Priorizar seguridad/salud |
| **Pearson**   | ⚡⚡      | ⭐⭐⭐     | Baja         | Patrones similares        |

### ¿Qué método elegir?

- **Familia con niños** → ⚖️ Weighted (prioriza seguridad y accesibilidad)
- **Estudiante/Joven profesional** → 🎯 Coseno (balance general)
- **Búsqueda conservadora** → 📊 ML (resultados más estrictos)
- **Todas las categorías igual de importantes** → 📏 Manhattan
- **Buscar zonas con patrón similar** → 📈 Pearson

## Cómo cambiar el método

1. Localiza el botón **"Método: [nombre]"** en la esquina inferior derecha del mapa
2. Haz clic para desplegar el menú
3. Selecciona uno de los 5 métodos disponibles
4. El mapa de calor se recalculará automáticamente

## Ejemplo de uso

```
Prompt: "Busco un lugar tranquilo, necesito buen internet para teletrabajar, 
         tengo un perro y me gustaría estar cerca de parques. 
         Presupuesto medio-alto."

Resultado esperado: 
- Zonas con alta conectividad (connectivity)
- Baja contaminación acústica (noise)
- Buena puntuación en wellbeing (espacios verdes)
- Precio medio-alto (income)

Método recomendado: Coseno o Weighted
```

## Notas Técnicas

- Todos los métodos devuelven valores normalizados entre 0 y 1
- Se requiere un umbral mínimo del 30% para mostrar una zona en el mapa
- Cada celda del mapa representa un área de ~2.36 km² de Los Ángeles
- Los cálculos se ejecutan en el backend (Python + NumPy) para máxima precisión
