<script setup lang="ts">
import { zhCN, dateZhCN } from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'
import 'vfonts/Lato.css'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#18a058',
    primaryColorHover: '#36ad6a',
    primaryColorPressed: '#0c7a43',
    primaryColorSuppl: '#36ad6a'
  }
}
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
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
          <p>Powered by MuNET-OSS · Power By Applesaber · <a href="https://github.com/MuNET-OSS/chunithm-data-converter" target="_blank" rel="noopener noreferrer">GitHub</a></p>
        </footer>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
</style>
