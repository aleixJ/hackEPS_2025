# Community Vibe Index Generator

Índice compuesto que mide la "vibra comunitaria" y detecta gentrificación combinando:

1. **Yelp Fusion API** - Datos de negocios (precio, categorías trendy, reviews)
2. **LADBS Building Permits** - Inversión inmobiliaria reciente

## 🎯 Qué Detecta

### El "Índice Hipster" (Yelp)
- **Precio Promedio**: ¿Están abriendo negocios caros?
- **Ratio Trendy**: ¿Hay cafeterías de especialidad, bares de vino, yoga studios?
- **Densidad de Reviews**: ¿La gente va al barrio o es dormitorio?

### El "Índice de Reinversión" (LADBS)
- **Valuación de Permisos**: ¿Cuánto $$ se está invirtiendo en construcción?
- **Tipos Relevantes**: Remodelaciones, adiciones, obra nueva > $20k

## 📊 Fórmula del Score

```
Community Vibe = (Yelp Component × 0.4) + (Permits Component × 0.6)

Donde:
  Yelp Component = (Precio × 0.3) + (Trendy × 0.4) + (Vibrancia × 0.3)
  Permits Component = Suma Valuaciones / Max Valuación
```

## 🔑 Setup - Yelp API Key

### 1. Obtener API Key de Yelp

1. Ve a https://www.yelp.com/developers
2. Crea una cuenta o inicia sesión
3. Crea una nueva app
4. Copia tu **API Key**

### 2. Configurar la API Key

**Opción A - Variable de Entorno (Recomendado):**
```bash
export YELP_API_KEY='tu_api_key_aqui'
```

**Opción B - Archivo .env:**
```bash
# Crear archivo .env en la carpeta community_vibe
echo "YELP_API_KEY=tu_api_key_aqui" > .env
```

Luego instalar python-dotenv:
```bash
pip install python-dotenv
```

Y añadir al inicio del script:
```python
from dotenv import load_dotenv
load_dotenv()
```

## 🚀 Ejecutar

```bash
cd /home/gerard/Gerard/Projects/hackEPS_2025/server/community_vibe
python community_vibe.py
```

**Tiempo estimado**: ~20-30 minutos
- 400 celdas × (0.2s Yelp + delay) ≈ 80-120 segundos para Yelp
- ~5-10 minutos para descargar y procesar permisos LADBS

## 📈 Interpretación de Resultados

### Valores Altos (0.7-1.0) 🔥
**"Hotspots de Gentrificación"**
- Negocios caros/trendy + Alta inversión
- Ejemplos: Highland Park, Arts District, partes de Downtown

### Valores Medios-Altos (0.5-0.7) 📈
**"Zonas Consolidadas o en Mejora"**
- Barrios establecidos con actividad constante
- O barrios en transición temprana

### Valores Medios (0.3-0.5) 🏘️
**"Barrios Residenciales Estables"**
- Poca vida nocturna, inversión moderada
- Barrios dormitorio tradicionales

### Valores Bajos (0-0.3) 💤
**"Zonas Estancadas o Industriales"**
- Poca actividad comercial
- Baja inversión inmobiliaria

## 📝 Notas Importantes

### Límites de Yelp API
- **Free Tier**: 500 llamadas/día
- Para 400 celdas estás OK
- Si falla, el script continúa con solo datos de LADBS

### Datos de LADBS
- Gratis y sin límites
- Actualizados regularmente por la ciudad
- Datos históricos disponibles

### Sin Yelp API Key
El script funcionará usando **solo** datos de permisos de construcción:
```
Community Vibe = Permits Score × 1.0
```

Será menos preciso pero aún útil para detectar zonas de inversión.

## 🎨 Visualización Sugerida

En el cliente, usar un **gradiente de colores calientes**:
- 🟣 Violeta/Púrpura: Baja vibra (0-0.3)
- 🔵 Azul: Media-baja (0.3-0.5)
- 🟢 Verde: Media (0.5-0.7)
- 🟡 Amarillo: Media-alta (0.7-0.85)
- 🔴 Rojo: Alta (0.85-1.0) ← **Gentrificación activa**

## 🔍 Debugging

Si hay problemas:

```bash
# Ver qué permisos se están descargando
# Modificar el script para imprimir el dataframe:
print(df.head())
print(df['permit_type'].value_counts())

# Test de Yelp API
curl -H "Authorization: Bearer TU_API_KEY" \
  "https://api.yelp.com/v3/businesses/search?latitude=34.0522&longitude=-118.2437&limit=5"
```

## 📦 Output

Archivo generado:
```
server/city_stats/jsons/community_vibe_matrix_20x20_TIMESTAMP.json
```

Estructura:
```json
[{
  "Aspect": "CommunityVibe",
  "CommunityVibMatrix": [[0.0, 0.1, ...], ...],
  "MaxScore": 1.234,
  "Components": {
    "yelp": "Price + Trendy + Reviews (40%)",
    "permits": "Construction investment (60%)"
  }
}]
```
