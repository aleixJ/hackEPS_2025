<template>
  <div id="app">
    <!-- Mapa como fondo -->
    <div id="map"></div>
    
    <!-- Panel de prompt superpuesto a la izquierda -->
    <div class="prompt-panel">
      <div class="prompt-container">
        <h2>AI Assistant</h2>
        
        <div class="input-section">
          <textarea
            v-model="userPrompt"
            placeholder="Descriu la teva zona ideal a Los Ángeles..."
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
            <span v-if="loading">Generando...</span>
            <span v-else>Generar</span>
          </button>
          <button 
            @click="refresh" 
            :disabled="loading"
            class="btn btn-secondary"
          >
            Limpiar
          </button>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="preferenceVector.length > 0" class="output-section">
          <label>Preferències Analitzades</label>
          
          <!-- Gràfic Radar -->
          <div class="chart-container">
            <Radar :data="chartData" :options="chartOptions" />
          </div>
          
          <!-- Controls per modificar valors -->
          <div class="controls-container">
            <h3>Ajusta les Preferències</h3>
            <div class="slider-grid">
              <div v-for="(aspect, index) in aspectNames" :key="index" class="slider-item">
                <label>
                  {{ aspect }}
                  <span class="value-display">{{ (preferenceVector[index] * 100).toFixed(0) }}%</span>
                </label>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  :value="preferenceVector[index] * 100"
                  @input="updatePreferenceInstant(index, $event.target.value)"
                  @mouseup="updatePreferenceAndRecalculate(index, $event.target.value)"
                  @touchend="updatePreferenceAndRecalculate(index, $event.target.value)"
                  class="slider"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Controles de filtros a la derecha -->
    <div id="controls">
      <button @click="showFiltersMenu = !showFiltersMenu" class="filters-toggle-btn">
        Filtros {{ showFiltersMenu ? '▲' : '▼' }}
      </button>
      <div v-show="showFiltersMenu" class="filters-menu">
        <button @click="toggleCrimeLayer" class="toggle-btn" :class="{ 'active': showCrimeLayer }">
          {{ showCrimeLayer ? 'Ocultar' : 'Mostrar' }} Criminalidad
        </button>
        <button @click="toggleConnectivityLayer" class="toggle-btn" :class="{ 'active': showConnectivityLayer }">
          {{ showConnectivityLayer ? 'Ocultar' : 'Mostrar' }} Conectividad
        </button>
        <button @click="toggleIncomeLayer" class="toggle-btn" :class="{ 'active': showIncomeLayer }">
          {{ showIncomeLayer ? 'Ocultar' : 'Mostrar' }} Ingresos
        </button>
        <button @click="toggleNoiseLayer" class="toggle-btn" :class="{ 'active': showNoiseLayer }">
          {{ showNoiseLayer ? 'Ocultar' : 'Mostrar' }} Ruido
        </button>
        <button @click="toggleWalkabilityLayer" class="toggle-btn" :class="{ 'active': showWalkabilityLayer }">
          {{ showWalkabilityLayer ? 'Ocultar' : 'Mostrar' }} Walkability
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
        <button @click="toggleHeatmapLayer" class="toggle-btn heatmap-btn" :class="{ 'active': showHeatmapLayer }">
          {{ showHeatmapLayer ? 'Ocultar' : 'Mostrar' }} Mapa de Calor
        </button>
      </div>
    </div>
    
    <!-- Selector de método de cálculo abajo a la derecha -->
    <div id="method-selector">
      <button @click="showMethodMenu = !showMethodMenu" class="method-toggle-btn">
        Método: {{ getMethodName(calculationMethod) }} {{ showMethodMenu ? '▲' : '▼' }}
      </button>
      <div v-show="showMethodMenu" class="method-menu">
        <button 
          @click="selectMethod('cosine')" 
          class="method-btn" 
          :class="{ 'active': calculationMethod === 'cosine' }"
        >
          📐 Similitud Coseno
        </button>
        <button 
          @click="selectMethod('ml')" 
          class="method-btn" 
          :class="{ 'active': calculationMethod === 'ml' }"
        >
          🎯 Maximum Likelihood
        </button>
        <button 
          @click="selectMethod('manhattan')" 
          class="method-btn" 
          :class="{ 'active': calculationMethod === 'manhattan' }"
        >
          🏙️ Manhattan Distance
        </button>
        <button 
          @click="selectMethod('weighted')" 
          class="method-btn" 
          :class="{ 'active': calculationMethod === 'weighted' }"
        >
          ⚖️ Weighted Euclidean
        </button>
        <button 
          @click="selectMethod('pearson')" 
          class="method-btn" 
          :class="{ 'active': calculationMethod === 'pearson' }"
        >
          📊 Pearson Correlation
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
import { Radar } from 'vue-chartjs';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)


