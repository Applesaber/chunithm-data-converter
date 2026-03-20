import json
import csv
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

from chunithm_api_converter import calculate_rank_from_score

def detect_csv_format(csv_path: str) -> str:
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # 读取前几行来检测格式
            lines = []
            for _ in range(5):
                line = f.readline()
                if not line:
                    break
                lines.append(line.strip())
            
            if not lines:
                return "unknown"
            
            # 检查列名来确定格式
            header = lines[0].lower()
            
            # 检查是否是"水鱼"格式
            if '排名' in header or '乐曲名' in header or '难度' in header:
                return "shuiyu"
            
            # 检查是否是"落雪"格式
            elif 'id' in header or 'song_name' in header or 'level_index' in header:
                return "lxns"
            
            # 默认格式
            else:
                return "unknown"
                
    except Exception as e:
        print(f"检测CSV格式时出错: {e}")
        return "unknown"

def read_csv_file(csv_path: str, format_type: str = "auto") -> List[Dict[str, Any]]:
    
    # 自动检测格式
    if format_type == "auto":
        format_type = detect_csv_format(csv_path)
        print(f"检测到CSV格式: {format_type}")
    
    if format_type == "shuiyu":
        return read_shuiyu_csv(csv_path)
    elif format_type == "lxns":
        return read_lxns_csv(csv_path)
    else:
        print(f"错误: 不支持的CSV格式: {format_type}")
        print("请使用 --format 参数指定格式: shuiyu 或 lxns")
        sys.exit(1)

def read_lxns_csv(csv_path: str) -> List[Dict[str, Any]]:
    scores = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # 尝试检测分隔符
            sample = f.read(1024)
            f.seek(0)
            
            # 检查分隔符
            if ',' in sample:
                delimiter = ','
            elif ';' in sample:
                delimiter = ';'
            elif '\t' in sample:
                delimiter = '\t'
            else:
                delimiter = ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # 转换数据类型
                    score_data = {
                        'id': int(row['id']),
                        'song_name': row['song_name'],
                        'level': row['level'],
                        'level_index': int(row['level_index']),
                        'score': int(row['score']),
                        'rating': float(row['rating']),
                        'over_power': float(row['over_power']),
                        'clear': row['clear'],
                        'full_combo': row.get('full_combo', ''),
                        'full_chain': row.get('full_chain', ''),
                        'rank': row['rank'],
                        'upload_time': row['upload_time'],
                        'play_time': row.get('play_time', '')
                    }
                    scores.append(score_data)
                except (KeyError, ValueError) as e:
                    print(f"警告: 第{row_num}行数据解析错误: {e}")
                    continue
        
        print(f"成功读取 {len(scores)} 条落雪格式分数记录")
        return scores
        
    except Exception as e:
        print(f"读取落雪格式CSV文件时发生错误: {str(e)}")
        sys.exit(1)

