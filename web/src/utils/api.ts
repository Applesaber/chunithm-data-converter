import type { PlayerInfo, ScoreRecord, ApiMode } from '../types'
import { calculateRankFromScore } from './converter'

const LXNS_BASE_URL = 'https://maimai.lxns.net/api/v0'
const SHUIYU_BASE_URL = 'https://www.diving-fish.com/api/chunithmprober'

async function fetchJson(url: string, headers: Record<string, string>): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'GET',
      headers: { ...headers, 'Content-Type': 'application/json' },
    })
  } catch (e) {
    console.warn('Direct fetch failed, falling back to allorigins proxy', e);
    const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
    res = await fetch(proxyUrl, {
      method: 'GET',
      headers: { ...headers, 'Content-Type': 'application/json' },
    });
  }

  if (!res.ok) {
    if (res.status === 401) throw new Error('认证失败：请检查令牌是否正确')
    if (res.status === 403) throw new Error('权限不足：令牌无访问权限')
    if (res.status === 429) throw new Error('请求过于频繁，请稍后重试')
    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  }

  return res.json()
}

function parseLxnsPlayer(data: Record<string, unknown>): PlayerInfo {
  return {
    name: (data['name'] as string) || '',
    level: Number(data['level'] || 0),
    rating: Number(data['rating'] || 0),
    ratingPossession: (data['rating_possession'] as string) || '',
    friendCode: Number(data['friend_code'] || 0),
    rebornCount: Number(data['reborn_count'] || 0),
    overPower: Number(data['over_power'] || 0),
    overPowerProgress: Number(data['over_power_progress'] || 0),
    currency: Number(data['currency'] || 0),
    totalCurrency: Number(data['total_currency'] || 0),
    totalPlayCount: Number(data['total_play_count'] || 0),
    trophy: (data['trophy'] as Record<string, unknown>) || null,
    character: (data['character'] as Record<string, unknown>) || null,
    namePlate: (data['name_plate'] as Record<string, unknown>) || null,
    mapIcon: (data['map_icon'] as Record<string, unknown>) || null,
    classEmblem: (data['class_emblem'] as Record<string, unknown>) || null,
    uploadTime: (data['upload_time'] as string) || '',
  }
}

function parseLxnsScore(s: Record<string, unknown>): ScoreRecord {
  return {
    recordId: Number(s['id'] || 0),
    songName: (s['song_name'] as string) || '',
    level: (s['level'] as string) || '',
    levelIndex: Number(s['level_index'] || 0),
    score: Number(s['score'] || 0),
    rating: Number(s['rating'] || 0),
    overPower: Number(s['over_power'] || 0),
    clearStatus: (s['clear'] as string) || '',
    fullCombo: (s['full_combo'] as string) || null,
    fullChain: (s['full_chain'] as string) || null,
    rank: (s['rank'] as string) || '',
    uploadTime: (s['upload_time'] as string) || '',
    playTime: (s['play_time'] as string) || null,
  }
}

function parseShuiyuPlayer(data: Record<string, unknown>): PlayerInfo {
  return {
    name: (data['nickname'] as string) || '',
    level: 0,
    rating: Number(data['rating'] || 0),
    ratingPossession: '',
    friendCode: 0,
    rebornCount: 0,
    overPower: 0,
    overPowerProgress: 0,
    currency: 0,
    totalCurrency: 0,
    totalPlayCount: 0,
    trophy: null,
    character: null,
    namePlate: null,
    mapIcon: null,
    classEmblem: null,
    uploadTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
  }
}

function parseShuiyuScore(s: Record<string, unknown>): ScoreRecord {
  const scoreVal = Number(s['score'] || 0)
  const fc = (s['fc'] as string) || ''
  let fullCombo: string | null = null
  if (fc === 'fc') fullCombo = 'fullcombo'
  else if (fc === 'fcp') fullCombo = 'perfect'
  else if (fc === 'ap') fullCombo = 'alljustice'
  else if (fc === 'app') fullCombo = 'alljusticecritical'

  return {
    recordId: Number(s['mid'] || 0),
    songName: (s['title'] as string) || '',
    level: `Lv${s['ds'] || 0}`,
    levelIndex: Number(s['level_index'] || 0),
    score: scoreVal,
    rating: Number(s['ra'] || 0),
    overPower: 0,
    clearStatus: scoreVal > 0 ? 'clear' : 'failed',
    fullCombo,
    fullChain: null,
    rank: calculateRankFromScore(scoreVal),
    uploadTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
    playTime: null,
  }
}

export interface ApiFetchResult {
  player: PlayerInfo
  scores: ScoreRecord[]
}

