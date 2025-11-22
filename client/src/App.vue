<template>
  <div id="app">
    <div id="map"></div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import osmtogeojson from 'osmtogeojson';

export default {
  name: 'App',
  mounted() {
    // Create map
    const map = L.map('map').setView([34.0522, -118.2437], 10);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

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
            fillOpacity: 0.2
          }).addTo(map);
          
          // Fit map to rectangle
          map.fitBounds(bounds);
        }
      })
      .catch(error => console.error('Error loading data from server:', error));
  }
};
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}

#map {
  height: 100%;
  width: 100%;
}
</style>
