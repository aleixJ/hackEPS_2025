<template>
  <div id="app">

    <div class="container">
      <header>
        <h1>AI Prompt Generator</h1>
        <p class="subtitle">Enter your prompt and get AI-generated responses</p>
      </header>

      <main>
        <div class="input-section">
          <label for="prompt-input">Your Prompt</label>
          <textarea
            id="prompt-input"
            v-model="userPrompt"
            placeholder="Enter your prompt here..."
            rows="5"
            :disabled="loading"
          ></textarea>
        </div>

        <div class="button-group">
          <button 
            @click="generateOutput" 
            :disabled="loading || !userPrompt.trim()"
            class="btn btn-primary"
          >
            <span v-if="loading">Generating...</span>
            <span v-else>Generate</span>
          </button>
          <button 
            @click="refresh" 
            :disabled="loading"
            class="btn btn-secondary"
          >
            Refresh
          </button>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="aiOutput" class="output-section">
          <label>AI Output</label>
          <div class="output-content">
            {{ aiOutput }}
          </div>
        </div>
      </main>
     <!-- A partir de aqui empieza el fichero de mapa -->
    <div id="map"></div>
    <div id="controls">
      <button @click="showFiltersMenu = !showFiltersMenu" class="filters-toggle-btn">
        Filtros {{ showFiltersMenu ? '▲' : '▼' }}
      </button>
      <div v-show="showFiltersMenu" class="filters-menu">
        <button @click="toggleCrimeLayer" class="toggle-btn" :class="{ 'active': showCrimeLayer }">
          {{ showCrimeLayer ? 'Ocultar' : 'Mostrar' }} Índice de Criminalidad
        </button>
        <button @click="toggleConnectivityLayer" class="toggle-btn" :class="{ 'active': showConnectivityLayer }">
          {{ showConnectivityLayer ? 'Ocultar' : 'Mostrar' }} Conectividad
        </button>
        <button @click="toggleIncomeLayer" class="toggle-btn" :class="{ 'active': showIncomeLayer }">
          {{ showIncomeLayer ? 'Ocultar' : 'Mostrar' }} Nivel de Ingresos
        </button>
        <button @click="toggleNoiseLayer" class="toggle-btn" :class="{ 'active': showNoiseLayer }">
          {{ showNoiseLayer ? 'Ocultar' : 'Mostrar' }} Nivel de Ruido
        </button>
        <button @click="toggleWalkabilityLayer" class="toggle-btn" :class="{ 'active': showWalkabilityLayer }">
          {{ showWalkabilityLayer ? 'Ocultar' : 'Mostrar' }} Walkability 15min
        </button>
        <button @click="toggleAccessibilityLayer" class="toggle-btn" :class="{ 'active': showAccessibilityLayer }">
          {{ showAccessibilityLayer ? 'Ocultar' : 'Mostrar' }} Accesibilidad
        </button>
        <button @click="toggleWellbeingLayer" class="toggle-btn" :class="{ 'active': showWellbeingLayer }">
          {{ showWellbeingLayer ? 'Ocultar' : 'Mostrar' }} Wellbeing
        </button>
        <button @click="toggleMobilityLayer" class="toggle-btn" :class="{ 'active': showMobilityLayer }">
          {{ showMobilityLayer ? 'Ocultar' : 'Mostrar' }} Mobility
        </button>
        <button @click="toggleEducationLayer" class="toggle-btn" :class="{ 'active': showEducationLayer }">
          {{ showEducationLayer ? 'Ocultar' : 'Mostrar' }} Education
        </button>
        <button @click="toggleCommunityVibeLayer" class="toggle-btn" :class="{ 'active': showCommunityVibeLayer }">
          {{ showCommunityVibeLayer ? 'Ocultar' : 'Mostrar' }} Community Vibe
        </button>
        <button @click="toggleHealthLayer" class="toggle-btn" :class="{ 'active': showHealthLayer }">
          {{ showHealthLayer ? 'Ocultar' : 'Mostrar' }} Health
        </button>
      </div>

      
      
      
      
      
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import osmtogeojson from 'osmtogeojson';