def read_shuiyu_csv(csv_path: str) -> List[Dict[str, Any]]:
    scores = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # 水鱼格式使用逗号分隔
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # 解析难度字符串，提取级别和难度索引
                    level_str = str(row['难度']).strip()
                    
                    # 处理难度级别
                    level = level_str
                    
                    # 将难度转换为level_index
                    # 水鱼格式的难度需要映射到level_index
                    # 基本规则: 数字 -> BASIC/ADVANCED, 数字+ -> EXPERT/MASTER
                    level_index = 0  # 默认BASIC
                    
                    if '+' in level_str:
                        # 有+的通常是EXPERT或MASTER
                        base_level = level_str.replace('+', '')
                        try:
                            level_num = float(base_level)
                            if level_num >= 10:
                                level_index = 3  # MASTER
                            else:
                                level_index = 2  # EXPERT
                        except:
                            level_index = 2  # EXPERT
                    else:
                        # 没有+的通常是BASIC或ADVANCED
                        try:
                            level_num = float(level_str)
                            if level_num >= 7:
                                level_index = 1  # ADVANCED
                            else:
                                level_index = 0  # BASIC
                        except:
                            level_index = 0  # BASIC
                    
                    # 根据分数计算rank
                    score = int(row['分数'])
                    rank = calculate_rank_from_score(score)
                    
                    # 根据分数判断是否clear (假设分数>0就是clear)
                    clear_status = "clear" if score > 0 else "failed"
                    
                    # 转换数据类型
                    score_data = {
                        'id': row_num,  # 水鱼格式没有id，使用行号
                        'song_name': row['乐曲名'],
                        'level': level_str,
                        'level_index': level_index,
                        'score': score,
                        'rating': float(row['Rating']),
                        'over_power': 0.0,  # 水鱼格式没有over_power
                        'clear': clear_status,
                        'full_combo': '',  # 水鱼格式没有full_combo信息
                        'full_chain': '',  # 水鱼格式没有full_chain信息
                        'rank': rank,
                        'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'play_time': ''  # 水鱼格式没有play_time
                    }
                    scores.append(score_data)
                except (KeyError, ValueError) as e:
                    print(f"警告: 第{row_num}行数据解析错误: {e}")
                    print(f"行数据: {row}")
                    continue
        
        print(f"成功读取 {len(scores)} 条水鱼格式分数记录")
        return scores
        
    except Exception as e:
        print(f"读取水鱼格式CSV文件时发生错误: {str(e)}")
        sys.exit(1)

def convert_rank_to_score_rank(rank: str) -> int:
    rank = str(rank).lower().strip()
    
    rank_mapping = {
        'd': 0,
        'c': 1,
        'b': 2, 'bb': 2, 'bbb': 2,
        'a': 3, 'aa': 3, 'aaa': 3,
        's': 4, 'sp': 4, 'ss': 4, 'ssp': 4,
        'sss': 5, 'sssp': 5
    }
    
    return rank_mapping.get(rank, 2)

def convert_clear_status(clear: str) -> int:
    clear = str(clear).lower().strip()
    
    if clear == 'clear':
        return 1
    elif clear == 'failed':
        return 0
    else:
        return 0

def create_munet_json_template(username: str = "Player") -> Dict[str, Any]:
    
    return {
        "gameId": "SDHD",
        "userData": {
            "userName": username,
            "level": 0,
            "reincarnationNum": 0,
            "exp": "0",
            "point": 0,
            "totalPoint": 0,
            "playCount": 0,
            "multiPlayCount": 0,
            "playerRating": 0,
            "highestRating": 0,
            "nameplateId": 0,
            "frameId": 0,
            "characterId": 0,
            "trophyId": 0,
            "playedTutorialBit": 0,
            "firstTutorialCancelNum": 0,
            "masterTutorialCancelNum": 0,
            "totalMapNum": 0,
            "totalHiScore": 0,
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
            "lastPlayDate": "",
            "lastPlaceId": 0,
            "lastPlaceName": "",
            "lastRegionId": "0",
            "lastRegionName": "",
            "lastAllNetId": "0",
            "lastCountryCode": "",
            "userNameEx": "",
            "compatibleCmVersion": "",
            "medal": 0,
            "mapIconId": 0,
            "voiceId": 0,
            "avatarWear": 0,
            "avatarHead": 0,
            "avatarFace": 0,
            "avatarSkin": 0,
            "avatarItem": 0,
            "avatarFront": 0,
            "avatarBack": 0,
            "trophyIdSub1": 0,
            "trophyIdSub2": 0,
            "banState": 0,
            "totalScore": 0,
            "accessCode": "0",
            "isNetBattleHost": False
        },
        "userGameOption": {
            "bgInfo": 0, "fieldColor": 0, "guideSound": 0, "soundEffect": 0,
            "guideLine": 0, "speed": 0, "optionSet": 0, "matching": 0,
            "judgePos": 0, "rating": 0, "judgeCritical": 0, "judgeJustice": 0,
            "judgeAttack": 0, "headphone": 0, "playerLevel": 0,
            "successTap": 0, "successExTap": 0, "successSlideHold": 0,
            "successAir": 0, "successFlick": 0, "successSkill": 0,
            "successTapTimbre": 0, "privacy": 0, "mirrorFumen": 0,
            "selectMusicFilterLv": 0, "sortMusicFilterLv": 0, "sortMusicGenre": 0,
            "categoryDetail": 0, "judgeTimingOffset": 0, "playTimingOffset": 0,
            "fieldWallPosition": 0, "resultVoiceShort": 0, "notesThickness": 0,
            "judgeAppendSe": 0, "trackSkip": 0, "hardJudge": 0,
            "speed_120": 0, "fieldWallPosition_120": 0,
            "playTimingOffset_120": 0, "judgeTimingOffset_120": 0,
            "ext1": 0, "ext2": 0, "ext3": 0, "ext4": 0, "ext5": 0,
            "ext6": 0, "ext7": 0, "ext8": 0, "ext9": 0, "ext10": 0,
        },
        "userActivityList": [],
        "userCharacterList": [],
        "userItemList": [],
        "userMapList": [],
        "userMusicDetailList": [],
        "userCourseList": [],
        "userChargeList": [],
        "userPlaylogList": []
    }

