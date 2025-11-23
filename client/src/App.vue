<template>
  <div id="app">
    <div id="map"></div>
    <div id="controls">
      <button @click="toggleCrimeLayer" class="toggle-btn">
        {{ showCrimeLayer ? 'Ocultar' : 'Mostrar' }} Índice de Criminalidad
      </button>
      <button @click="toggleConnectivityLayer" class="toggle-btn">
        {{ showConnectivityLayer ? 'Ocultar' : 'Mostrar' }} Conectividad
      </button>
      <button @click="toggleIncomeLayer" class="toggle-btn">
        {{ showIncomeLayer ? 'Ocultar' : 'Mostrar' }} Nivel de Ingresos
      </button>
      <button @click="toggleNoiseLayer" class="toggle-btn">
        {{ showNoiseLayer ? 'Ocultar' : 'Mostrar' }} Nivel de Ruido
      </button>
      <button @click="toggleWalkabilityLayer" class="toggle-btn">
        {{ showWalkabilityLayer ? 'Ocultar' : 'Mostrar' }} Walkability 15min
      </button>
      <button @click="toggleWellbeingLayer" class="toggle-btn">
        {{ showWellbeingLayer ? 'Ocultar' : 'Mostrar' }} Wellbeing
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
      showCrimeLayer: true,
      connectivityRectangles: [],
      showConnectivityLayer: true,
      incomeRectangles: [],
      showIncomeLayer: true,
      noiseRectangles: [],
      showNoiseLayer: true,
      walkabilityRectangles: [],
      showWalkabilityLayer: true,
      wellbeingRectangles: [],
      showWellbeingLayer: true
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
    
    toggleConnectivityLayer() {
      this.showConnectivityLayer = !this.showConnectivityLayer;
      
      this.connectivityRectangles.forEach(rect => {
        if (this.showConnectivityLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleIncomeLayer() {
      this.showIncomeLayer = !this.showIncomeLayer;
      
      this.incomeRectangles.forEach(rect => {
        if (this.showIncomeLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleNoiseLayer() {
      this.showNoiseLayer = !this.showNoiseLayer;
      
      this.noiseRectangles.forEach(rect => {
        if (this.showNoiseLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleWalkabilityLayer() {
      this.showWalkabilityLayer = !this.showWalkabilityLayer;
      
      this.walkabilityRectangles.forEach(rect => {
        if (this.showWalkabilityLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleWellbeingLayer() {
      this.showWellbeingLayer = !this.showWellbeingLayer;
      
      this.wellbeingRectangles.forEach(rect => {
        if (this.showWellbeingLayer) {
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
    
    getConnectivityColor(connectivityValue) {
      // No mostrar si es menor al 10%
      if (connectivityValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (connectivityValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(0, 255, 0)',
        opacity: opacity
      };
    },
    
    getIncomeColor(incomeValue) {
      // No mostrar si es menor al 10%
      if (incomeValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (incomeValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(0, 0, 255)',
        opacity: opacity
      };
    },
    
    getNoiseColor(noiseValue) {
      // No mostrar si es menor al 10%
      if (noiseValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (noiseValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(255, 165, 0)', // Naranja para noise
        opacity: opacity
      };
    },
    
    getWalkabilityColor(walkabilityValue) {
      // No mostrar si es menor al 10%
      if (walkabilityValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (walkabilityValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(128, 0, 128)', // Morado para walkability
        opacity: opacity
      };
    },
    
    getWellbeingColor(wellbeingValue) {
      // No mostrar si es menor al 10%
      if (wellbeingValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (wellbeingValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(0, 255, 255)', // Cyan para wellbeing
        opacity: opacity
      };
    },
    
    drawCrimeGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.crime.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de criminalidad');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const crimeValue = matrix_LA_alldata_20x20[i][j][1]; // Índice 1 = crimes
          
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
    },
    
    drawConnectivityGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.connectivity.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de conectividad');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const connectivityValue = matrix_LA_alldata_20x20[i][j][2]; // Índice 2 = connectivity
          
          if (connectivityValue === null || connectivityValue === undefined) continue;
          
          const colorData = this.getConnectivityColor(connectivityValue);
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
            <strong>Conectividad:</strong> ${(connectivityValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.connectivityRectangles.push(rectangle);
          
          if (this.showConnectivityLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    },
    
    drawIncomeGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.income.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de income');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const incomeValue = matrix_LA_alldata_20x20[i][j][0]; // Índice 0 = income
          
          if (incomeValue === null || incomeValue === undefined) continue;
          
          const colorData = this.getIncomeColor(incomeValue);
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
            <strong>Nivel de Ingresos:</strong> ${(incomeValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.incomeRectangles.push(rectangle);
          
          if (this.showIncomeLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    },
    
    drawNoiseGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.noise.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de noise');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const noiseValue = matrix_LA_alldata_20x20[i][j][3]; // Índice 3 = noise
          
          if (noiseValue === null || noiseValue === undefined) continue;
          
          const colorData = this.getNoiseColor(noiseValue);
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
            <strong>Nivel de Ruido:</strong> ${(noiseValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.noiseRectangles.push(rectangle);
          
          if (this.showNoiseLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    },
    
    drawWalkabilityGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.walkability.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de walkability');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const walkabilityValue = matrix_LA_alldata_20x20[i][j][4]; // Índice 4 = walkability
          
          if (walkabilityValue === null || walkabilityValue === undefined) continue;
          
          const colorData = this.getWalkabilityColor(walkabilityValue);
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
            <strong>Walkability 15min:</strong> ${(walkabilityValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.walkabilityRectangles.push(rectangle);
          
          if (this.showWalkabilityLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    },
    
    drawWellbeingGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.wellbeing.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de wellbeing');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const wellbeingValue = matrix_LA_alldata_20x20[i][j][6]; // Índice 6 = wellbeing
          
          if (wellbeingValue === null || wellbeingValue === undefined) continue;
          
          const colorData = this.getWellbeingColor(wellbeingValue);
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
            <strong>Wellbeing:</strong> ${(wellbeingValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.wellbeingRectangles.push(rectangle);
          
          if (this.showWellbeingLayer) {
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
        
        // Dibujar grid de income (primero, capa de fondo)
        this.drawIncomeGrid(data);
        
        // Dibujar grid de noise
        this.drawNoiseGrid(data);
        
        // Dibujar grid de wellbeing
        this.drawWellbeingGrid(data);
        
        // Dibujar grid de walkability
        this.drawWalkabilityGrid(data);
        
        // Dibujar grid de conectividad
        this.drawConnectivityGrid(data);
        
        // Dibujar grid de criminalidad (último, capa superior)
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
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  min-width: 200px;
}

.toggle-btn:hover {
  background-color: #f4f4f4;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.toggle-btn:active {
  transform: scale(0.98);
}
</style>