export default {
  name: 'App',
  data() {
    return {

      userPrompt: '',
      aiOutput: '',
      loading: false,
      error: '',
      map: null,
      crimeRectangles: [],
      showCrimeLayer: false,
      connectivityRectangles: [],
      showConnectivityLayer: false,
      incomeRectangles: [],
      showIncomeLayer: false,
      noiseRectangles: [],
      showNoiseLayer: false,
      walkabilityRectangles: [],
      showWalkabilityLayer: false,
      accessibilityRectangles: [],
      showAccessibilityLayer: false,
      wellbeingRectangles: [],
      showWellbeingLayer: false,
      mobilityRectangles: [],
      showMobilityLayer: false,
      educationRectangles: [],
      showEducationLayer: false,
      healthRectangles: [],
      showHealthLayer: false,
      communityVibeRectangles: [],
      showCommunityVibeLayer: false,
      showFiltersMenu: false,
      showFiltersMenu: false
    };
  },
  methods: {
    async generateOutput() {
      if (!this.userPrompt.trim()) {
        this.error = 'Please enter a prompt';
        return;
      }

      this.loading = true;
      this.error = '';
      this.aiOutput = '';

      try {
        const response = await axios.post('/api/generate', {
          prompt: this.userPrompt
        });

        this.aiOutput = response.data.output;
      } catch (err) {
        this.error = err.response?.data?.error || 'An error occurred while generating output';
        console.error('Error:', err);
      } finally {
        this.loading = false;
      }
    },
    refresh() {
      this.userPrompt = '';
      this.aiOutput = '';
      this.error = '';
    },
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
    
    toggleAccessibilityLayer() {
      this.showAccessibilityLayer = !this.showAccessibilityLayer;
      
      this.accessibilityRectangles.forEach(rect => {
        if (this.showAccessibilityLayer) {
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
    
    toggleMobilityLayer() {
      this.showMobilityLayer = !this.showMobilityLayer;
      
      this.mobilityRectangles.forEach(rect => {
        if (this.showMobilityLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleEducationLayer() {
      this.showEducationLayer = !this.showEducationLayer;
      
      this.educationRectangles.forEach(rect => {
        if (this.showEducationLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleHealthLayer() {
      this.showHealthLayer = !this.showHealthLayer;
      
      this.healthRectangles.forEach(rect => {
        if (this.showHealthLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    toggleCommunityVibeLayer() {
      this.showCommunityVibeLayer = !this.showCommunityVibeLayer;
      
      this.communityVibeRectangles.forEach(rect => {
        if (this.showCommunityVibeLayer) {
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
    
    getAccessibilityColor(accessibilityValue) {
      // No mostrar si es menor al 10%
      if (accessibilityValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (accessibilityValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(255, 255, 0)', // Amarillo para accesibilidad
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
    
    getMobilityColor(mobilityValue) {
      // No mostrar si es menor al 10%
      if (mobilityValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (mobilityValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(0, 128, 128)', // Teal para mobility
        opacity: opacity
      };
    },
    
    getEducationColor(educationValue) {
      // No mostrar si es menor al 10%
      if (educationValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (educationValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(50, 205, 50)', // Lime para education
        opacity: opacity
      };
    },
    
    getHealthColor(healthValue) {
      // No mostrar si es menor al 10%
      if (healthValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (healthValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      return {
        color: 'rgb(0, 255, 0)', // Verde lima para health
        opacity: opacity
      };
    },
    
    getCommunityVibeColor(communityVibeValue) {
      // No mostrar si es menor al 10%
      if (communityVibeValue < 0.1) return null;
      
      // Mapear de 10%-100% a opacidad 40%-100%
      const normalizedValue = (communityVibeValue - 0.1) / 0.9; // 0 a 1
      const opacity = 0.4 + (normalizedValue * 0.6); // 0.4 a 1.0
      
      // Gradiente caliente: bajo=azul, medio=amarillo, alto=rojo (gentrificación)
      let color;
      if (communityVibeValue < 0.3) {
        // Azul-Púrpura (estancado)
        color = 'rgb(100, 100, 255)';
      } else if (communityVibeValue < 0.5) {
        // Amarillo (estable)
        color = 'rgb(255, 255, 100)';
      } else if (communityVibeValue < 0.7) {
        // Naranja (en desarrollo)
        color = 'rgb(255, 165, 0)';
      } else {
        // Rojo (gentrificación)
        color = 'rgb(255, 0, 0)';
      }
      
      return {
        color: color,
        opacity: opacity
      };
    },
    
    drawCrimeGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.crimes.success || !matrix_LA_alldata_20x20) {
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
    
    drawEducationGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.education.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de education');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const educationValue = matrix_LA_alldata_20x20[i][j][8]; // Índice 8
          
          if (educationValue === null || educationValue === undefined) continue;
          
          const colorData = this.getEducationColor(educationValue);
          if (!colorData) continue;
          
          // Calcular coordenadas de la celda
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
          
          rectangle.bindPopup(`
            <strong>Education:</strong> ${(educationValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.educationRectangles.push(rectangle);
          
          if (this.showEducationLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    },
    
    drawHealthGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.health.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de health');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const healthValue = matrix_LA_alldata_20x20[i][j][10]; // Índice 10 = health
          
          if (healthValue === null || healthValue === undefined) continue;
          
          const colorData = this.getHealthColor(healthValue);
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
            <strong>Health:</strong> ${(healthValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.healthRectangles.push(rectangle);
          
          if (this.showHealthLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
    },
    
    drawCommunityVibeGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.community_vibe.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de community_vibe');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const communityVibeValue = matrix_LA_alldata_20x20[i][j][9]; // Índice 9 = community_vibe
          
          if (communityVibeValue === null || communityVibeValue === undefined) continue;
          
          const colorData = this.getCommunityVibeColor(communityVibeValue);
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
          
          // Añadir popup con información interpretativa
          let interpretation = '';
          if (communityVibeValue < 0.3) {
            interpretation = 'Estancado/Dormitorio';
          } else if (communityVibeValue < 0.5) {
            interpretation = 'Estable residencial';
          } else if (communityVibeValue < 0.7) {
            interpretation = 'En desarrollo';
          } else {
            interpretation = 'Gentrificación activa';
          }
          
          rectangle.bindPopup(`
            <strong>Community Vibe:</strong> ${(communityVibeValue * 100).toFixed(2)}%<br>
            <strong>Estado:</strong> ${interpretation}<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.communityVibeRectangles.push(rectangle);
          
          if (this.showCommunityVibeLayer) {
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
    
    drawAccessibilityGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.accessibility.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de accessibility');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      // Dibujar cada celda de la matriz 20x20
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const accessibilityValue = matrix_LA_alldata_20x20[i][j][5]; // Índice 5 = accessibility
          
          if (accessibilityValue === null || accessibilityValue === undefined) continue;
          
          const colorData = this.getAccessibilityColor(accessibilityValue);
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
            <strong>Accesibilidad:</strong> ${(accessibilityValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.accessibilityRectangles.push(rectangle);
          
          if (this.showAccessibilityLayer) {
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
    },
    
    drawMobilityGrid(data) {
      const { matrix_LA_alldata_20x20, data_info, rectangle } = data;
      
      if (!data_info.mobility.success || !matrix_LA_alldata_20x20) {
        console.error('Error cargando datos de mobility');
        return;
      }
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const mobilityValue = matrix_LA_alldata_20x20[i][j][7]; // Índice 7
          
          if (mobilityValue === null || mobilityValue === undefined) continue;
          
          const colorData = this.getMobilityColor(mobilityValue);
          if (!colorData) continue;
          
          // Calcular coordenadas de la celda
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
          
          rectangle.bindPopup(`
            <strong>Mobility:</strong> ${(mobilityValue * 100).toFixed(2)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.mobilityRectangles.push(rectangle);
          
          if (this.showMobilityLayer) {
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
        
        // Dibujar grid de accessibility
        this.drawAccessibilityGrid(data);
        
        // Dibujar grid de wellbeing
        this.drawWellbeingGrid(data);
        
        // Dibujar grid de mobility
        this.drawMobilityGrid(data);
        
        // Dibujar grid de education
        this.drawEducationGrid(data);
        
        // Dibujar grid de health
        this.drawHealthGrid(data);
        
        // Dibujar grid de community vibe
        this.drawCommunityVibeGrid(data);
        
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

.filters-toggle-btn {
  background-color: #2196F3;
  color: white;
  border: 2px solid #1976D2;
  border-radius: 4px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 3px 6px rgba(33, 150, 243, 0.4);
  transition: all 0.3s ease;
  min-width: 150px;
  text-align: center;
}

.filters-toggle-btn:hover {
  background-color: #1976D2;
  box-shadow: 0 5px 10px rgba(33, 150, 243, 0.5);
}

.filters-toggle-btn:active {
  transform: scale(0.98);
}

.filters-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 500px;
  overflow-y: auto;
}

.filters-toggle-btn {
  background-color: #2196F3;
  color: white;
  border: 2px solid #1976D2;
  border-radius: 4px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 3px 6px rgba(33, 150, 243, 0.4);
  transition: all 0.3s ease;
  min-width: 150px;
  text-align: center;
}

.filters-toggle-btn:hover {
  background-color: #1976D2;
  box-shadow: 0 5px 10px rgba(33, 150, 243, 0.5);
}

.filters-toggle-btn:active {
  transform: scale(0.98);
}

.filters-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 500px;
  overflow-y: auto;
}

.toggle-btn {
  background-color: #f0f0f0;
  border: 2px solid rgba(0,0,0,0.2);
  border-radius: 4px;
  padding: 10px 15px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
  min-width: 200px;
  color: #666;
}

.toggle-btn:hover {
  background-color: #e0e0e0;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.toggle-btn:active {
  transform: scale(0.98);
}

.toggle-btn.active {
  background-color: #4CAF50;
  color: white;
  border-color: #45a049;
  box-shadow: 0 3px 6px rgba(76, 175, 80, 0.4);
}

.toggle-btn.active:hover {
  background-color: #45a049;
  box-shadow: 0 5px 10px rgba(76, 175, 80, 0.5);
}
</style>
