<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { fetchFromApi, setCorsProxy } from '../utils/api'
import { parseCsvFile } from '../utils/csv-parser'
import { convertScoresToMunet } from '../utils/converter'
import type { ApiMode, CsvFormat, MunetJson } from '../types'

const router = useRouter()

const activeTab = ref<'api' | 'csv'>('api')

const apiMode = ref<ApiMode>('lxns')
const apiForm = reactive({
  lxnsToken: '',
  lxnsDeveloperToken: '',
  lxnsFriendCode: '',
  shuiyuImportToken: '',
  shuiyuDeveloperToken: '',
  shuiyuUsername: '',
  corsProxy: 'https://corsproxy.io/?url='
})
const showAdvanced = ref(false)

// CSV Form state
const csvFormat = ref<CsvFormat>('auto')
const csvUsername = ref('Player')
const csvFile = ref<File | null>(null)
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// Execution state
const isConverting = ref(false)
const progressMessages = ref<string[]>([])
const errorMessage = ref('')
const conversionResult = ref<MunetJson | null>(null)
const resultStats = ref({ scores: 0, musicDetails: 0, playlogs: 0 })

// Helper to add progress messages
const addProgress = (msg: string) => {
  progressMessages.value.push(msg)
}

// Reset state before new conversion
const resetState = () => {
  progressMessages.value = []
  errorMessage.value = ''
  conversionResult.value = null
  resultStats.value = { scores: 0, musicDetails: 0, playlogs: 0 }
}

// Handle API conversion
const handleApiConversion = async () => {
  if (isConverting.value) return
  resetState()
  isConverting.value = true
  
  try {
    setCorsProxy(apiForm.corsProxy)
    
    // Parse friend code if needed
    let friendCode: number | undefined
    if (apiMode.value === 'lxns-dev') {
      friendCode = parseInt(apiForm.lxnsFriendCode, 10)
      if (isNaN(friendCode)) {
        throw new Error('好友码必须是数字')
      }
    }
    
    const { player, scores } = await fetchFromApi(apiMode.value, {
      lxnsToken: apiForm.lxnsToken,
      lxnsDeveloperToken: apiForm.lxnsDeveloperToken,
      lxnsFriendCode: friendCode,
      shuiyuImportToken: apiForm.shuiyuImportToken,
      shuiyuDeveloperToken: apiForm.shuiyuDeveloperToken,
      shuiyuUsername: apiForm.shuiyuUsername,
      onProgress: addProgress
    })
    
    addProgress(`获取到 ${scores.length} 条成绩记录`)
    addProgress('正在转换为 MuNET 格式...')
    
    const munetData = convertScoresToMunet(scores, player)
    finishConversion(munetData, scores.length)
    
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '转换过程中发生未知错误'
  } finally {
    isConverting.value = false
  }
}

// Handle File Drop
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
  if (!file.name.toLowerCase().endsWith('.csv')) {
    errorMessage.value = '只能上传 CSV 文件'
    return
  }
  errorMessage.value = ''
  csvFile.value = file
}

// Handle CSV conversion
const handleCsvConversion = async () => {
  if (isConverting.value || !csvFile.value) return
  resetState()
  isConverting.value = true
  
  try {
    addProgress(`正在读取文件: ${csvFile.value.name}`)
    const scores = await parseCsvFile(csvFile.value, csvFormat.value)
    
    addProgress(`成功解析 ${scores.length} 条成绩记录`)
    addProgress('正在转换为 MuNET 格式...')
    
    const munetData = convertScoresToMunet(scores, null, csvUsername.value)
    finishConversion(munetData, scores.length)
    
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '解析 CSV 文件失败'
  } finally {
    isConverting.value = false
  }
}

const finishConversion = (data: MunetJson, scoresCount: number) => {
  conversionResult.value = data
  resultStats.value = {
    scores: scoresCount,
    musicDetails: data.userMusicDetailList.length,
    playlogs: data.userPlaylogList.length
  }
  addProgress('转换完成！')
}

