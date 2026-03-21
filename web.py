import os
import json
from flask import Flask, request, jsonify, send_from_directory
from chunithm_api_converter import (
    ChunithmAPIClient, MuNETConverter, _load_env,
    calculate_rank_from_score, determine_clear_status_from_score,
)
from convert_chunithm_scores import convert_csv_to_munet
from datetime import datetime

_load_env()

app = Flask(__name__, static_folder="web/dist", static_url_path="")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    mode = data.get("mode")
    if not mode:
        return jsonify({"error": "缺少 mode 参数"}), 400

    try:
        player_info, scores = fetch_scores(mode, data)
        converter = MuNETConverter(create_client(mode, data))
        munet_data = converter.convert_to_munet_format(player_info, scores)
        return jsonify(munet_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"转换失败: {str(e)}"}), 500


@app.route("/api/convert/csv", methods=["POST"])
def convert_csv():
    if "file" not in request.files:
        return jsonify({"error": "缺少 CSV 文件"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "只支持 CSV 文件"}), 400

    username = request.form.get("username", "Player")
    fmt = request.form.get("format", "auto")

    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as tmp:
            file.save(tmp)
            tmp_path = tmp.name

        class FakeArgs:
            input = tmp_path
            output = None
            username = "Player"
            format = "auto"

        args = FakeArgs()
        args.username = username
        args.format = fmt

        munet_data = convert_csv_to_munet(args)
        os.unlink(tmp_path)
        return jsonify(munet_data)
    except Exception as e:
        return jsonify({"error": f"CSV 转换失败: {str(e)}"}), 500


def create_client(mode, data):
    lxns_token = data.get("lxnsToken")
    lxns_dev_token = data.get("lxnsDeveloperToken") or os.environ.get("LXNS_DEVELOPER_TOKEN")
    shuiyu_import_token = data.get("shuiyuImportToken")
    shuiyu_dev_token = data.get("shuiyuDeveloperToken") or os.environ.get("SHUIYU_DEVELOPER_TOKEN")
    friend_code = data.get("lxnsFriendCode")
    username = data.get("shuiyuUsername")

    if friend_code is not None:
        friend_code = int(friend_code)

    return ChunithmAPIClient(
        api_mode=mode,
        api_token=lxns_token,
        developer_token=lxns_dev_token if mode.startswith("lxns") else shuiyu_dev_token,
        import_token=shuiyu_import_token,
        friend_code=friend_code,
        username=username,
    )


def fetch_scores(mode, data):
    client = create_client(mode, data)

    if mode == "lxns":
        player = client.fetch_player_info()
        if not player:
            raise ValueError("无法获取玩家信息")
        scores = client.fetch_player_scores()
        return player, scores

    elif mode == "lxns-dev":
        fc = data.get("lxnsFriendCode")
        if not fc:
            raise ValueError("缺少好友码")
        fc = int(fc)
        player = client.fetch_player_info_by_friend_code(fc)
        if not player:
            raise ValueError("无法获取玩家信息")
        bests = client.fetch_player_bests(fc)
        scores = []
        if bests:
            scores.extend(bests.get("bests", []))
            scores.extend(bests.get("selections", []))
            scores.extend(bests.get("new_bests", []))
        recents = client.fetch_player_recents(fc)
        scores.extend(recents)
        return player, scores

    elif mode == "shuiyu":
        result = client.fetch_shuiyu_player_records()
        if not result:
            raise ValueError("无法获取水鱼数据")
        player = client._parse_shuiyu_player_data(result)
        records = result.get("records", {}).get("best", [])
        scores = [client._parse_shuiyu_score_data(r) for r in records]
        return player, scores

    elif mode == "shuiyu-dev":
        username = data.get("shuiyuUsername")
        if not username:
            raise ValueError("缺少用户名")
        result = client.fetch_shuiyu_player_records_by_username(username)
        if not result:
            raise ValueError("无法获取水鱼数据")
        player = client._parse_shuiyu_player_data(result)
        records = result.get("records", {}).get("best", [])
        scores = [client._parse_shuiyu_score_data(r) for r in records]
        return player, scores

    else:
        raise ValueError(f"不支持的模式: {mode}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Chunithm Data Converter Web Server")
    print(f"http://localhost:{port}")
    print(f"API: POST /api/convert  POST /api/convert/csv")
    app.run(host="0.0.0.0", port=port, debug=False)