export default {
  name: 'App',
  components: {
    Radar
  },
  data() {
    return {
      userPrompt: '',
      aiOutput: '',
      preferenceVector: [],
      aspectNames: [
        'Poder Adquisitiu',
        'Criminalitat',
        'Connectivitat WFH',
        'Soroll',
        'Walkability 15min',
        'Accessibilitat',
        'Espais verds/Mascotes',
        'Mobilitat',
        'Educació',
        'Community Vibe',
        'Centres de Salut'
      ],
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
      showFiltersMenu: false,
      heatmapRectangles: [],
      showHeatmapLayer: false,
      calculationMethod: 'cosine',
      showMethodMenu: false,
      showFiltersMenu: false

    };
  },
  computed: {
    chartData() {
      return {
        labels: this.aspectNames,
        datasets: [{
          label: 'Preferències',
          data: this.preferenceVector.map(v => v * 100),
          backgroundColor: 'rgba(33, 150, 243, 0.2)',
          borderColor: 'rgba(33, 150, 243, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(33, 150, 243, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(33, 150, 243, 1)'
        }]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 20,
              font: {
                size: 9
              },
              color: 'rgba(0, 0, 0, 0.4)',
              backdropColor: 'transparent',
              callback: function(value) {
                return value + '%';
              }
            },
            pointLabels: {
              font: {
                size: 10,
                weight: '500'
              },
              color: '#333'
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.08)'
            },
            angleLines: {
              color: 'rgba(0, 0, 0, 0.08)'
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.parsed.r.toFixed(0) + '%';
              }
            }
          }
        }
      }
    }
  },
  methods: {
    updatePreferenceInstant(index, value) {
      // Actualiza el valor instantáneamente mientras se mueve el slider
      this.preferenceVector[index] = parseFloat(value) / 100;
      this.$forceUpdate();
    },
    
    async updatePreferenceAndRecalculate(index, value) {
      // Actualiza el valor y recalcula el heatmap al soltar el slider
      this.preferenceVector[index] = parseFloat(value) / 100;
      this.$forceUpdate();
      
      // Actualizar el vector en el backend
      try {
        await axios.post('http://localhost:5000/api/update-vector', {
          vector: this.preferenceVector
        });
        
        // Recargar el mapa de calor si existe
        if (this.heatmapRectangles.length > 0 || this.showHeatmapLayer) {
          await this.loadHeatmap();
          
          // Activar automáticamente el mapa de calor si estaba oculto
          if (!this.showHeatmapLayer) {
            this.showHeatmapLayer = true;
            this.heatmapRectangles.forEach(rect => rect.addTo(this.map));
          }
        }
      } catch (err) {
        console.error('Error updating vector:', err);
        this.error = 'Error actualizando preferencias';
      }
    },
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
        
        // Cargar el mapa de calor automáticamente después de generar el vector
        if (response.data.vector && Array.isArray(response.data.vector) && response.data.vector.length === 11) {
          
        // Guardar el vector de preferències
          this.preferenceVector = response.data.vector;
          await this.loadHeatmap();
        } else {
          this.error = 'No s\'ha rebut un vector vàlid de la IA';

        }
        
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
      this.preferenceVector = [];
      this.error = '';
      
      // Limpiar el mapa de calor
      this.heatmapRectangles.forEach(rect => rect.remove());
      this.heatmapRectangles = [];
      this.showHeatmapLayer = false;
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
    
    toggleHeatmapLayer() {
      this.showHeatmapLayer = !this.showHeatmapLayer;
      
      this.heatmapRectangles.forEach(rect => {
        if (this.showHeatmapLayer) {
          rect.addTo(this.map);
        } else {
          rect.remove();
        }
      });
    },
    
    async loadHeatmap() {
      try {
        const response = await axios.get(`http://localhost:5000/api/heatmap?method=${this.calculationMethod}`);
        const { heatmap, rectangle, stats, method } = response.data;
        
        console.log(`Heatmap stats (${method}):`, stats);
        
        this.drawHeatmapGrid(heatmap, rectangle);
      } catch (err) {
        console.error('Error loading heatmap:', err);
        this.error = 'Error cargando el mapa de calor';
      }
    },
    
    async selectMethod(method) {
      this.calculationMethod = method;
      this.showMethodMenu = false;
      
      // Recargar el mapa de calor con el nuevo método si ya hay un vector
      if (this.heatmapRectangles.length > 0) {
        await this.loadHeatmap();
      }
    },
    
    getMethodName(method) {
      const names = {
        'cosine': 'Coseno',
        'ml': 'ML',
        'manhattan': 'Manhattan',
        'weighted': 'Weighted',
        'pearson': 'Pearson'
      };
      return names[method] || 'Coseno';
    },
    
    getVectorLabel(index) {
      const labels = [
        'Income (Precio)',
        'Crimes (Seguridad)',
        'Connectivity (Internet)',
        'Noise (Ruido)',
        'Walkability (15 min)',
        'Accessibility (Acceso)',
        'Wellbeing (Bienestar)',
        'Mobility (Transporte)',
        'Education (Educación)',
        'Community Vibe (Ambiente)',
        'Health (Salud)'
      ];
      return labels[index] || `Índice ${index}`;
    },
    
    async onSliderChange() {
      // Actualizar el vector en el backend
      try {
        await axios.post('http://localhost:5000/api/update-vector', {
          vector: this.userVector
        });
        
        // Recargar el mapa de calor con el nuevo vector
        if (this.heatmapRectangles.length > 0 || this.showHeatmapLayer) {
          await this.loadHeatmap();
          
          // Activar automáticamente el mapa de calor si estaba oculto
          if (!this.showHeatmapLayer) {
            this.showHeatmapLayer = true;
            this.heatmapRectangles.forEach(rect => rect.addTo(this.map));
          }
        }
      } catch (err) {
        console.error('Error updating vector:', err);
      }
    },
    
    getHeatmapColor(similarity) {
      // Gradiente de color basado en similitud (0-1)
      // 0 = Azul (frío, no coincide)
      // 0.5 = Verde/Amarillo (medio)
      // 1 = Rojo (caliente, muy coincidente)
      
      // No mostrar si la similitud es muy baja (menos del 30%)
      if (similarity < 0.3) return null;
      
      let color;
      let opacity;
      
      if (similarity < 0.4) {
        // Azul (baja coincidencia)
        color = 'rgb(0, 100, 255)';
        opacity = 0.4;
      } else if (similarity < 0.5) {
        // Cyan
        color = 'rgb(0, 200, 255)';
        opacity = 0.5;
      } else if (similarity < 0.6) {
        // Verde
        color = 'rgb(0, 255, 100)';
        opacity = 0.6;
      } else if (similarity < 0.7) {
        // Amarillo-Verde
        color = 'rgb(150, 255, 0)';
        opacity = 0.7;
      } else if (similarity < 0.8) {
        // Amarillo
        color = 'rgb(255, 255, 0)';
        opacity = 0.75;
      } else if (similarity < 0.9) {
        // Naranja
        color = 'rgb(255, 150, 0)';
        opacity = 0.85;
      } else {
        // Rojo (alta coincidencia)
        color = 'rgb(255, 0, 0)';
        opacity = 0.9;
      }
      
      return { color, opacity };
    },
    
    drawHeatmapGrid(heatmap, rectangle) {
      // Limpiar rectángulos anteriores
      this.heatmapRectangles.forEach(rect => rect.remove());
      this.heatmapRectangles = [];
      
      const { north, south, west, east } = rectangle;
      const verticalStep = (north - south) / 20;
      const horizontalStep = (east - west) / 20;
      
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 20; j++) {
          const similarity = heatmap[i][j];
          
          const colorData = this.getHeatmapColor(similarity);
          if (!colorData) continue;
          
          const cellNorth = north - (i * verticalStep);
          const cellSouth = cellNorth - verticalStep;
          const cellWest = west + (j * horizontalStep);
          const cellEast = cellWest + horizontalStep;
          
          const bounds = [[cellNorth, cellWest], [cellSouth, cellEast]];
          
          const rectangle = L.rectangle(bounds, {
            color: colorData.color,
            fillColor: colorData.color,
            weight: 1,
            fillOpacity: colorData.opacity
          });
          
          rectangle.bindPopup(`
            <strong>Coincidencia:</strong> ${(similarity * 100).toFixed(1)}%<br>
            <strong>Posición:</strong> [${i}, ${j}]
          `);
          
          this.heatmapRectangles.push(rectangle);
          
          if (this.showHeatmapLayer) {
            rectangle.addTo(this.map);
          }
        }
      }
      
      console.log(`Heatmap dibujado: ${this.heatmapRectangles.length} celdas`);
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

