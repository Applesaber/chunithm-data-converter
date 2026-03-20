import requests
import json
import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

DEFAULT_API_TOKEN = " "
LXNS_BASE_URL = "https://maimai.lxns.net/api/v0"
SHUIYU_BASE_URL = "https://www.diving-fish.com/api/chunithmprober"

PASSING_CLEAR_STATUSES = {"catastrophy", "absolute", "brave", "hard", "clear"}

SCORE_RANK_MAP = {
    "d": 0,
    "c": 1,
    "b": 2, "bb": 2, "bbb": 2,
    "a": 3, "aa": 3, "aaa": 3,
    "s": 4, "sp": 4, "ss": 4, "ssp": 4,
    "sss": 5, "sssp": 5,
}

RANK_TO_INT = {
    "d": 0, "c": 1,
    "b": 2, "bb": 3, "bbb": 4,
    "a": 5, "aa": 6, "aaa": 7,
    "s": 8, "sp": 9, "ss": 10, "ssp": 11,
    "sss": 12, "sssp": 13,
}

FULL_CHAIN_TO_INT = {
    None: 0,
    "fullchain": 1,
    "fullchain2": 2,
}

def calculate_rank_from_score(score: int) -> str:
    if score >= 1009000:
        return "sssp"
    elif score >= 1007500:
        return "sss"
    elif score >= 1005000:
        return "ssp"
    elif score >= 1000000:
        return "ss"
    elif score >= 990000:
        return "sp"
    elif score >= 975000:
        return "s"
    elif score >= 950000:
        return "aaa"
    elif score >= 925000:
        return "aa"
    elif score >= 900000:
        return "a"
    elif score >= 800000:
        return "bbb"
    elif score >= 700000:
        return "bb"
    elif score >= 600000:
        return "b"
    elif score >= 500000:
        return "c"
    else:
        return "d"

def determine_clear_status_from_score(score: int) -> str:
    if score > 0:
        return "clear"
    else:
        return "failed"

@dataclass
class PlayerInfo:
    name: str
    level: int
    rating: float
    rating_possession: str
    friend_code: int
    class_emblem: Optional[Dict]
    reborn_count: int
    over_power: float
    over_power_progress: float
    currency: int
    total_currency: int
    total_play_count: int
    trophy: Optional[Dict]
    character: Optional[Dict]
    name_plate: Optional[Dict]
    map_icon: Optional[Dict]
    upload_time: str

@dataclass
class ScoreRecord:
    record_id: int
    song_name: str
    level: str
    level_index: int
    score: int
    rating: float
    over_power: float
    clear_status: str
    full_combo: Optional[str]
    full_chain: Optional[str]
    rank: str
    upload_time: str
    play_time: Optional[str]

@dataclass
class SongData:
    song_id: int
    title: str
    artist: str
    genre: str
    bpm: int
    version: int
    difficulties: List[Dict[str, Any]]

