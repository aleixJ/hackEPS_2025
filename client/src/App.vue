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
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      userPrompt: '',
      aiOutput: '',
      loading: false,
      error: ''
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
    }
  }
};
</script>

<style scoped>
/* Component-specific styles are in style.css */
</style>
