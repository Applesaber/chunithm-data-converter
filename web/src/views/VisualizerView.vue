<script setup lang="ts">
import { ref, computed, onMounted, shallowRef } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import 'chart.js/auto'
import type { MunetJson, MusicDetail } from '../types'

// Data state
const munetData = shallowRef<MunetJson | null>(null)
const errorMessage = ref('')
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// Table state
const sortKey = ref<keyof MusicDetail | 'levelName' | 'rankName'>('scoreMax')
const sortDesc = ref(true)
const currentPage = ref(1)
const itemsPerPage = 50

// Constants for mapping
const LEVEL_NAMES = ['BASIC', 'ADVANCED', 'EXPERT', 'MASTER', 'ULTIMA']
const LEVEL_CLASSES = ['level-bas', 'level-adv', 'level-exp', 'level-mas', 'level-ult']

// Check sessionStorage on mount
onMounted(() => {
  try {
    const saved = sessionStorage.getItem('munetData')
    if (saved) {
      munetData.value = JSON.parse(saved) as MunetJson
    }
  } catch (e) {
    console.error('Failed to load from sessionStorage:', e)
  }
})

// File handling
const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}
const onDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
}
const onDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFileSelect(files[0])
  }
}
const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0])
  }
}
const handleFileSelect = (file: File) => {
  if (!file.name.toLowerCase().endsWith('.json')) {
    errorMessage.value = '只能上传 JSON 文件'
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target?.result as string)
      if (!data.userMusicDetailList) {
        throw new Error('无效的数据格式: 缺少 userMusicDetailList')
      }
      munetData.value = data
      errorMessage.value = ''
      currentPage.value = 1
    } catch (err) {
      errorMessage.value = err instanceof Error ? err.message : '解析 JSON 失败'
    }
  }
  reader.readAsText(file)
}

const loadDemoData = () => {
  const mockMusicList: MusicDetail[] = []
  for (let i = 0; i < 200; i++) {
    const level = Math.floor(Math.random() * 5)
    const scoreRank = Math.floor(Math.random() * 3) + 3
    mockMusicList.push({
      musicId: 1000 + i,
      level,
      playCount: Math.floor(Math.random() * 20) + 1,
      scoreMax: 950000 + Math.floor(Math.random() * 60000),
      missCount: Math.floor(Math.random() * 10),
      maxComboCount: Math.floor(Math.random() * 1000),
      fullChain: 0,
      maxChain: 0,
      scoreRank,
      theoryCount: 0,
      ext1: 0,
      isFullCombo: Math.random() > 0.7,
      isAllJustice: Math.random() > 0.9,
      isSuccess: Math.random() > 0.1 ? 1 : 0,
      isLock: false
    })
  }

  munetData.value = {
    gameId: 'SDEZ',
    userData: {
      userName: 'Demo Player',
      playerRating: 165000,
      totalHiScore: 1234567890,
      playCount: 456,
      overPowerPoint: 8520
    },
    userGameOption: {},
    userActivityList: [],
    userCharacterList: [],
    userItemList: [],
    userMapList: [],
    userMusicDetailList: mockMusicList,
    userCourseList: [],
    userChargeList: [],
    userPlaylogList: []
  }
  errorMessage.value = ''
  currentPage.value = 1
}

const resetData = () => {
  munetData.value = null
  sessionStorage.removeItem('munetData')
}

const playerInfo = computed(() => {
  if (!munetData.value) return null
  const ud = munetData.value.userData as Record<string, unknown>
  return {
    name: (ud.userName as string) || 'Unknown Player',
    rating: ud.playerRating ? ((ud.playerRating as number) / 100).toFixed(2) : '0.00',
    totalScore: (ud.totalHiScore as number) || 0,
    playCount: (ud.playCount as number) || 0,
    overPower: ud.overPowerPoint ? ((ud.overPowerPoint as number) / 100).toFixed(2) : '0.00'
  }
})

const stats = computed(() => {
  if (!munetData.value) return { total: 0, clear: 0, fc: 0, aj: 0 }
  const list = munetData.value.userMusicDetailList || []
  return {
    total: list.length,
    clear: list.filter(m => m.isSuccess > 0).length,
    fc: list.filter(m => m.isFullCombo).length,
    aj: list.filter(m => m.isAllJustice).length
  }
})

const chartTheme = {
  text: '#94a3b8',
  grid: '#2d2b3d'
}

const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  color: chartTheme.text,
  plugins: {
    legend: { labels: { color: chartTheme.text } }
  }
}

const barChartOptions = {
  ...commonOptions,
  scales: {
    x: { grid: { display: false }, ticks: { color: chartTheme.text } },
    y: { grid: { color: chartTheme.grid }, ticks: { color: chartTheme.text } }
  }
}