export async function fetchFromApi(mode: ApiMode, options: {
  lxnsToken?: string
  lxnsDeveloperToken?: string
  lxnsFriendCode?: number
  shuiyuImportToken?: string
  shuiyuDeveloperToken?: string
  shuiyuUsername?: string
  onProgress?: (msg: string) => void
}): Promise<ApiFetchResult> {
  const progress = options.onProgress || (() => {})

  if (mode === 'lxns') {
    if (!options.lxnsToken) throw new Error('落雪个人模式需要个人令牌')
    const headers = { 'X-User-Token': options.lxnsToken }

    progress('正在获取玩家信息...')
    const playerRaw = await fetchJson(`${LXNS_BASE_URL}/user/chunithm/player`, headers) as Record<string, unknown>
    const playerData = (playerRaw['success'] ? playerRaw['data'] : playerRaw) as Record<string, unknown>
    const player = parseLxnsPlayer(playerData)

    progress('正在获取成绩数据...')
    const scoresRaw = await fetchJson(`${LXNS_BASE_URL}/user/chunithm/player/scores`, headers) as Record<string, unknown>
    const scoresData = (scoresRaw['success'] ? scoresRaw['data'] : scoresRaw) as Record<string, unknown>[]
    const scores = scoresData.map(parseLxnsScore)

    progress(`获取到 ${scores.length} 条成绩`)
    return { player, scores }
  }

  if (mode === 'lxns-dev') {
    if (!options.lxnsDeveloperToken) throw new Error('落雪开发者模式需要开发者令牌')
    if (!options.lxnsFriendCode) throw new Error('落雪开发者模式需要好友码')
    const headers = { Authorization: options.lxnsDeveloperToken }
    const fc = options.lxnsFriendCode

    progress('正在获取玩家信息...')
    const playerRaw = await fetchJson(`${LXNS_BASE_URL}/chunithm/player/${fc}`, headers) as Record<string, unknown>
    const playerData = (playerRaw['success'] ? playerRaw['data'] : playerRaw) as Record<string, unknown>
    const player = parseLxnsPlayer(playerData)

    progress('正在获取 Best 成绩...')
    const bestsRaw = await fetchJson(`${LXNS_BASE_URL}/chunithm/player/${fc}/bests`, headers) as Record<string, unknown>
    const bestsData = (bestsRaw['success'] ? bestsRaw['data'] : bestsRaw) as Record<string, unknown>
    const scores: ScoreRecord[] = []
    for (const key of ['bests', 'selections', 'new_bests']) {
      const arr = (bestsData[key] || []) as Record<string, unknown>[]
      scores.push(...arr.map(parseLxnsScore))
    }

    progress('正在获取最近成绩...')
    const recentsRaw = await fetchJson(`${LXNS_BASE_URL}/chunithm/player/${fc}/recents`, headers) as Record<string, unknown>
    const recentsData = (recentsRaw['success'] ? recentsRaw['data'] : recentsRaw) as Record<string, unknown>[]
    scores.push(...recentsData.map(parseLxnsScore))

    progress(`获取到 ${scores.length} 条成绩`)
    return { player, scores }
  }

  if (mode === 'shuiyu') {
    if (!options.shuiyuImportToken) throw new Error('水鱼个人模式需要 Import-Token')
    const headers = { 'Import-Token': options.shuiyuImportToken }

    progress('正在获取玩家成绩...')
    const data = await fetchJson(`${SHUIYU_BASE_URL}/player/records`, headers) as Record<string, unknown>
    const player = parseShuiyuPlayer(data)
    const records = ((data['records'] as Record<string, unknown>)?.['best'] || []) as Record<string, unknown>[]
    const scores = records.map(parseShuiyuScore)

    progress(`获取到 ${scores.length} 条成绩`)
    return { player, scores }
  }

  if (mode === 'shuiyu-dev') {
    if (!options.shuiyuDeveloperToken) throw new Error('水鱼开发者模式需要 Developer-Token')
    if (!options.shuiyuUsername) throw new Error('水鱼开发者模式需要用户名')
    const headers = { 'Developer-Token': options.shuiyuDeveloperToken }

    progress(`正在获取玩家 "${options.shuiyuUsername}" 的成绩...`)
    const data = await fetchJson(
      `${SHUIYU_BASE_URL}/dev/player/records?username=${encodeURIComponent(options.shuiyuUsername)}`,
      headers,
    ) as Record<string, unknown>
    const player = parseShuiyuPlayer(data)
    const records = ((data['records'] as Record<string, unknown>)?.['best'] || []) as Record<string, unknown>[]
    const scores = records.map(parseShuiyuScore)

    progress(`获取到 ${scores.length} 条成绩`)
    return { player, scores }
  }

  throw new Error(`不支持的模式: ${mode}`)
}