// Download JSON
const downloadJson = () => {
  if (!conversionResult.value) return
  
  const jsonStr = JSON.stringify(conversionResult.value)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = 'chunithm_munet_export.json'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// View in Visualizer
const viewVisualizer = () => {
  if (!conversionResult.value) return
  
  try {
    sessionStorage.setItem('munetData', JSON.stringify(conversionResult.value))
    router.push('/visualizer')
  } catch (e) {
    errorMessage.value = '数据过大，无法保存到会话中，请先下载文件后在可视化页面手动上传。'
  }
}

const isApiFormValid = computed(() => {
  switch (apiMode.value) {
    case 'lxns': return !!apiForm.lxnsToken
    case 'lxns-dev': return !!apiForm.lxnsDeveloperToken && !!apiForm.lxnsFriendCode
    case 'shuiyu': return !!apiForm.shuiyuImportToken
    case 'shuiyu-dev': return !!apiForm.shuiyuDeveloperToken && !!apiForm.shuiyuUsername
    default: return false
  }
})
</script>

<template>
  <div>
    <div class="card mb-6">
      <div class="tabs">
        <button 
          class="tab" 
          :class="{ active: activeTab === 'api' }" 
          @click="activeTab = 'api'"
        >API 模式</button>
        <button 
          class="tab" 
          :class="{ active: activeTab === 'csv' }" 
          @click="activeTab = 'csv'"
        >CSV 上传</button>
      </div>

      <!-- API Mode Form -->
      <div v-if="activeTab === 'api'">
        <div class="form-group">
          <label class="form-label">选择模式</label>
          <select v-model="apiMode" class="select" :disabled="isConverting">
            <option value="lxns">落雪个人 (通过 Token 获取个人数据)</option>
            <option value="lxns-dev">落雪开发者 (通过好友码获取他人数据)</option>
            <option value="shuiyu">水鱼个人 (通过 Import-Token 获取个人数据)</option>
            <option value="shuiyu-dev">水鱼开发者 (通过用户名获取他人数据)</option>
          </select>
        </div>

        <div v-if="apiMode === 'lxns'" class="form-group">
          <label class="form-label">落雪个人令牌</label>
          <input 
            v-model="apiForm.lxnsToken" 
            type="password" 
            class="input" 
            placeholder="输入你的落雪个人 Token"
            :disabled="isConverting"
          />
        </div>

        <template v-if="apiMode === 'lxns-dev'">
          <div class="form-group">
            <label class="form-label">落雪开发者令牌</label>
            <input 
              v-model="apiForm.lxnsDeveloperToken" 
              type="password" 
              class="input" 
              placeholder="输入你的开发者 Token"
              :disabled="isConverting"
            />
          </div>
          <div class="form-group">
            <label class="form-label">好友码</label>
            <input 
              v-model="apiForm.lxnsFriendCode" 
              type="text" 
              class="input" 
              placeholder="输入目标玩家的 10 位数字好友码"
              :disabled="isConverting"
            />
          </div>
        </template>

        <div v-if="apiMode === 'shuiyu'" class="form-group">
          <label class="form-label">水鱼 Import-Token</label>
          <input 
            v-model="apiForm.shuiyuImportToken" 
            type="password" 
            class="input" 
            placeholder="输入你的水鱼 Import-Token"
            :disabled="isConverting"
          />
        </div>

        <template v-if="apiMode === 'shuiyu-dev'">
          <div class="form-group">
            <label class="form-label">水鱼 Developer-Token</label>
            <input 
              v-model="apiForm.shuiyuDeveloperToken" 
              type="password" 
              class="input" 
              placeholder="输入你的开发者 Token"
              :disabled="isConverting"
            />
          </div>
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input 
              v-model="apiForm.shuiyuUsername" 
              type="text" 
              class="input" 
              placeholder="输入目标玩家的用户名"
              :disabled="isConverting"
            />
          </div>
        </template>

        <!-- Advanced settings -->
        <div class="mt-4 mb-6">
          <button class="btn btn-secondary w-full" @click="showAdvanced = !showAdvanced" :disabled="isConverting">
            {{ showAdvanced ? '隐藏高级设置' : '显示高级设置 (CORS 代理)' }}
          </button>
          
          <div v-show="showAdvanced" class="form-group mt-4">
            <label class="form-label">CORS 代理 (解决浏览器跨域问题)</label>
            <input 
              v-model="apiForm.corsProxy" 
              type="text" 
              class="input" 
              placeholder="如 https://corsproxy.io/?url="
              :disabled="isConverting"
            />
          </div>
        </div>

        <button 
          class="btn btn-primary btn-block" 
          @click="handleApiConversion" 
          :disabled="!isApiFormValid || isConverting"
        >
          {{ isConverting ? '正在转换...' : '开始转换' }}
        </button>
      </div>

      <!-- CSV Mode Form -->
      <div v-if="activeTab === 'csv'">
        <div class="form-group">
          <label class="form-label">上传 CSV 文件</label>
          <div 
            class="dropzone" 
            :class="{ 'drag-active': isDragging }"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
            @click="() => fileInput?.click()"
          >
            <input 
              type="file" 
              ref="fileInput" 
              accept=".csv" 
              style="display: none" 
              @change="onFileChange"
              :disabled="isConverting"
            />
            <div v-if="!csvFile">
              <p>点击选择或拖拽 .csv 文件到此处</p>
              <p style="font-size: 0.875rem; color: var(--text-muted)">支持落雪或水鱼导出的成绩 CSV 文件</p>
            </div>
            <div v-else>
              <p style="color: var(--primary-color); font-weight: bold;">已选择: {{ csvFile.name }}</p>
              <p style="font-size: 0.875rem; color: var(--text-muted)">点击或拖拽可更换文件</p>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">格式</label>
          <select v-model="csvFormat" class="select" :disabled="isConverting">
            <option value="auto">自动检测</option>
            <option value="lxns">落雪格式</option>
            <option value="shuiyu">水鱼格式</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">用户名 (当 CSV 不包含用户名时使用)</label>
          <input 
            v-model="csvUsername" 
            type="text" 
            class="input" 
            placeholder="Player"
            :disabled="isConverting"
          />
        </div>

        <button 
          class="btn btn-primary btn-block mt-6" 
          @click="handleCsvConversion" 
          :disabled="!csvFile || isConverting"
        >
          {{ isConverting ? '正在转换...' : '开始转换' }}
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>

    <!-- Progress Output -->
    <div v-if="progressMessages.length > 0" class="card mb-6" style="background-color: var(--bg-color)">
      <h3 style="font-size: 1rem; margin-bottom: 0.5rem">运行日志</h3>
      <div style="font-family: monospace; font-size: 0.875rem; max-height: 200px; overflow-y: auto; color: var(--text-secondary)">
        <div v-for="(msg, i) in progressMessages" :key="i">[{{ new Date().toLocaleTimeString() }}] {{ msg }}</div>
      </div>
    </div>

    <!-- Success Output -->
    <div v-if="conversionResult" class="card" style="border-color: var(--success-color); box-shadow: 0 0 15px var(--success-bg)">
      <h2 style="color: var(--success-color); margin-bottom: 1rem;">转换成功！</h2>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ resultStats.scores }}</div>
          <div class="stat-label">成绩数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ resultStats.musicDetails }}</div>
          <div class="stat-label">音乐详情数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ resultStats.playlogs }}</div>
          <div class="stat-label">游玩记录数</div>
        </div>
      </div>

      <div class="flex gap-4 mt-6">
        <button class="btn btn-primary flex-1" @click="downloadJson">
          下载 JSON 文件
        </button>
        <button class="btn btn-secondary flex-1" @click="viewVisualizer">
          查看可视化分析
        </button>
      </div>
    </div>
  </div>
</template>
