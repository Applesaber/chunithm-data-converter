import type { PlayerInfo, ScoreRecord, MunetJson, MusicDetail, Playlog } from '../types'

const PASSING_CLEAR_STATUSES = new Set(['catastrophy', 'absolute', 'brave', 'hard', 'clear'])

const SCORE_RANK_MAP: Record<string, number> = {
  d: 0, c: 1,
  b: 2, bb: 2, bbb: 2,
  a: 3, aa: 3, aaa: 3,
  s: 4, sp: 4, ss: 4, ssp: 4,
  sss: 5, sssp: 5,
}

const RANK_TO_INT: Record<string, number> = {
  d: 0, c: 1,
  b: 2, bb: 3, bbb: 4,
  a: 5, aa: 6, aaa: 7,
  s: 8, sp: 9, ss: 10, ssp: 11,
  sss: 12, sssp: 13,
}

const FULL_CHAIN_TO_INT: Record<string, number> = {
  '': 0,
  fullchain: 1,
  fullchain2: 2,
}

export function calculateRankFromScore(score: number): string {
  if (score >= 1009000) return 'sssp'
  if (score >= 1007500) return 'sss'
  if (score >= 1005000) return 'ssp'
  if (score >= 1000000) return 'ss'
  if (score >= 990000) return 'sp'
  if (score >= 975000) return 's'
  if (score >= 950000) return 'aaa'
  if (score >= 925000) return 'aa'
  if (score >= 900000) return 'a'
  if (score >= 800000) return 'bbb'
  if (score >= 700000) return 'bb'
  if (score >= 600000) return 'b'
  if (score >= 500000) return 'c'
  return 'd'
}

function convertRankToScoreRank(rank: string): number {
  return SCORE_RANK_MAP[rank.toLowerCase().trim()] ?? 2
}

