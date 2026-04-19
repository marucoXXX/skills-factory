"""
save_image.py — Base64エンコードされた画像データをファイルに保存するヘルパースクリプト

web_fetchツールで取得した画像のBase64データを受け取り、
ローカルファイルとして保存する。

使い方:
  python save_image.py --base64 "<base64文字列>" --output {{WORK_DIR}}/hq_photo.jpg
  python save_image.py --base64-file {{WORK_DIR}}/img_b64.txt --output {{WORK_DIR}}/hq_photo.jpg
"""

import argparse
import base64
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Base64画像データをファイルに保存")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--base64", help="Base64エンコード文字列（直接指定）")
    group.add_argument("--base64-file", help="Base64エンコード文字列が保存されたファイルパス")
    parser.add_argument("--output", required=True, help="出力画像ファイルパス")
    args = parser.parse_args()

    # Base64データの取得
    if args.base64:
        b64_data = args.base64
    else:
        with open(args.base64_file, "r") as f:
            b64_data = f.read().strip()

    # data:image/xxx;base64, プレフィックスがある場合は除去
    if "," in b64_data and b64_data.startswith("data:"):
        b64_data = b64_data.split(",", 1)[1]

    # デコードして保存
    try:
        img_bytes = base64.b64decode(b64_data)
    except Exception as e:
        print(f"  ✗ Base64デコードエラー: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "wb") as f:
        f.write(img_bytes)

    print(f"  ✓ Image saved: {args.output} ({len(img_bytes)} bytes)")


if __name__ == "__main__":
    main()