const scoreDistData = computed(() => {
  if (!munetData.value) return { labels: [], datasets: [] }
  
  const counts: Record<string, number> = { 'D-B': 0, 'A-AA': 0, 'AAA': 0, 'S': 0, 'S+': 0, 'SS': 0, 'SS+': 0, 'SSS': 0, 'SSS+': 0 }
  
  munetData.value.userMusicDetailList.forEach(m => {
    const s = m.scoreMax
    if (s >= 1009000) counts['SSS+']++
    else if (s >= 1007500) counts['SSS']++
    else if (s >= 1005000) counts['SS+']++
    else if (s >= 1000000) counts['SS']++
    else if (s >= 990000) counts['S+']++
    else if (s >= 975000) counts['S']++
    else if (s >= 950000) counts['AAA']++
    else if (s >= 900000) counts['A-AA']++
    else counts['D-B']++
  })

  return {
    labels: Object.keys(counts),
    datasets: [{
      label: '曲目数量',
      data: Object.values(counts),
      backgroundColor: 'rgba(139, 92, 246, 0.7)',
      borderColor: '#8b5cf6',
      borderWidth: 1,
      borderRadius: 4
    }]
  }
})

const diffDistData = computed(() => {
  if (!munetData.value) return { labels: [], datasets: [] }
  
  const counts = [0, 0, 0, 0, 0] // BAS, ADV, EXP, MAS, ULT
  munetData.value.userMusicDetailList.forEach(m => {
    if (m.level >= 0 && m.level <= 4) {
      counts[m.level]++
    }
  })

  return {
    labels: LEVEL_NAMES,
    datasets: [{
      data: counts,
      backgroundColor: [
        '#10b981', // BAS (Green)
        '#f59e0b', // ADV (Yellow)
        '#ef4444', // EXP (Red)
        '#a855f7', // MAS (Purple)
        '#64748b'  // ULT (Gray/Blackish normally, using gray for dark theme visibility)
      ],
      borderWidth: 0,
      hoverOffset: 4
    }]
  }
})

const sortedMusicList = computed(() => {
  if (!munetData.value) return []
  
  let list = [...munetData.value.userMusicDetailList]
  
  list.sort((a, b) => {
    const aRecord = a as unknown as Record<string, number | string | boolean>
    const bRecord = b as unknown as Record<string, number | string | boolean>
    let valA = aRecord[sortKey.value as string]
    let valB = bRecord[sortKey.value as string]
    
    // Virtual fields
    if (sortKey.value === 'levelName') {
      valA = a.level
      valB = b.level
    } else if (sortKey.value === 'rankName') {
      valA = a.scoreRank
      valB = b.scoreRank
    }
    
    if (valA < valB) return sortDesc.value ? 1 : -1
    if (valA > valB) return sortDesc.value ? -1 : 1
    return 0
  })
  
  return list
})

const totalPages = computed(() => Math.ceil(sortedMusicList.value.length / itemsPerPage))

const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return sortedMusicList.value.slice(start, end)
})

const sortBy = (key: string) => {
  if (sortKey.value === key) {
    sortDesc.value = !sortDesc.value
  } else {
    sortKey.value = key as keyof MusicDetail | 'levelName' | 'rankName'
    sortDesc.value = true
  }
  currentPage.value = 1
}

const formatScore = (score: number) => {
  return score.toLocaleString()
}

const getRankName = (score: number) => {
  if (score >= 1009000) return 'SSS+'
  if (score >= 1007500) return 'SSS'
  if (score >= 1005000) return 'SS+'
  if (score >= 1000000) return 'SS'
  if (score >= 990000) return 'S+'
  if (score >= 975000) return 'S'
  if (score >= 950000) return 'AAA'
  if (score >= 925000) return 'AA'
  if (score >= 900000) return 'A'
  if (score >= 800000) return 'B'
  if (score >= 700000) return 'C'
  return 'D'
}
</script>

