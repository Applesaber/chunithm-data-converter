<script setup lang="ts">
</script>

<template>
  <header>
    <div class="nav-container">
      <router-link to="/" class="brand">Chunithm → MuNET</router-link>
      <nav class="nav-links">
        <router-link to="/" class="nav-link">转换器</router-link>
        <router-link to="/visualizer" class="nav-link">可视化</router-link>
      </nav>
    </div>
  </header>

  <main class="container">
    <router-view />
  </main>

  <footer>
    <p>Powered by MuNET-OSS · <a href="https://github.com/MuNET-OSS/chunithm-data-converter" target="_blank" rel="noopener noreferrer">GitHub</a></p>
  </footer>
</template>

<style>
</style>
