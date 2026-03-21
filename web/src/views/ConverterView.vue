<script setup lang="ts">
import type { UploadFileInfo } from 'naive-ui'
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { fetchFromApi } from '../utils/api'
import { parseCsvFile } from '../utils/csv-parser'
import { convertScoresToMunet } from '../utils/converter'
import type { ApiMode, CsvFormat, MunetJson } from '../types'

const router = useRouter()

const activeTab = ref<'api' | 'csv'>('api')

const apiMode = ref<ApiMode>('lxns')
const apiForm = reactive({
  lxnsToken: '',
  lxnsDeveloperToken: import.meta.env.VITE_LXNS_DEVELOPER_TOKEN || '',
  lxnsFriendCode: '',
  shuiyuImportToken: '',
  shuiyuDeveloperToken: import.meta.env.VITE_SHUIYU_DEVELOPER_TOKEN || '',
  shuiyuUsername: ''
})

// CSV Form state
const csvFormat = ref<CsvFormat>('auto')
const csvUsername = ref('Player')
const csvFile = ref<File | null>(null)

const apiModeOptions = [
  { label: '落雪个人 (通过 Token 获取个人数据)', value: 'lxns' },
  { label: '落雪开发者 (通过好友码获取他人数据)', value: 'lxns-dev' },
  { label: '水鱼个人 (通过 Import-Token 获取个人数据)', value: 'shuiyu' },
  { label: '水鱼开发者 (通过用户名获取他人数据)', value: 'shuiyu-dev' }
]

const csvFormatOptions = [
  { label: '自动检测', value: 'auto' },
  { label: '落雪格式', value: 'lxns' },
  { label: '水鱼格式', value: 'shuiyu' }
]

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

