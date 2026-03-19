# Chunithm CSV 到 MuNET JSON 转换工具

## 简介

这个Python脚本可以将 *水鱼* *落雪* 的Chunithm CSV数据数据转换为MuNET可导入的JSON文件。

### 支持的格式

1. [落雪](https://maimai.lxns.net/)
2. [水鱼](https://maimai.diving-fish.com/)
## 使用方法

### 基本用法
```bash
python convert_chunithm_scores.py
```

### 带参数用法
```bash
# 指定输入文件
python convert_chunithm_scores.py --input my_scores.csv

# 指定输出文件
python convert_chunithm_scores.py --output output.json

# 指定用户名
python convert_chunithm_scores.py --username "玩家名称"

# 指定CSV格式 (auto/luoxue/shuiyu)
python convert_chunithm_scores.py --format shuiyu

# 显示详细输出
python convert_chunithm_scores.py --verbose

# 完整使用 - 水鱼格式
python convert_chunithm_scores.py --input 水鱼.csv --format shuiyu --username "水鱼玩家" --verbose

# 完整使用 - 落雪格式
python convert_chunithm_scores.py --input chunithm-scores.csv --format luoxue --username "落雪玩家" --verbose
```

### 查看帮助
```bash
python convert_chunithm_scores.py --help
```

## 转换规则

### 通用规则
1. **音乐详情去重**: 同一音乐同一难度只保留最高分
2. **游玩次数统计**: 统计每个音乐每个难度的游玩次数
3. **等级转换**:
   - D/C/B → scoreRank 0/1/2
   - A/AA/AAA → scoreRank 3
   - S/SP/SS/SSP → scoreRank 4
   - SSS/SSSP → scoreRank 5
4. **时间格式**: 将CSV中的时间转换为ISO 8601格式

### 落雪格式特有
1. **通关状态**: 直接使用CSV中的clear字段
2. **Full Combo**: 直接使用CSV中的full_combo字段
3. **游玩记录**: 包含完整的游玩记录

### 水鱼格式特有
1. **通关状态**: 根据分数自动判断 (分数>0 = clear)
2. **等级计算**: 根据分数自动计算rank等级
3. **难度映射**: 自动将难度字符串映射到level_index （不准确，之后要同步曲库完善）
   - 数字 (如5, 7) → BASIC/ADVANCED
   - 数字+ (如8+, 12+) → EXPERT/MASTER
4. **游玩记录**: 不生成游玩记录 (缺少时间信息)

## 输出文件结构

生成的JSON文件包含以下主要部分:

1. `userData`: 用户基本信息
2. `userGameOption`: 游戏设置
3. `userMusicDetailList`: 音乐详情列表
4. `userPlaylogList`: 游玩记录列表 (所有记录)

## 示例

```bash
# 转换默认的chunithm-scores.csv文件
python convert_chunithm_scores.py

# 转换后生成的文件
# MuNET Chunithm Export - Apple - YYYY-MM-DD HH-MM-SS.json
```

## 注意事项

### 通用注意事项
1. CSV文件必须使用 UTF-8 编码
2. 脚本会自动检测CSV分隔符 (逗号、分号、制表符)
3. 脚本会计算总分数并更新到userData中

### 落雪格式注意事项
1. 如果play_time字段为空，不会生成对应的游玩记录
2. 需要完整的字段信息才能生成完整的MuNET数据

### 水鱼格式注意事项
1. 不包含游玩时间信息，因此不会生成游玩记录
2. 不包含音乐ID，会自动使用行号作为musicId
3. 不包含clear状态，会根据分数自动判断
4. 不包含rank等级，会根据分数自动计算
5. 难度级别需要正确映射到level_index

## 依赖

- Python 3.6+
- 标准库: json, csv, datetime, argparse

## 故障排除

1. **文件不存在**: 检查输入文件路径是否正确
2. **格式错误**: 检查CSV文件格式是否符合要求