class ChunithmAPIClient:

    def __init__(self, api_mode: str,
                 api_token: Optional[str] = None,
                 friend_code: Optional[int] = None,
                 developer_token: Optional[str] = None,
                 import_token: Optional[str] = None,
                 username: Optional[str] = None):
        self.api_token = api_token or DEFAULT_API_TOKEN
        self.api_mode = api_mode
        self.friend_code = friend_code
        self.developer_token = developer_token
        self.import_token = import_token
        self.username = username

        if api_mode == "lxns":
            self.headers = {
                "X-User-Token": self.api_token,
                "Content-Type": "application/json"
            }
            self.base_url = LXNS_BASE_URL
        elif api_mode == "lxns-dev":
            self.headers = {
                "Authorization": self.developer_token,
                "Content-Type": "application/json"
            }
            self.base_url = LXNS_BASE_URL
        elif api_mode == "shuiyu":
            self.headers = {
                "Import-Token": self.import_token,
                "Content-Type": "application/json"
            }
            self.base_url = SHUIYU_BASE_URL
        elif api_mode == "shuiyu-dev":
            self.headers = {
                "Developer-Token": self.developer_token,
                "Content-Type": "application/json"
            }
            self.base_url = SHUIYU_BASE_URL
        else:
            raise ValueError(f"不支持的API模式: {api_mode}")

    def _make_request(self, endpoint: str, use_auth: bool = True, params: Optional[Dict] = None) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        headers = self.headers if use_auth else {"Content-Type": "application/json"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if "success" in data:
                    if data.get("success"):
                        return data.get("data")
                    else:
                        error_code = data.get("code")
                        if error_code == 401:
                            self._print_auth_error("API 401", endpoint)
                        else:
                            print(f"API返回错误: {data.get('message')}")
                        return None
                else:
                    return data
            elif response.status_code == 401:
                self._print_auth_error("HTTP 401", endpoint)
                return None
            elif response.status_code == 429:
                print("请求过于频繁，等待5秒后重试...")
                time.sleep(5)
                return self._make_request(endpoint, use_auth, params)
            else:
                print(f"HTTP错误 {response.status_code}: {response.text[:200]}")

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")

        return None

    def _print_auth_error(self, error_type: str, endpoint: str):
        if self.api_mode == "lxns-dev":
            token_preview = self.developer_token[:10] if self.developer_token else "(无令牌)"
            hint = "lxns-dev 模式需要 --developer-token"
        elif self.api_mode == "shuiyu":
            token_preview = self.import_token[:10] if self.import_token else "(无令牌)"
            hint = "shuiyu 模式需要 --import-token"
        elif self.api_mode == "shuiyu-dev":
            token_preview = self.developer_token[:10] if self.developer_token else "(无令牌)"
            hint = "shuiyu-dev 模式需要 --shuiyu-developer-token"
        else:
            token_preview = self.api_token[:10] if self.api_token and self.api_token.strip() else "(无令牌)"
            hint = "lxns 模式需要 --token"
        print(f"认证失败 ({error_type}): 请检查令牌是否正确，模式是否匹配")
        print(f"  端点: {endpoint}")
        print(f"  模式: {self.api_mode}")
        print(f"  令牌前10位: {token_preview}")
        print(f"  提示: {hint}")

    def _parse_player_data(self, player_data: Dict) -> PlayerInfo:
        return PlayerInfo(
            name=player_data.get("name", ""),
            level=int(player_data.get("level", 0)),
            rating=float(player_data.get("rating", 0)),
            rating_possession=player_data.get("rating_possession", ""),
            friend_code=int(player_data.get("friend_code", 0)),
            class_emblem=player_data.get("class_emblem"),
            reborn_count=int(player_data.get("reborn_count", 0)),
            over_power=float(player_data.get("over_power", 0)),
            over_power_progress=float(player_data.get("over_power_progress", 0)),
            currency=int(player_data.get("currency", 0)),
            total_currency=int(player_data.get("total_currency", 0)),
            total_play_count=int(player_data.get("total_play_count", 0)),
            trophy=player_data.get("trophy"),
            character=player_data.get("character"),
            name_plate=player_data.get("name_plate"),
            map_icon=player_data.get("map_icon"),
            upload_time=player_data.get("upload_time", ""),
        )

    def _parse_score_data(self, score: Dict) -> ScoreRecord:
        return ScoreRecord(
            record_id=int(score.get("id", 0)),
            song_name=score.get("song_name", ""),
            level=score.get("level", ""),
            level_index=int(score.get("level_index", 0)),
            score=int(score.get("score", 0)),
            rating=float(score.get("rating", 0)),
            over_power=float(score.get("over_power", 0)),
            clear_status=score.get("clear", ""),
            full_combo=score.get("full_combo"),
            full_chain=score.get("full_chain"),
            rank=score.get("rank", ""),
            upload_time=score.get("upload_time", ""),
            play_time=score.get("play_time"),
        )

    def _parse_shuiyu_player_data(self, player_data: Dict) -> PlayerInfo:
        nickname = player_data.get("nickname", "")
        rating = player_data.get("rating", 0)
        
        return PlayerInfo(
            name=nickname,
            level=0,
            rating=float(rating),
            rating_possession="",
            friend_code=0,
            class_emblem=None,
            reborn_count=0,
            over_power=0.0,
            over_power_progress=0.0,
            currency=0,
            total_currency=0,
            total_play_count=0,
            trophy=None,
            character=None,
            name_plate=None,
            map_icon=None,
            upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _parse_shuiyu_score_data(self, score: Dict) -> ScoreRecord:
        mid = score.get("mid", 0)
        title = score.get("title", "")
        score_value = score.get("score", 0)
        fc = score.get("fc", "")
        level_index = score.get("level_index", 0)
        ds = score.get("ds", 0.0)
        ra = score.get("ra", 0.0)
        
        rank = calculate_rank_from_score(score_value)
        clear_status = determine_clear_status_from_score(score_value)
        
        full_combo = None
        if fc == "fc":
            full_combo = "fullcombo"
        elif fc == "fcp":
            full_combo = "perfect"
        elif fc == "ap":
            full_combo = "alljustice"
        elif fc == "app":
            full_combo = "alljusticecritical"
        
        return ScoreRecord(
            record_id=int(mid),
            song_name=title,
            level=f"Lv{ds}",
            level_index=int(level_index),
            score=int(score_value),
            rating=float(ra),
            over_power=0.0,
            clear_status=clear_status,
            full_combo=full_combo,
            full_chain=None,
            rank=rank,
            upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            play_time=None,
        )

    def fetch_player_info(self) -> Optional[PlayerInfo]:
        print("从API获取玩家信息...")
        player_data = self._make_request("/user/chunithm/player", use_auth=True)
        if not player_data:
            return None
        return self._parse_player_data(player_data)

    def fetch_player_scores(self) -> List[ScoreRecord]:
        print("从API获取玩家成绩...")
        scores_data = self._make_request("/user/chunithm/player/scores", use_auth=True)
        if not scores_data:
            return []
        print(f"获取到 {len(scores_data)} 条成绩记录")
        return [self._parse_score_data(s) for s in scores_data]

    def fetch_player_info_by_friend_code(self, friend_code: int) -> Optional[PlayerInfo]:
        endpoint = f"/chunithm/player/{friend_code}"
        player_data = self._make_request(endpoint, use_auth=True)
        if not player_data:
            return None
        return self._parse_player_data(player_data)

    def fetch_player_bests(self, friend_code: int) -> Optional[Dict[str, List[ScoreRecord]]]:
        endpoint = f"/chunithm/player/{friend_code}/bests"
        data = self._make_request(endpoint, use_auth=True)
        if not data:
            return None
        result = {}
        for key in ("bests", "selections", "new_bests"):
            result[key] = [self._parse_score_data(s) for s in data.get(key, [])]
        return result

    def fetch_player_recents(self, friend_code: int) -> List[ScoreRecord]:
        endpoint = f"/chunithm/player/{friend_code}/recents"
        data = self._make_request(endpoint, use_auth=True)
        if not data:
            return []
        return [self._parse_score_data(s) for s in data]

    def fetch_all_songs(self) -> List[SongData]:
        if self.api_mode in ["lxns", "lxns-dev"]:
            print("从落雪API获取曲目列表...")
            songs_data = self._make_request("/chunithm/song/list", use_auth=False, params={"notes": True})
            if not songs_data:
                return []

            songs = songs_data.get("songs", [])
            print(f"获取到 {len(songs)} 首曲目")

            song_objects = []
            for song in songs:
                song_data = SongData(
                    song_id=song.get("id"),
                    title=song.get("title"),
                    artist=song.get("artist", ""),
                    genre=song.get("genre", ""),
                    bpm=song.get("bpm", 0),
                    version=song.get("version", 0),
                    difficulties=song.get("difficulties", [])
                )
                song_objects.append(song_data)

            return song_objects
        else:
            # 水鱼模式
            return self.fetch_shuiyu_all_songs()

    def fetch_shuiyu_player_records(self) -> Optional[Dict]:
        print("从水鱼API获取玩家成绩...")
        data = self._make_request("/player/records", use_auth=True)
        if not data:
            return None
        return data

    def fetch_shuiyu_player_records_by_username(self, username: str) -> Optional[Dict]:
        print(f"从水鱼API获取玩家 '{username}' 的成绩...")
        data = self._make_request(f"/dev/player/records?username={username}", use_auth=True)
        if not data:
            return None
        return data

    def fetch_shuiyu_all_songs(self) -> List[SongData]:
        print("从水鱼API获取曲目列表...")
        songs_data = self._make_request("/music_data", use_auth=False)
        if not songs_data:
            return []

        songs = songs_data if isinstance(songs_data, list) else songs_data.get("music_data", [])
        print(f"获取到 {len(songs)} 首曲目")

        song_objects = []
        for song in songs:
            song_data = SongData(
                song_id=song.get("id"),
                title=song.get("title"),
                artist=song.get("artist", ""),
                genre=song.get("genre", ""),
                bpm=song.get("bpm", 0),
                version=song.get("version", 0),
                difficulties=song.get("difficulties", [])
            )
            song_objects.append(song_data)

        return song_objects

class MuNETConverter:

    def __init__(self, api_client: ChunithmAPIClient):
        self.api_client = api_client

    def convert_to_munet_format(self, player_info: PlayerInfo, scores: List[ScoreRecord]) -> Dict:
        print("开始转换为MuNET格式...")

        all_songs = self.api_client.fetch_all_songs()
        song_map = {song.song_id: song for song in all_songs}

        total_hi_score = sum(s.score for s in scores)
        player_rating = int(player_info.rating * 100)

        user_data = {
            "userName": player_info.name,
            "level": player_info.level,
            "reincarnationNum": player_info.reborn_count,
            "exp": "0",
            "point": player_info.currency,
            "totalPoint": player_info.total_currency,
            "playCount": player_info.total_play_count,
            "multiPlayCount": 0,
            "playerRating": player_rating,
            "highestRating": player_rating,
            "nameplateId": player_info.name_plate.get("id", 0) if player_info.name_plate else 0,
            "frameId": 0,
            "characterId": player_info.character.get("id", 0) if player_info.character else 0,
            "trophyId": player_info.trophy.get("id", 0) if player_info.trophy else 0,
            "playedTutorialBit": 0,
            "firstTutorialCancelNum": 0,
            "masterTutorialCancelNum": 0,
            "totalMapNum": 0,
            "totalHiScore": total_hi_score,
            "totalBasicHighScore": 0,
            "totalAdvancedHighScore": 0,
            "totalExpertHighScore": 0,
            "totalMasterHighScore": 0,
            "totalUltimaHighScore": 0,
            "eventWatchedDate": "1970-01-01T09:00:00",
            "friendCount": 0,
            "firstGameId": "SDHD",
            "firstRomVersion": "",
            "firstDataVersion": "",
            "firstPlayDate": "",
            "lastGameId": "SDHD",
            "lastRomVersion": "",
            "lastDataVersion": "",
            "lastPlayDate": player_info.upload_time,
            "lastPlaceId": 0,
            "lastPlaceName": "",
            "lastRegionId": "0",
            "lastRegionName": "",
            "lastAllNetId": "0",
            "lastCountryCode": "",
            "userNameEx": "",
            "compatibleCmVersion": "",
            "medal": player_info.class_emblem.get("medal", 0) if player_info.class_emblem else 0,
            "mapIconId": player_info.map_icon.get("id", 0) if player_info.map_icon else 0,
            "voiceId": 0,
            "avatarWear": 0,
            "avatarHead": 0,
            "avatarFace": 0,
            "avatarSkin": 0,
            "avatarItem": 0,
            "avatarFront": 0,
            "avatarBack": 0,
            "classEmblemBase": player_info.class_emblem.get("base", 0) if player_info.class_emblem else 0,
            "classEmblemMedal": player_info.class_emblem.get("medal", 0) if player_info.class_emblem else 0,
            "stockedGridCount": 0,
            "exMapLoopCount": 0,
            "netBattlePlayCount": 0,
            "netBattleWinCount": 0,
            "netBattleLoseCount": 0,
            "netBattleConsecutiveWinCount": 0,
            "charaIllustId": 0,
            "skillId": 0,
            "stageId": 0,
            "overPowerPoint": int(player_info.over_power * 100),
            "overPowerRate": int(player_info.over_power_progress * 100),
            "overPowerLowerRank": 0,
            "avatarPoint": 0,
            "battleRankId": 0,
            "battleRankPoint": 0,
            "eliteRankPoint": 0,
            "netBattle1stCount": 0,
            "netBattle2ndCount": 0,
            "netBattle3rdCount": 0,
            "netBattle4thCount": 0,
            "netBattleCorrection": 0,
            "netBattleErrCnt": 0,
            "netBattleHostErrCnt": 0,
            "battleRewardStatus": 0,
            "battleRewardIndex": 0,
            "battleRewardCount": 0,
            "ext1": 0, "ext2": 0, "ext3": 0, "ext4": 0, "ext5": 0,
            "ext6": 0, "ext7": 0, "ext8": 0, "ext9": 0, "ext10": 0,
            "extStr1": "", "extStr2": "",
            "extLong1": 0, "extLong2": 0,
            "rankUpChallengeResults": None,
            "netBattleEndState": 0,
            "trophyIdSub1": 0,
            "trophyIdSub2": 0,
            "banState": 0,
            "totalScore": total_hi_score,
            "accessCode": "0",
            "isNetBattleHost": False,
        }

        user_game_option = {
            "bgInfo": 0,
            "fieldColor": 0,
            "guideSound": 0,
            "soundEffect": 0,
            "guideLine": 0,
            "speed": 0,
            "optionSet": 0,
            "matching": 0,
            "judgePos": 0,
            "rating": 0,
            "judgeCritical": 0,
            "judgeJustice": 0,
            "judgeAttack": 0,
            "headphone": 0,
            "playerLevel": 0,
            "successTap": 0,
            "successExTap": 0,
            "successSlideHold": 0,
            "successAir": 0,
            "successFlick": 0,
            "successSkill": 0,
            "successTapTimbre": 0,
            "privacy": 0,
            "mirrorFumen": 0,
            "selectMusicFilterLv": 0,
            "sortMusicFilterLv": 0,
            "sortMusicGenre": 0,
            "categoryDetail": 0,
            "judgeTimingOffset": 0,
            "playTimingOffset": 0,
            "fieldWallPosition": 0,
            "resultVoiceShort": 0,
            "notesThickness": 0,
            "judgeAppendSe": 0,
            "trackSkip": 0,
            "hardJudge": 0,
            "speed_120": 0,
            "fieldWallPosition_120": 0,
            "playTimingOffset_120": 0,
            "judgeTimingOffset_120": 0,
            "ext1": 0, "ext2": 0, "ext3": 0, "ext4": 0, "ext5": 0,
            "ext6": 0, "ext7": 0, "ext8": 0, "ext9": 0, "ext10": 0,
        }

        best_scores: Dict[Tuple[int, int], ScoreRecord] = {}
        for score in scores:
            key = (score.record_id, score.level_index)
            existing = best_scores.get(key)
            if existing is None or score.score > existing.score:
                best_scores[key] = score

        user_music_detail_list = []
        for (song_id, level_index), score in best_scores.items():
            is_fc = score.full_combo is not None
            is_aj = score.full_combo in ("alljustice", "alljusticecritical")
            is_success = 1 if score.clear_status in PASSING_CLEAR_STATUSES else 0
            score_rank = SCORE_RANK_MAP.get(score.rank, 0)

            detail = {
                "musicId": song_id,
                "level": level_index,
                "playCount": 1,
                "scoreMax": score.score,
                "missCount": 0,
                "maxComboCount": 0,
                "fullChain": FULL_CHAIN_TO_INT.get(score.full_chain, 0),
                "maxChain": 0,
                "scoreRank": score_rank,
                "theoryCount": 0,
                "ext1": 0,
                "isFullCombo": is_fc,
                "isAllJustice": is_aj,
                "isSuccess": is_success,
                "isLock": False,
            }
            user_music_detail_list.append(detail)

        user_playlog_list = []
        for score in scores:
            if not score.play_time:
                continue
            song_info = song_map.get(score.record_id)

            playlog = {
                "romVersion": "",
                "orderId": 0,
                "sortNumber": 0,
                "placeId": 0,
                "playDate": score.play_time,
                "userPlayDate": score.play_time,
                "musicId": score.record_id,
                "level": score.level_index,
                "customId": 0,
                "playedUserId1": 0, "playedUserId2": 0, "playedUserId3": 0,
                "playedUserName1": "", "playedUserName2": "", "playedUserName3": "",
                "playedMusicLevel1": 0, "playedMusicLevel2": 0, "playedMusicLevel3": 0,
                "playedCustom1": 0, "playedCustom2": 0, "playedCustom3": 0,
                "track": 1,
                "score": score.score,
                "rank": RANK_TO_INT.get(score.rank, 0),
                "maxCombo": 0,
                "maxChain": 0,
                "rateTap": 0, "rateHold": 0, "rateSlide": 0, "rateAir": 0, "rateFlick": 0,
                "judgeGuilty": 0, "judgeAttack": 0, "judgeJustice": 0, "judgeCritical": 0, "judgeHeaven": 0,
                "eventId": 0,
                "playerRating": player_rating,
                "fullChainKind": FULL_CHAIN_TO_INT.get(score.full_chain, 0),
                "characterId": player_info.character.get("id", 0) if player_info.character else 0,
                "charaIllustId": player_info.character.get("id", 0) if player_info.character else 0,
                "skillId": 0,
                "playKind": 0,
                "skillLevel": 0,
                "skillEffect": 0,
                "placeName": "",
                "commonId": 0,
                "regionId": 0,
                "machineType": 0,
                "ticketId": 0,
                "afterRating": player_rating,
                "beforeRating": player_rating,
                "isAllPerfect": score.full_combo == "alljusticecritical",
                "achievement": score.score,
                "isNewRecord": False,
                "isFullCombo": score.full_combo is not None,
                "isAllJustice": score.full_combo in ("alljustice", "alljusticecritical"),
                "isContinue": False,
                "isFreeToPlay": False,
                "isClear": score.clear_status in PASSING_CLEAR_STATUSES,
            }
            user_playlog_list.append(playlog)

        if (i_count := len(scores)) > 0:
            print(f"  转换进度: {i_count}/{i_count}")

        munet_data = {
            "gameId": "SDHD",
            "userData": user_data,
            "userGameOption": user_game_option,
            "userActivityList": [],
            "userCharacterList": [],
            "userChargeList": [],
            "userCourseList": [],
            "userDuelList": [],
            "userItemList": [],
            "userMapList": [],
            "userMusicDetailList": user_music_detail_list,
            "userPlaylogList": user_playlog_list,
        }

        print(f"转换完成: {len(user_music_detail_list)} 条音乐详情, {len(user_playlog_list)} 条游玩记录")
        return munet_data

    def save_to_file(self, munet_data: Dict, output_path: str):
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(munet_data, f, ensure_ascii=False, indent=2)

        print(f"已保存到: {output_path}")

        detail_list = munet_data.get("userMusicDetailList", [])
        playlog_list = munet_data.get("userPlaylogList", [])
        fc_count = sum(1 for d in detail_list if d.get("isFullCombo"))
        aj_count = sum(1 for d in detail_list if d.get("isAllJustice"))
        clear_count = sum(1 for d in detail_list if d.get("isSuccess"))

        print(f"\n统计信息:")
        print(f"  音乐详情数: {len(detail_list)}")
        print(f"  游玩记录数: {len(playlog_list)}")
        print(f"  通关数: {clear_count}")
        print(f"  FC数: {fc_count}")
        print(f"  AJ数: {aj_count}")

def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

def run_api_converter(args):
    # 参数验证
    if args.mode == "lxns-dev":
        if not args.lxns_friend_code:
            print("错误: lxns-dev 模式需要 --lxns-friend-code")
            sys.exit(1)
        if not args.lxns_developer_token:
            print("错误: lxns-dev 模式需要 --lxns-developer-token (或设置环境变量 LXNS_DEVELOPER_TOKEN)")
            sys.exit(1)
    elif args.mode == "lxns":
        if not args.lxns_token:
            print("错误: lxns 模式需要 --lxns-token")
            sys.exit(1)
    elif args.mode == "shuiyu":
        if not args.shuiyu_import_token:
            print("错误: shuiyu 模式需要 --shuiyu-import-token")
            sys.exit(1)
    elif args.mode == "shuiyu-dev":
        if not args.shuiyu_developer_token:
            print("错误: shuiyu-dev 模式需要 --shuiyu-developer-token (或设置环境变量 SHUIYU_DEVELOPER_TOKEN)")
            sys.exit(1)
        if not args.shuiyu_username:
            print("错误: shuiyu-dev 模式需要 --shuiyu-username")
            sys.exit(1)

    print("=" * 60)
    print("Chunithm API Converter - 落雪/水鱼API转MuNET格式工具")
    print(f"模式: {args.mode}")
    print("=" * 60)

    try:
        print(f"\n初始化API客户端...")
        dev_token = args.shuiyu_developer_token if args.mode == "shuiyu-dev" else args.lxns_developer_token
        api_client = ChunithmAPIClient(
            api_token=args.lxns_token,
            api_mode=args.mode,
            friend_code=args.lxns_friend_code,
            developer_token=dev_token,
            import_token=args.shuiyu_import_token,
            username=args.shuiyu_username,
        )

        print(f"\n获取玩家信息...")
        player_info = None
        scores = []
        
        if args.mode in ["lxns", "lxns-dev"]:
            if args.mode == "lxns-dev":
                player_info = api_client.fetch_player_info_by_friend_code(args.lxns_friend_code)
            else:
                player_info = api_client.fetch_player_info()

            if not player_info:
                print("错误: 无法获取玩家信息")
                sys.exit(1)

            print(f"玩家: {player_info.name}")
            print(f"好友码: {player_info.friend_code}")
            print(f"Rating: {player_info.rating}")
            print(f"等级: {player_info.level}")
            print(f"OVER POWER: {player_info.over_power}")
            print(f"总游玩次数: {player_info.total_play_count}")

            print(f"\n获取玩家成绩...")
            if args.mode == "lxns-dev":
                bests = api_client.fetch_player_bests(args.lxns_friend_code)
                if bests:
                    scores.extend(bests.get("bests", []))
                    scores.extend(bests.get("selections", []))
                    scores.extend(bests.get("new_bests", []))
                recents = api_client.fetch_player_recents(args.lxns_friend_code)
                scores.extend(recents)
            else:
                scores = api_client.fetch_player_scores()
                
        elif args.mode in ["shuiyu", "shuiyu-dev"]:
            if args.mode == "shuiyu":
                print("水鱼Import-Token模式: 获取玩家成绩...")
                data = api_client.fetch_shuiyu_player_records()
            else:
                print(f"水鱼Developer-Token模式: 获取玩家 '{args.shuiyu_username}' 的成绩...")
                data = api_client.fetch_shuiyu_player_records_by_username(args.shuiyu_username)

            if not data:
                print("错误: 无法获取水鱼API数据")
                sys.exit(1)

            player_info = api_client._parse_shuiyu_player_data(data)
            records = data.get("records", {}).get("best", [])
            scores = [api_client._parse_shuiyu_score_data(record) for record in records]

            print(f"玩家: {player_info.name}")
            print(f"Rating: {player_info.rating}")
            print(f"获取到 {len(scores)} 条成绩记录")

        if not player_info:
            print("错误: 无法获取玩家信息")
            sys.exit(1)
            
        if not scores:
            print("错误: 无法获取玩家成绩")
            sys.exit(1)

        print(f"获取到 {len(scores)} 条成绩记录")

        if args.test:
            print(f"测试模式: 只处理前10条成绩")
            scores = scores[:10]

        print(f"\n获取歌曲信息...")
        songs = api_client.fetch_all_songs()
        print(f"获取到 {len(songs)} 首歌曲信息")

        print(f"\n开始数据转换...")
        converter = MuNETConverter(api_client)
        munet_data = converter.convert_to_munet_format(player_info, scores)

        print(f"\n保存结果...")
        converter.save_to_file(munet_data, args.output)

        print(f"\n转换完成!")
        print(f"输出文件: {args.output}")

    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