/* Panel de prompt superpuesto a la izquierda */
.prompt-panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 28%;
  max-width: 450px;
  min-width: 320px;
  height: 100vh;
  z-index: 1000;
  overflow-y: auto;
}

.prompt-container {
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin: 10px;
}

/* Responsive design */
@media (max-width: 1400px) {
  .prompt-panel {
    width: 35%;
  }
}

@media (max-width: 1024px) {
  .prompt-panel {
    width: 45%;
    max-width: 400px;
  }
}

@media (max-width: 768px) {
  .prompt-panel {
    width: 100%;
    max-width: 100%;
    height: auto;
    max-height: 60vh;
    position: relative;
  }
  
  #map {
    height: 40vh;
    margin-top: 60vh;
  }
  
  #controls {
    top: calc(60vh + 10px);
  }
}

.prompt-container h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  border-bottom: 2px solid #2196F3;
  padding-bottom: 10px;
}

@media (max-width: 768px) {
  .prompt-container h2 {
    font-size: 16px;
  }
}

.input-section {
  margin-bottom: 15px;
}

.input-section textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  min-height: 100px;
}

.input-section textarea:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

@media (max-width: 768px) {
  .input-section textarea {
    font-size: 12px;
    min-height: 80px;
  }
}

.input-section textarea:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-primary {
  background-color: #2196F3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-secondary {
  background-color: #666;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #555;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.btn-secondary:active:not(:disabled) {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .btn {
    padding: 8px 12px;
    font-size: 12px;
  }
}