def convert_csv_to_munet(csv_scores: List[Dict[str, Any]], username: str = "Player") -> Dict[str, Any]:
    """将CSV分数转换为MuNET格式"""
    munet_data = create_munet_json_template(username)
    
    # 转换userMusicDetailList
    user_music_details = []
    music_detail_map = {}  # 用于去重 (musicId, level) -> 最高分
    
    for score in csv_scores:
        music_id = score['id']
        level_index = score['level_index']
        
        # MuNET中level从1开始: 1=BASIC, 2=ADVANCED, 3=EXPERT, 4=MASTER, 5=ULTIMA
        level = level_index + 1
        
        key = (music_id, level)
        
        # 如果已经有这个音乐和难度的记录，保留最高分
        if key in music_detail_map:
            existing_score = music_detail_map[key]
            if score['score'] > existing_score['scoreMax']:
                music_detail_map[key] = {
                    'musicId': music_id,
                    'level': level,
                    'playCount': existing_score['playCount'] + 1,
                    'scoreMax': score['score'],
                    'rank': score['rank'],
                    'clear': score['clear'],
                    'full_combo': score['full_combo']
                }
            else:
                music_detail_map[key]['playCount'] += 1
        else:
            music_detail_map[key] = {
                'musicId': music_id,
                'level': level,
                'playCount': 1,
                'scoreMax': score['score'],
                'rank': score['rank'],
                'clear': score['clear'],
                'full_combo': score['full_combo']
            }
    
    # 转换为MuNET格式
    for key, data in music_detail_map.items():
        music_detail = {
            "musicId": data['musicId'],
            "level": data['level'],
            "playCount": data['playCount'],
            "scoreMax": data['scoreMax'],
            "missCount": 0,
            "maxComboCount": 0,
            "fullChain": 0,
            "maxChain": 0,
            "scoreRank": convert_rank_to_score_rank(data['rank']),
            "theoryCount": 0,
            "ext1": 0,
            "isFullCombo": data['full_combo'] == 'fullcombo',
            "isAllJustice": False,
            "isSuccess": convert_clear_status(data['clear']),
            "isLock": False
        }
        user_music_details.append(music_detail)
    
    munet_data['userMusicDetailList'] = user_music_details
    
    # 转换userPlaylogList
    user_playlogs = []
    
    for i, score in enumerate(csv_scores):
        if not score.get('play_time'):
            continue
            
        try:
            # 解析play_time
            play_time_str = score['play_time'].strip()
            if not play_time_str:
                continue
                
            # 处理不同的时间格式
            if ' ' in play_time_str:
                date_part, time_part = play_time_str.split(' ', 1)
                # 确保时间部分有完整的时分秒
                time_parts = time_part.split(':')
                if len(time_parts) == 2:
                    time_part = f"{time_part}:00"
                play_date = f"{date_part}T{time_part}"
            else:
                play_date = f"{play_time_str}T00:00:00"
        except Exception as e:
            print(f"警告: 解析play_time '{score.get('play_time')}' 时出错: {e}")
            continue
        
        # 生成sortNumber (时间戳)
        try:
            dt = datetime.strptime(play_date, "%Y-%m-%dT%H:%M:%S")
            sort_number = int(dt.timestamp())
        except:
            sort_number = 1700000000 + i
        
        playlog = {
            "romVersion": "",
            "orderId": i,
            "sortNumber": sort_number,
            "placeId": 0,
            "playDate": play_date.split('T')[0] + "T00:00:00",
            "userPlayDate": play_date,
            "musicId": score['id'],
            "level": score['level_index'] + 1,
            "customId": 0,
            "playedUserId1": 0,
            "playedUserId2": 0,
            "playedUserId3": 0,
            "playedUserName1": "",
            "playedUserName2": "",
            "playedUserName3": "",
            "playedMusicLevel1": 0,
            "playedMusicLevel2": 0,
            "playedMusicLevel3": 0,
            "playedCustom1": 0,
            "playedCustom2": 0,
            "playedCustom3": 0,
            "track": 1,
            "score": score['score'],
            "rank": convert_rank_to_score_rank(score['rank']),
            "maxCombo": 0,
            "maxChain": 0,
            "rateTap": 0,
            "rateHold": 0,
            "rateSlide": 0,
            "rateAir": 0,
            "rateFlick": 0,
            "judgeGuilty": 0,
            "judgeAttack": 0,
            "judgeJustice": 0,
            "judgeCritical": 0,
            "judgeHeaven": 0,
            "eventId": 0,
            "playerRating": 0,
            "fullChainKind": 0,
            "characterId": 0,
            "charaIllustId": 0,
            "skillId": 0,
            "playKind": 0,
            "skillLevel": 0,
            "skillEffect": 0,
            "placeName": "",
            "commonId": 0,
            "regionId": 0,
            "machineType": 0,
            "ticketId": 0,
            "afterRating": 0,
            "beforeRating": 0,
            "isAllPerfect": False,
            "achievement": score['score'],
            "isNewRecord": True,
            "isFullCombo": score['full_combo'] == 'fullcombo',
            "isAllJustice": False,
            "isContinue": False,
            "isFreeToPlay": False,
            "isClear": score['clear'] == 'clear'
        }
        user_playlogs.append(playlog)
    
    munet_data['userPlaylogList'] = user_playlogs
    
    # 计算总分数
    total_score = sum(score['score'] for score in csv_scores)
    munet_data['userData']['totalScore'] = total_score
    munet_data['userData']['totalHiScore'] = total_score
    
    return munet_data

