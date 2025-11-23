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

## Método de Cálculo

- Se utiliza **similitud coseno** para comparar vectores
- Valores entre 0 (totalmente diferentes) y 1 (idénticos)
- Cada celda del mapa representa un área de ~2.36 km² de Los Ángeles

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
```
