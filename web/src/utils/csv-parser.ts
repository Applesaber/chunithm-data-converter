import Papa from 'papaparse'
import type { ScoreRecord, CsvFormat } from '../types'
import { calculateRankFromScore } from './converter'

function detectCsvFormat(headers: string[]): 'lxns' | 'shuiyu' | 'unknown' {
  const joined = headers.map(h => h.toLowerCase()).join(',')
  if (joined.includes('排名') || joined.includes('乐曲名') || joined.includes('难度')) {
    return 'shuiyu'
  }
  if (joined.includes('id') || joined.includes('song_name') || joined.includes('level_index')) {
    return 'lxns'
  }
  return 'unknown'
}

function parseLxnsRow(row: Record<string, string>): ScoreRecord | null {
  try {
    return {
      recordId: parseInt(row['id']),
      songName: row['song_name'],
      level: row['level'],
      levelIndex: parseInt(row['level_index']),
      score: parseInt(row['score']),
      rating: parseFloat(row['rating']),
      overPower: parseFloat(row['over_power']),
      clearStatus: row['clear'],
      fullCombo: row['full_combo'] || null,
      fullChain: row['full_chain'] || null,
      rank: row['rank'],
      uploadTime: row['upload_time'],
      playTime: row['play_time'] || null,
    }
  } catch {
    return null
  }
}

function parseShuiyuRow(row: Record<string, string>, rowNum: number): ScoreRecord | null {
  try {
    const scoreVal = parseInt(row['分数'])
    const rank = calculateRankFromScore(scoreVal)
    const levelStr = (row['难度'] || '').trim()

    let levelIndex = 0
    if (levelStr.includes('+')) {
      const base = parseFloat(levelStr.replace('+', ''))
      levelIndex = base >= 10 ? 3 : 2
    } else {
      const num = parseFloat(levelStr)
      levelIndex = num >= 7 ? 1 : 0
    }

    return {
      recordId: rowNum,
      songName: row['乐曲名'],
      level: levelStr,
      levelIndex,
      score: scoreVal,
      rating: parseFloat(row['Rating'] || '0'),
      overPower: 0,
      clearStatus: scoreVal > 0 ? 'clear' : 'failed',
      fullCombo: null,
      fullChain: null,
      rank,
      uploadTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
      playTime: null,
    }
  } catch {
    return null
  }
}

export function parseCsvFile(file: File, format: CsvFormat): Promise<ScoreRecord[]> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete(results) {
        const data = results.data as Record<string, string>[]
        if (data.length === 0) {
          reject(new Error('CSV 文件为空'))
          return
        }

        let detectedFormat = format
        if (format === 'auto') {
          const headers = Object.keys(data[0])
          const detected = detectCsvFormat(headers)
          if (detected === 'unknown') {
            reject(new Error('无法自动检测 CSV 格式，请手动选择落雪或水鱼格式'))
            return
          }
          detectedFormat = detected
        }

        const scores: ScoreRecord[] = []
        for (let i = 0; i < data.length; i++) {
          const row = data[i]
          const record = detectedFormat === 'lxns'
            ? parseLxnsRow(row)
            : parseShuiyuRow(row, i + 1)
          if (record) scores.push(record)
        }

        resolve(scores)
      },
      error(err) {
        reject(new Error(`CSV 解析错误: ${err.message}`))
      },
    })
  })
}