.error-message {
  padding: 8px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 12px;
}

.output-section {
  margin-top: 15px;
}

.output-section label {
  display: block;
  margin-bottom: 12px;
  color: #333;
  font-weight: bold;
  font-size: 14px;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #e0e0e0;
}

@media (max-width: 768px) {
  .output-section label {
    font-size: 13px;
  }
}

.output-content {
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 12px;
  line-height: 1.5;
  max-height: 300px;
  overflow-y: auto;
}

/* Gràfic i controls */
.chart-container {
  width: 100%;
  max-width: 100%;
  height: 280px;
  margin: 15px auto;
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-container canvas {
  max-height: 260px !important;
}

@media (min-width: 1400px) {
  .chart-container {
    max-width: 100%;
    height: 320px;
  }
  
  .chart-container canvas {
    max-height: 300px !important;
  }
}

@media (max-width: 768px) {
  .chart-container {
    height: 240px;
    padding: 8px;
  }
  
  .chart-container canvas {
    max-height: 220px !important;
  }
}

.controls-container {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  max-height: 400px;
  overflow-y: auto;
}

.controls-container h3 {
  margin: 0 0 15px 0;
  font-size: 15px;
  color: #333;
  text-align: center;
  font-weight: 600;
  position: sticky;
  top: -15px;
  background: #f8f9fa;
  padding: 10px 0;
  z-index: 10;
}

@media (max-width: 768px) {
  .controls-container {
    max-height: 300px;
  }
  
  .controls-container h3 {
    font-size: 14px;
  }
}

.slider-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.slider-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  transition: box-shadow 0.2s ease;
}