function createMunetTemplate(username: string): MunetJson {
  return {
    gameId: 'SDHD',
    userData: {
      userName: username,
      level: 0,
      reincarnationNum: 0,
      exp: '0',
      point: 0,
      totalPoint: 0,
      playCount: 0,
      multiPlayCount: 0,
      playerRating: 0,
      highestRating: 0,
      nameplateId: 0,
      frameId: 0,
      characterId: 0,
      trophyId: 0,
      playedTutorialBit: 0,
      firstTutorialCancelNum: 0,
      masterTutorialCancelNum: 0,
      totalMapNum: 0,
      totalHiScore: 0,
      totalBasicHighScore: 0,
      totalAdvancedHighScore: 0,
      totalExpertHighScore: 0,
      totalMasterHighScore: 0,
      totalUltimaHighScore: 0,
      eventWatchedDate: '1970-01-01T09:00:00',
      friendCount: 0,
      firstGameId: 'SDHD',
      firstRomVersion: '',
      firstDataVersion: '',
      firstPlayDate: '',
      lastGameId: 'SDHD',
      lastRomVersion: '',
      lastDataVersion: '',
      lastPlayDate: '',
      lastPlaceId: 0,
      lastPlaceName: '',
      lastRegionId: '0',
      lastRegionName: '',
      lastAllNetId: '0',
      lastCountryCode: '',
      userNameEx: '',
      compatibleCmVersion: '',
      medal: 0,
      mapIconId: 0,
      voiceId: 0,
      avatarWear: 0,
      avatarHead: 0,
      avatarFace: 0,
      avatarSkin: 0,
      avatarItem: 0,
      avatarFront: 0,
      avatarBack: 0,
      classEmblemBase: 0,
      classEmblemMedal: 0,
      stockedGridCount: 0,
      exMapLoopCount: 0,
      netBattlePlayCount: 0,
      netBattleWinCount: 0,
      netBattleLoseCount: 0,
      netBattleConsecutiveWinCount: 0,
      charaIllustId: 0,
      skillId: 0,
      stageId: 0,
      overPowerPoint: 0,
      overPowerRate: 0,
      overPowerLowerRank: 0,
      avatarPoint: 0,
      battleRankId: 0,
      battleRankPoint: 0,
      eliteRankPoint: 0,
      netBattle1stCount: 0,
      netBattle2ndCount: 0,
      netBattle3rdCount: 0,
      netBattle4thCount: 0,
      netBattleCorrection: 0,
      netBattleErrCnt: 0,
      netBattleHostErrCnt: 0,
      battleRewardStatus: 0,
      battleRewardIndex: 0,
      battleRewardCount: 0,
      ext1: 0, ext2: 0, ext3: 0, ext4: 0, ext5: 0,
      ext6: 0, ext7: 0, ext8: 0, ext9: 0, ext10: 0,
      extStr1: '', extStr2: '',
      extLong1: 0, extLong2: 0,
      rankUpChallengeResults: null,
      netBattleEndState: 0,
      trophyIdSub1: 0,
      trophyIdSub2: 0,
      banState: 0,
      totalScore: 0,
      accessCode: '0',
      isNetBattleHost: false,
    },
    userGameOption: {
      bgInfo: 0, fieldColor: 0, guideSound: 0, soundEffect: 0,
      guideLine: 0, speed: 0, optionSet: 0, matching: 0,
      judgePos: 0, rating: 0, judgeCritical: 0, judgeJustice: 0,
      judgeAttack: 0, headphone: 0, playerLevel: 0,
      successTap: 0, successExTap: 0, successSlideHold: 0,
      successAir: 0, successFlick: 0, successSkill: 0,
      successTapTimbre: 0, privacy: 0, mirrorFumen: 0,
      selectMusicFilterLv: 0, sortMusicFilterLv: 0, sortMusicGenre: 0,
      categoryDetail: 0, judgeTimingOffset: 0, playTimingOffset: 0,
      fieldWallPosition: 0, resultVoiceShort: 0, notesThickness: 0,
      judgeAppendSe: 0, trackSkip: 0, hardJudge: 0,
      speed_120: 0, fieldWallPosition_120: 0,
      playTimingOffset_120: 0, judgeTimingOffset_120: 0,
      ext1: 0, ext2: 0, ext3: 0, ext4: 0, ext5: 0,
      ext6: 0, ext7: 0, ext8: 0, ext9: 0, ext10: 0,
    },
    userActivityList: [],
    userCharacterList: [],
    userChargeList: [],
    userCourseList: [],
    userDuelList: [],
    userItemList: [],
    userMapList: [],
    userMusicDetailList: [],
    userPlaylogList: [],
  }
}

