# Chunithm CSV 到 MuNET JSON 转换工具

## 简介

这个Python脚本可以将 落雪导出格式 的分数数据转换为MuNET可导入的数据文件。

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

# 显示详细输出
python convert_chunithm_scores.py --verbose

# 完整使用
python convert_chunithm_scores.py --input scores.csv --output result.json --username "玩家名称" --verbose
```

### 查看帮助
```bash
python convert_chunithm_scores.py --help
```

## 转换规则

1. **音乐详情去重**: 同一音乐同一难度只保留最高分
2. **游玩次数统计**: 统计每个音乐每个难度的游玩次数
3. **等级转换**:
   - D/C/B → scoreRank 0/1/2
   - A/AA/AAA → scoreRank 3
   - S/SP/SS/SSP → scoreRank 4
   - SSS/SSSP → scoreRank 5
4. **通关状态转换**:
   - "clear" → isSuccess: 1, isClear: true
   - "failed" → isSuccess: 0, isClear: false
5. **时间格式**: 将CSV中的时间转换为ISO 8601格式

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

1. CSV文件必须使用 UTF-8
1. 脚本会自动检测CSV分隔符 (逗号、分号、制表符)
2. 如果play_time字段为空，不会生成对应的游玩记录
3. 脚本会计算总分数并更新到userData中

## 依赖

- Python 3.6+
- 标准库: json, csv, datetime, argparse

## 故障排除

1. **文件不存在**: 检查输入文件路径是否正确
2. **格式错误**: 检查CSV文件格式是否符合要求