.slider-item:hover {
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.2);
}

.slider-item label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #555;
}

@media (max-width: 768px) {
  .slider-item label {
    font-size: 11px;
  }
}

.value-display {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 11px;
  font-weight: bold;
  min-width: 45px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
}

@media (max-width: 768px) {
  .value-display {
    font-size: 10px;
    padding: 3px 8px;
    min-width: 40px;
  }
}

.slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #e0e0e0 0%, #d3d3d3 100%);
  outline: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.slider:hover {
  background: linear-gradient(to right, #bbdefb 0%, #90caf9 100%);
}

@media (max-width: 768px) {
  .slider {
    height: 10px;
  }
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  cursor: pointer;
  box-shadow: 0 3px 6px rgba(33, 150, 243, 0.4);
  transition: all 0.2s ease;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  cursor: pointer;
  box-shadow: 0 3px 6px rgba(33, 150, 243, 0.4);
  border: none;
  transition: all 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
  transform: scale(1.15);
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.5);
}

.slider::-moz-range-thumb:hover {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
  transform: scale(1.15);
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.5);
}

.slider::-webkit-slider-thumb:active {
  transform: scale(1.05);
}

.slider::-moz-range-thumb:active {
  transform: scale(1.05);
}

@media (max-width: 768px) {
  .slider::-webkit-slider-thumb {
    width: 22px;
    height: 22px;
  }
  
  .slider::-moz-range-thumb {
    width: 22px;
    height: 22px;
  }
}

/* Controles de filtros del mapa a la derecha */
#controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

@media (max-width: 768px) {
  #controls {
    position: fixed;
    bottom: 10px;
    top: auto;
    right: 10px;
    left: 10px;
  }
  
  .filters-menu {
    max-height: 200px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  
  .toggle-btn {
    font-size: 11px;
    padding: 8px 10px;
    min-width: auto;
  }
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

.toggle-btn.heatmap-btn {
  background: linear-gradient(90deg, rgb(0, 100, 255) 0%, rgb(0, 255, 100) 50%, rgb(255, 0, 0) 100%);
  color: white;
  font-weight: bold;
  border: 3px solid #333;
}

.toggle-btn.heatmap-btn:hover {
  box-shadow: 0 5px 15px rgba(255, 0, 0, 0.5);
}

.toggle-btn.heatmap-btn.active {
  border-color: #FFD700;
  box-shadow: 0 5px 15px rgba(255, 215, 0, 0.7);
}

/* Selector de método de cálculo abajo a la derecha */
#method-selector {
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.method-toggle-btn {
  background-color: #673AB7;
  color: white;
  border: 2px solid #512DA8;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 3px 6px rgba(103, 58, 183, 0.4);
  transition: all 0.3s ease;
  min-width: 180px;
  text-align: center;
}

.method-toggle-btn:hover {
  background-color: #512DA8;
  box-shadow: 0 5px 10px rgba(103, 58, 183, 0.5);
}

.method-toggle-btn:active {
  transform: scale(0.98);
}

.method-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.method-btn {
  background-color: #f0f0f0;
  border: 2px solid rgba(0,0,0,0.2);
  border-radius: 4px;
  padding: 10px 15px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
  min-width: 180px;
  color: #666;
  text-align: left;
}

.method-btn:hover {
  background-color: #e0e0e0;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.method-btn:active {
  transform: scale(0.98);
}

.method-btn.active {
  background-color: #673AB7;
  color: white;
  border-color: #512DA8;
  box-shadow: 0 3px 6px rgba(103, 58, 183, 0.4);
}

.method-btn.active:hover {
  background-color: #512DA8;
  box-shadow: 0 5px 10px rgba(103, 58, 183, 0.5);
}
</style>