export function convertScoresToMunet(
  scores: ScoreRecord[],
  playerInfo: PlayerInfo | null,
  username?: string,
): MunetJson {
  const name = playerInfo?.name ?? username ?? 'Player'
  const munet = createMunetTemplate(name)

  if (playerInfo) {
    const playerRating = Math.round(playerInfo.rating * 100)
    const totalHiScore = scores.reduce((sum, s) => sum + s.score, 0)
    Object.assign(munet.userData, {
      userName: playerInfo.name,
      level: playerInfo.level,
      reincarnationNum: playerInfo.rebornCount,
      point: playerInfo.currency,
      totalPoint: playerInfo.totalCurrency,
      playCount: playerInfo.totalPlayCount,
      playerRating,
      highestRating: playerRating,
      nameplateId: playerInfo.namePlate?.['id'] ?? 0,
      characterId: playerInfo.character?.['id'] ?? 0,
      trophyId: playerInfo.trophy?.['id'] ?? 0,
      totalHiScore,
      totalScore: totalHiScore,
      lastPlayDate: playerInfo.uploadTime,
      classEmblemBase: playerInfo.classEmblem?.['base'] ?? 0,
      classEmblemMedal: playerInfo.classEmblem?.['medal'] ?? 0,
      medal: playerInfo.classEmblem?.['medal'] ?? 0,
      mapIconId: playerInfo.mapIcon?.['id'] ?? 0,
      charaIllustId: playerInfo.character?.['id'] ?? 0,
      overPowerPoint: Math.round(playerInfo.overPower * 100),
      overPowerRate: Math.round(playerInfo.overPowerProgress * 100),
    })
  }

  const bestScores = new Map<string, ScoreRecord>()
  for (const score of scores) {
    const key = `${score.recordId}_${score.levelIndex}`
    const existing = bestScores.get(key)
    if (!existing || score.score > existing.score) {
      bestScores.set(key, score)
    }
  }

  const musicDetails: MusicDetail[] = []
  for (const score of bestScores.values()) {
    const isFc = score.fullCombo !== null && score.fullCombo !== ''
    const isAj = score.fullCombo === 'alljustice' || score.fullCombo === 'alljusticecritical'
    const isSuccess = PASSING_CLEAR_STATUSES.has(score.clearStatus) ? 1 : 0

    musicDetails.push({
      musicId: score.recordId,
      level: score.levelIndex,
      playCount: 1,
      scoreMax: score.score,
      missCount: 0,
      maxComboCount: 0,
      fullChain: FULL_CHAIN_TO_INT[score.fullChain ?? ''] ?? 0,
      maxChain: 0,
      scoreRank: convertRankToScoreRank(score.rank),
      theoryCount: 0,
      ext1: 0,
      isFullCombo: isFc,
      isAllJustice: isAj,
      isSuccess: isSuccess,
      isLock: false,
    })
  }
  munet.userMusicDetailList = musicDetails

  const playerRating = playerInfo ? Math.round(playerInfo.rating * 100) : 0
  const playlogs: Playlog[] = []
  for (let i = 0; i < scores.length; i++) {
    const score = scores[i]
    if (!score.playTime) continue

    let playDate = score.playTime
    if (playDate.includes(' ')) {
      const [datePart, timePart] = playDate.split(' ', 2)
      const parts = timePart.split(':')
      const fullTime = parts.length === 2 ? `${timePart}:00` : timePart
      playDate = `${datePart}T${fullTime}`
    } else {
      playDate = `${playDate}T00:00:00`
    }

    playlogs.push({
      romVersion: '',
      orderId: i,
      sortNumber: 0,
      placeId: 0,
      playDate: playDate.split('T')[0] + 'T00:00:00',
      userPlayDate: playDate,
      musicId: score.recordId,
      level: score.levelIndex,
      customId: 0,
      playedUserId1: 0, playedUserId2: 0, playedUserId3: 0,
      playedUserName1: '', playedUserName2: '', playedUserName3: '',
      playedMusicLevel1: 0, playedMusicLevel2: 0, playedMusicLevel3: 0,
      playedCustom1: 0, playedCustom2: 0, playedCustom3: 0,
      track: 1,
      score: score.score,
      rank: RANK_TO_INT[score.rank.toLowerCase()] ?? 0,
      maxCombo: 0,
      maxChain: 0,
      rateTap: 0, rateHold: 0, rateSlide: 0, rateAir: 0, rateFlick: 0,
      judgeGuilty: 0, judgeAttack: 0, judgeJustice: 0, judgeCritical: 0, judgeHeaven: 0,
      eventId: 0,
      playerRating,
      fullChainKind: FULL_CHAIN_TO_INT[score.fullChain ?? ''] ?? 0,
      characterId: playerInfo?.character?.['id'] ?? 0,
      charaIllustId: playerInfo?.character?.['id'] ?? 0,
      skillId: 0, playKind: 0, skillLevel: 0, skillEffect: 0,
      placeName: '', commonId: 0, regionId: 0, machineType: 0, ticketId: 0,
      afterRating: playerRating, beforeRating: playerRating,
      isAllPerfect: score.fullCombo === 'alljusticecritical',
      achievement: score.score,
      isNewRecord: false,
      isFullCombo: score.fullCombo !== null && score.fullCombo !== '',
      isAllJustice: score.fullCombo === 'alljustice' || score.fullCombo === 'alljusticecritical',
      isContinue: false,
      isFreeToPlay: false,
      isClear: PASSING_CLEAR_STATUSES.has(score.clearStatus),
    })
  }
  munet.userPlaylogList = playlogs

  const totalScore = scores.reduce((sum, s) => sum + s.score, 0)
  munet.userData['totalScore'] = totalScore
  munet.userData['totalHiScore'] = totalScore

  return munet
}