<template>
  <div>
    <!-- Upload Section if no data -->
    <div v-if="!munetData" class="card text-center py-10" style="padding: 4rem 2rem;">
      <h2 class="mb-6">数据可视化</h2>
      <p class="mb-6" style="color: var(--text-secondary)">上传 MuNET 格式的 JSON 导出文件，分析你的游玩数据。</p>
      
      <div 
        class="dropzone mb-6" 
        style="max-width: 600px; margin: 0 auto 1.5rem auto;"
        :class="{ 'drag-active': isDragging }"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
        @click="() => fileInput?.click()"
      >
        <input 
          type="file" 
          ref="fileInput" 
          accept=".json" 
          style="display: none" 
          @change="onFileChange"
        />
        <div>
          <svg style="width: 48px; height: 48px; margin: 0 auto 1rem auto; color: var(--primary-color);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p>点击选择或拖拽 .json 文件到此处</p>
        </div>
      </div>
      
      <div v-if="errorMessage" class="error-message max-w-lg mx-auto mb-6">
        {{ errorMessage }}
      </div>

      <div class="mt-6">
        <span class="text-muted mr-4">没有数据？</span>
        <button class="btn btn-secondary" @click="loadDemoData">加载示例数据</button>
      </div>
    </div>

    <!-- Dashboard if data loaded -->
    <div v-else>
      <div class="flex justify-between items-center mb-6">
        <h2 style="margin: 0">玩家数据分析</h2>
        <button class="btn btn-secondary" @click="resetData">清除数据</button>
      </div>

      <!-- Player Info Card -->
      <div class="card mb-6" style="background: var(--primary-gradient); color: white; border: none;">
        <div class="flex" style="flex-wrap: wrap; gap: 2rem; align-items: center;">
          <div style="flex: 1; min-width: 200px;">
            <div style="font-size: 0.875rem; opacity: 0.8;">PLAYER</div>
            <div style="font-size: 2.5rem; font-weight: 700; line-height: 1.2;">{{ playerInfo?.name }}</div>
          </div>
          <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div>
              <div style="font-size: 0.875rem; opacity: 0.8;">RATING</div>
              <div style="font-size: 1.5rem; font-weight: 600;">{{ playerInfo?.rating }}</div>
            </div>
            <div>
              <div style="font-size: 0.875rem; opacity: 0.8;">OVERPOWER</div>
              <div style="font-size: 1.5rem; font-weight: 600;">{{ playerInfo?.overPower }}</div>
            </div>
            <div>
              <div style="font-size: 0.875rem; opacity: 0.8;">TOTAL SCORE</div>
              <div style="font-size: 1.5rem; font-weight: 600;">{{ playerInfo?.totalScore.toLocaleString() }}</div>
            </div>
            <div>
              <div style="font-size: 0.875rem; opacity: 0.8;">PLAY COUNT</div>
              <div style="font-size: 1.5rem; font-weight: 600;">{{ playerInfo?.playCount }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value" style="color: #60a5fa">{{ stats.total }}</div>
          <div class="stat-label">总游玩曲目数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: #34d399">{{ stats.clear }}</div>
          <div class="stat-label">通关数 (Clear)</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: #f87171">{{ stats.fc }}</div>
          <div class="stat-label">FC 数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: #fbbf24">{{ stats.aj }}</div>
          <div class="stat-label">AJ 数量</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid">
        <div class="card">
          <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">成绩分布</h3>
          <div class="chart-container" style="height: 280px; padding: 0; background: transparent; border: none;">
            <Bar :data="scoreDistData" :options="barChartOptions" />
          </div>
        </div>
        <div class="card">
          <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">难度分布</h3>
          <div class="chart-container" style="height: 280px; padding: 0; background: transparent; border: none;">
            <Doughnut :data="diffDistData" :options="commonOptions" />
          </div>
        </div>
      </div>

      <!-- Detailed Table -->
      <div class="card">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">游玩详情 (共 {{ sortedMusicList.length }} 首)</h3>
        
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th @click="sortBy('musicId')">
                  音乐 ID <span v-if="sortKey==='musicId'">{{ sortDesc ? '↓' : '↑' }}</span>
                </th>
                <th @click="sortBy('levelName')">
                  难度 <span v-if="sortKey==='levelName'">{{ sortDesc ? '↓' : '↑' }}</span>
                </th>
                <th @click="sortBy('scoreMax')">
                  最高分 <span v-if="sortKey==='scoreMax'">{{ sortDesc ? '↓' : '↑' }}</span>
                </th>
                <th>评级</th>
                <th @click="sortBy('isSuccess')" class="text-center">Clear</th>
                <th @click="sortBy('isFullCombo')" class="text-center">FC</th>
                <th @click="sortBy('isAllJustice')" class="text-center">AJ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedList" :key="`${item.musicId}-${item.level}`">
                <td style="font-family: monospace;">{{ item.musicId }}</td>
                <td>
                  <span class="badge" :class="LEVEL_CLASSES[item.level] || 'badge-gray'">
                    {{ LEVEL_NAMES[item.level] || 'UNKNOWN' }}
                  </span>
                </td>
                <td style="font-family: monospace; font-weight: 600;">{{ formatScore(item.scoreMax) }}</td>
                <td>
                  <span class="badge badge-purple" style="width: 40px; text-align: center;">
                    {{ getRankName(item.scoreMax) }}
                  </span>
                </td>
                <td class="text-center">
                  <span v-if="item.isSuccess > 0" class="badge badge-green">Clear</span>
                  <span v-else style="color: var(--border-color)">-</span>
                </td>
                <td class="text-center">
                  <span v-if="item.isFullCombo" class="badge badge-red">FC</span>
                  <span v-else style="color: var(--border-color)">-</span>
                </td>
                <td class="text-center">
                  <span v-if="item.isAllJustice" class="badge badge-yellow">AJ</span>
                  <span v-else style="color: var(--border-color)">-</span>
                </td>
              </tr>
              <tr v-if="paginatedList.length === 0">
                <td colspan="7" class="text-center" style="padding: 2rem; color: var(--text-muted);">
                  暂无数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-between items-center mt-4">
          <button 
            class="btn btn-secondary" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >上一页</button>
          <span style="color: var(--text-secondary)">第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button 
            class="btn btn-secondary" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>
