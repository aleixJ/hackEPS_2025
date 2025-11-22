<template>
  <div id="app">
    <div id="map"></div>
    <div id="controls">
      <button @click="toggleCrimeLayer" class="toggle-btn">
        {{ showCrimeLayer ? 'Ocultar' : 'Mostrar' }} Índice de Criminalidad
      </button>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import osmtogeojson from 'osmtogeojson';

export default {
  name: 'App',
  data() {
    return {
      map: null,
      crimeRectangles: [],
      showCrimeLayer: true
    };
  },
  methods: {
    toggleCrimeLayer() {
      this.showCrimeLayer = !this.showCrimeLayer;
      
      this.crimeRectangles.forEach(rect => {
        if (this.showCrimeLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    getCrimeColor(crimeValue) {
      // No mostrar si es menor al 10%
      if (crimeValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (crimeValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(255, 0, 0)',
        opacity: opacity
      };
    },
    
    drawCrimeGrid(data) {
      const { matrix, crime_info, rectangle } = data;
      
      if (!crime_info.success || !matrix) {
        console.error('Error cargando datos de criminalidad');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const crimeValue = matrix[i][j][1]; // Índice 1 contiene el valor de criminalidad
          
          if (crimeValue === null || crimeValue === undefined) continue;
          
          const colorData = this.getCrimeColor(crimeValue);
          if (!colorData) continue; // Saltar si es menor al 10%
          
          // Calcular coordenadas de la celda
          // i va de norte a sur, j va de oeste a este
          const cellNorth = north - (i * verticalStep);
          const cellSouth = cellNorth - verticalStep;
          const cellWest = west + (j * horizontalStep);
          const cellEast = cellWest + horizontalStep;
          
          const bounds = [[cellNorth, cellWest], [cellSouth, cellEast]];
          
          const rectangle = L.rectangle(bounds, {
            color: colorData.color,
            weight: 0.5,
            fillColor: colorData.color,
            fillOpacity: colorData.opacity
          });
          
          // Añadir popup con información
          rectangle.bindPopup(`
            <strong>Índice de Criminalidad:</strong> ${(crimeValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.crimeRectangles.push(rectangle);
          
          if (this.showCrimeLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    }
  },
  mounted() {
    // Create map
    this.map = L.map('map').setView([34.0522, -118.2437], 10);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    // Fetch OSM data from the backend
    fetch('http://localhost:5000/api/osm-data')
      .then(response => response.json())
      .then(data => {
        console.log('OSM data from server:', data);
        
        if (data.rectangle) {
          const { north, south, east, west } = data.rectangle;
          
          // Create rectangle bounds
          const bounds = [[north, west], [south, east]];
          
          // Draw rectangle on map
          L.rectangle(bounds, {
            color: 'blue',
            weight: 2,
            fillOpacity: 0
          }).addTo(this.map);
          
          // Fit map to rectangle
          this.map.fitBounds(bounds);
        }
        
        // Dibujar grid de criminalidad
        this.drawCrimeGrid(data);
      })
      .catch(error => console.error('Error loading data from server:', error));
  }
};
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
  position: relative;
}

#map {
  height: 100%;
  width: 100%;
}

#controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
}

.toggle-btn {
  background-color: white;
  border: 2px solid rgba(0,0,0,0.2);
  border-radius: 4px;
  padding: 10px 15px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background-color: #f4f4f4;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.toggle-btn:active {
  transform: scale(0.98);
}
</style>