const onUploadChange = (options: { file: UploadFileInfo }) => {
  if (options.file.file) {
    if (!options.file.name.toLowerCase().endsWith('.csv')) {
      errorMessage.value = '只能上传 CSV 文件'
      return
    }
    errorMessage.value = ''
    csvFile.value = options.file.file
  }
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
  
  const jsonStr = JSON.stringify(conversionResult.value, null, 2)
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
  <div class="converter-container">
    <n-card class="mb-6" style="border-radius: var(--radius-lg); background-color: var(--card-bg);">
      <n-tabs v-model:value="activeTab" type="segment" animated size="large">
        <n-tab-pane name="api" tab="API 模式">
          <!-- API Mode Form -->
          <n-form :disabled="isConverting" size="large" label-placement="top">
            <n-form-item label="选择模式">
              <n-select v-model:value="apiMode" :options="apiModeOptions" />
            </n-form-item>

            <n-form-item v-if="apiMode === 'lxns'" label="落雪个人令牌">
              <n-input 
                v-model:value="apiForm.lxnsToken" 
                type="password" 
                show-password-on="click" 
                placeholder="输入你的落雪个人 Token"
              />
            </n-form-item>

            <template v-if="apiMode === 'lxns-dev'">
              <n-alert v-if="!apiForm.lxnsDeveloperToken" type="warning" class="mb-4" :show-icon="false">
                此站点尚未配置落雪开发者 Token 环境变量，该模式不可用。
              </n-alert>
              <n-form-item label="好友码">
                <n-input 
                  v-model:value="apiForm.lxnsFriendCode" 
                  placeholder="输入目标玩家的好友码"
                  :disabled="!apiForm.lxnsDeveloperToken"
                />
              </n-form-item>
            </template>

            <n-form-item v-if="apiMode === 'shuiyu'" label="水鱼 Import-Token">
              <n-input 
                v-model:value="apiForm.shuiyuImportToken" 
                type="password" 
                show-password-on="click" 
                placeholder="输入你的水鱼 Import-Token"
              />
            </n-form-item>

            <template v-if="apiMode === 'shuiyu-dev'">
              <n-alert v-if="!apiForm.shuiyuDeveloperToken" type="warning" class="mb-4" :show-icon="false">
                此站点尚未配置水鱼开发者 Token 环境变量，该模式不可用。
              </n-alert>
              <n-form-item label="用户名">
                <n-input 
                  v-model:value="apiForm.shuiyuUsername" 
                  placeholder="输入目标玩家的用户名"
                  :disabled="!apiForm.shuiyuDeveloperToken"
                />
              </n-form-item>
            </template>


            <n-button 
              type="primary" 
              block 
              size="large"
              :loading="isConverting"
              :disabled="!isApiFormValid"
              @click="handleApiConversion"
            >
              开始转换
            </n-button>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="csv" tab="CSV 上传">
          <!-- CSV Mode Form -->
          <n-form :disabled="isConverting" size="large" label-placement="top">
            <n-form-item label="上传 CSV 文件">
              <n-upload
                :default-upload="false"
                :show-file-list="false"
                accept=".csv"
                @change="onUploadChange"
              >
                <n-upload-dragger>
                  <div v-if="!csvFile" style="padding: 24px">
                    <n-text style="font-size: 16px">
                      点击选择或拖拽 .csv 文件到此处
                    </n-text>
                    <n-p depth="3" style="margin: 8px 0 0 0">
                      支持落雪或水鱼导出的成绩 CSV 文件
                    </n-p>
                  </div>
                  <div v-else style="padding: 24px">
                    <n-text style="color: var(--primary-color); font-weight: bold; font-size: 16px">
                      已选择: {{ csvFile.name }}
                    </n-text>
                    <n-p depth="3" style="margin: 8px 0 0 0">
                      点击或拖拽可更换文件
                    </n-p>
                  </div>
                </n-upload-dragger>
              </n-upload>
            </n-form-item>

            <n-form-item label="格式">
              <n-select v-model:value="csvFormat" :options="csvFormatOptions" />
            </n-form-item>

            <n-form-item label="用户名 (当 CSV 不包含用户名时使用)">
              <n-input 
                v-model:value="csvUsername" 
                placeholder="Player"
              />
            </n-form-item>

            <n-button 
              type="primary" 
              block 
              size="large"
              class="mt-6"
              :loading="isConverting"
              :disabled="!csvFile"
              @click="handleCsvConversion"
            >
              开始转换
            </n-button>
          </n-form>
        </n-tab-pane>
      </n-tabs>

      <!-- Error Message -->
      <n-alert v-if="errorMessage" title="错误" type="error" class="mt-6">
        {{ errorMessage }}
      </n-alert>
    </n-card>

    <!-- Progress Output -->
    <n-card v-if="progressMessages.length > 0" class="mb-6" style="border-radius: var(--radius-lg); background-color: var(--bg-color);" title="运行日志" size="small">
      <div style="font-family: monospace; font-size: 0.875rem; max-height: 200px; overflow-y: auto; color: var(--text-secondary)">
        <div v-for="(msg, i) in progressMessages" :key="i">[{{ new Date().toLocaleTimeString() }}] {{ msg }}</div>
      </div>
    </n-card>

    <!-- Success Output -->
    <n-card v-if="conversionResult" style="border-radius: var(--radius-lg); border-color: var(--success-color); box-shadow: 0 0 15px var(--success-bg)">
      <template #header>
        <span style="color: var(--success-color);">转换成功！</span>
      </template>
      
      <n-grid x-gap="12" :cols="3" class="mb-6 text-center">
        <n-gi>
          <n-statistic label="成绩数量" :value="resultStats.scores" />
        </n-gi>
        <n-gi>
          <n-statistic label="音乐详情数" :value="resultStats.musicDetails" />
        </n-gi>
        <n-gi>
          <n-statistic label="游玩记录数" :value="resultStats.playlogs" />
        </n-gi>
      </n-grid>

      <n-space justify="center" size="large">
        <n-button type="primary" size="large" @click="downloadJson">
          下载 JSON 文件
        </n-button>
        <n-button secondary size="large" @click="viewVisualizer">
          查看可视化分析
        </n-button>
      </n-space>
    </n-card>
  </div>
</template>
