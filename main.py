import sys
import os
import argparse
from chunithm_api_converter import run_api_converter, _load_env
from convert_chunithm_scores import run_csv_converter


def setup_encoding():
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    setup_encoding()
    _load_env()

    parser = argparse.ArgumentParser(
        description="Chunithm to MuNET 转换工具",
        epilog=("子命令帮助:\n"
                "  python main.py api --help\n"
                "  python main.py csv --help"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    api_parser = subparsers.add_parser("api",
        help="从落雪/水鱼 API 获取数据并转换",
        description="Chunithm API Converter - 落雪/水鱼 API 转 MuNET 格式工具",
        epilog=("模式速查:\n"
                "  lxns       落雪个人模式   --lxns-token\n"
                "  lxns-dev   落雪开发者模式 --lxns-developer-token + --lxns-friend-code\n"
                "  shuiyu       水鱼个人模式   --shuiyu-import-token\n"
                "  shuiyu-dev   水鱼开发者模式 --shuiyu-developer-token + --shuiyu-username"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    api_parser.add_argument("--mode", "-m",
                            choices=["lxns", "lxns-dev", "shuiyu", "shuiyu-dev"],
                            required=True,
                            help="数据来源模式。lxns/lxns-dev 使用落雪 API，shuiyu/shuiyu-dev 使用水鱼 API")
    api_parser.add_argument("--output", "-o", default="chunithm_munet_export.json",
                            help="输出 JSON 文件路径 (默认: chunithm_munet_export.json)")
    api_parser.add_argument("--test", action="store_true",
                            help="测试模式，只处理前 10 条成绩")

    lxns = api_parser.add_argument_group("落雪 API (maimai.lxns.net)")
    lxns.add_argument("--lxns-token", default=None,
                      metavar="TOKEN",
                      help="个人令牌，lxns 模式必填")
    lxns.add_argument("--lxns-developer-token",
                      default=os.environ.get("LXNS_DEVELOPER_TOKEN"),
                      metavar="TOKEN",
                      help="开发者令牌，lxns-dev 模式必填 (也可设置环境变量 LXNS_DEVELOPER_TOKEN)")
    lxns.add_argument("--lxns-friend-code", type=int, default=None,
                      metavar="CODE",
                      help="好友码，lxns-dev 模式必填")

    shuiyu = api_parser.add_argument_group("水鱼 API (diving-fish.com)")
    shuiyu.add_argument("--shuiyu-import-token", default=None,
                        metavar="TOKEN",
                        help="Import-Token，shuiyu 模式必填")
    shuiyu.add_argument("--shuiyu-developer-token",
                        default=os.environ.get("SHUIYU_DEVELOPER_TOKEN"),
                        metavar="TOKEN",
                        help="Developer-Token，shuiyu-dev 模式必填 (也可设置环境变量 SHUIYU_DEVELOPER_TOKEN)")
    shuiyu.add_argument("--shuiyu-username", default=None,
                        metavar="USERNAME",
                        help="查询目标用户名，shuiyu-dev 模式必填")

    csv_parser = subparsers.add_parser("csv",
        help="从本地 CSV 文件转换",
        description="Chunithm CSV 转 MuNET JSON 转换工具",
    )
    csv_parser.add_argument("--input", "-i", default="chunithm-scores.csv",
                            help="输入 CSV 文件路径 (默认: chunithm-scores.csv)")
    csv_parser.add_argument("--output", "-o", default=None,
                            help="输出 JSON 文件路径 (默认: 自动生成)")
    csv_parser.add_argument("--username", "-u", default="Player",
                            help="用户名 (默认: Player)")
    csv_parser.add_argument("--format", "-f", default="auto",
                            choices=["auto", "lxns", "shuiyu"],
                            help="CSV 格式: auto(自动检测), lxns(落雪), shuiyu(水鱼) (默认: auto)")

    args = parser.parse_args()

    if args.command == "api":
        run_api_converter(args)
    elif args.command == "csv":
        run_csv_converter(args)


if __name__ == "__main__":
    main()
