<script setup lang="ts">
import { zhCN, dateZhCN } from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'
import 'vfonts/Lato.css'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#a18cd1',
    primaryColorHover: '#8a73be',
    primaryColorPressed: '#7057a6',
    primaryColorSuppl: '#e2a9d2',
    bodyColor: 'transparent',
    cardColor: 'rgba(255, 255, 255, 0.7)',
    modalColor: 'rgba(255, 255, 255, 0.8)',
    popoverColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: '16px'
  },
  Card: {
    color: 'rgba(255, 255, 255, 0.7)',
    colorModal: 'rgba(255, 255, 255, 0.8)',
    colorTarget: 'rgba(255, 255, 255, 0.7)',
    borderColor: 'rgba(255, 255, 255, 0.5)',
    borderRadius: '16px',
    boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.05)'
  }
}
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <header>
          <div class="nav-container">
            <router-link to="/" class="brand">水鱼/落雪导入MuNET</router-link>
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
          <p>Power By Applesaber · <a href="https://github.com/MuNET-OSS/chunithm-data-converter" target="_blank" rel="noopener noreferrer">GitHub</a></p>
        </footer>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
</style>
