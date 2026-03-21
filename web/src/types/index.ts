export interface PlayerInfo {
  name: string
  level: number
  rating: number
  ratingPossession: string
  friendCode: number
  rebornCount: number
  overPower: number
  overPowerProgress: number
  currency: number
  totalCurrency: number
  totalPlayCount: number
  trophy: Record<string, unknown> | null
  character: Record<string, unknown> | null
  namePlate: Record<string, unknown> | null
  mapIcon: Record<string, unknown> | null
  classEmblem: Record<string, unknown> | null
  uploadTime: string
}

export interface ScoreRecord {
  recordId: number
  songName: string
  level: string
  levelIndex: number
  score: number
  rating: number
  overPower: number
  clearStatus: string
  fullCombo: string | null
  fullChain: string | null
  rank: string
  uploadTime: string
  playTime: string | null
}

export interface MunetJson {
  gameId: string
  userData: Record<string, unknown>
  userGameOption: Record<string, unknown>
  userActivityList: unknown[]
  userCharacterList: unknown[]
  userItemList: unknown[]
  userMapList: unknown[]
  userMusicDetailList: MusicDetail[]
  userCourseList: unknown[]
  userChargeList: unknown[]
  userPlaylogList: Playlog[]
  userDuelList?: unknown[]
}

export interface MusicDetail {
  musicId: number
  level: number
  playCount: number
  scoreMax: number
  missCount: number
  maxComboCount: number
  fullChain: number
  maxChain: number
  scoreRank: number
  theoryCount: number
  ext1: number
  isFullCombo: boolean
  isAllJustice: boolean
  isSuccess: number
  isLock: boolean
}

export interface Playlog {
  musicId: number
  level: number
  score: number
  rank: number
  playDate: string
  userPlayDate: string
  isFullCombo: boolean
  isAllJustice: boolean
  isClear: boolean
  playerRating: number
  [key: string]: unknown
}

export type ApiMode = 'lxns' | 'lxns-dev' | 'shuiyu-import' | 'shuiyu-dev'
export type CsvFormat = 'auto' | 'lxns' | 'shuiyu'