def save_json_file(data: Dict[str, Any], output_path: str):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"成功保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存JSON文件时发生错误: {str(e)}")
        return False

def run_csv_converter(args):
    print("=" * 60)
    print("Chunithm CSV 到 MuNET JSON 转换工具")
    print("=" * 60)

    # 设置输出文件路径
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        output_path = f"MuNET Chunithm Export - {args.username} - {timestamp}.json"

    print(f"输入文件: {args.input}")
    print(f"输出文件: {output_path}")
    print(f"用户名: {args.username}")
    print(f"格式: {args.format}")
    print("-" * 60)

    try:
        # 读取CSV数据
        csv_scores = read_csv_file(args.input, args.format)

        if not csv_scores:
            print("错误: 没有读取到有效的分数数据")
            sys.exit(1)

        # 转换为MuNET格式
        print("正在转换为MuNET格式...")
        munet_data = convert_csv_to_munet(csv_scores, args.username)

        # 保存为JSON文件
        if save_json_file(munet_data, output_path):
            print("-" * 60)
            print("转换完成!")
            print(f"生成的JSON文件: {output_path}")
            print(f"文件大小: {os.path.getsize(output_path):,} 字节")
            print(f"包含 {len(munet_data['userMusicDetailList'])} 条音乐详情记录")
            print(f"包含 {len(munet_data['userPlaylogList'])} 条游玩记录")
            print(f"总分数: {munet_data['userData']['totalScore']:,}")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        sys.exit(1)