#!/usr/bin/env python3
"""
WordPress Draft Guard — 防止重复发布的安全检查工具。

用法:
    python3 wp_draft_guard.py                    # 检查所有草稿
    python3 wp_draft_guard.py --slug my-post     # 检查特定 slug
    python3 wp_draft_guard.py --strict           # 严格模式（相似度阈值降低）

环境变量:
    WP_URL        WordPress 站点 URL (如 https://mubibai.com)
    WP_USER       WordPress 用户名
    WP_APP_PASS   WordPress Application Password
"""

import os
import sys
import json
import argparse
import requests
from difflib import SequenceMatcher
from pathlib import Path


def get_wp_posts(url, user, password, status="publish", per_page=100):
    """从 WordPress REST API 获取文章列表。"""
    posts = []
    page = 1
    while True:
        resp = requests.get(
            f"{url}/wp-json/wp/v2/posts",
            params={"status": status, "per_page": per_page, "page": page},
            auth=(user, password),
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"⚠️  WP API error: {resp.status_code}")
            break
        data = resp.json()
        if not data:
            break
        posts.extend(data)
        page += 1
    return posts


def parse_frontmatter(content):
    """解析 Markdown frontmatter。"""
    import yaml

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return fm or {}, body
            except yaml.YAMLError:
                pass
    return {}, content


def similarity(a, b):
    """计算两个字符串的相似度 (0-1)。"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def check_local_drafts(drafts_dir, wp_slugs, wp_titles, threshold=0.7):
    """检查本地草稿是否与已发布文章重复。"""
    drafts_path = Path(drafts_dir)
    if not drafts_path.exists():
        print(f"⚠️  Drafts directory not found: {drafts_dir}")
        return []

    conflicts = []
    for md_file in drafts_path.glob("*.md"):
        if md_file.name.startswith("."):
            continue

        content = md_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(content)

        # 检查 slug
        local_slug = fm.get("slug", md_file.stem)
        if local_slug in wp_slugs:
            conflicts.append({
                "file": md_file.name,
                "type": "exact_slug",
                "match": local_slug,
                "severity": "HIGH",
            })
            continue

        # 检查标题相似度
        local_title = fm.get("title", md_file.stem.replace("-", " "))
        for wp_title in wp_titles:
            sim = similarity(local_title, wp_title)
            if sim >= threshold:
                conflicts.append({
                    "file": md_file.name,
                    "type": "similar_title",
                    "match": f"{wp_title} (similarity: {sim:.0%})",
                    "severity": "MEDIUM" if sim < 0.9 else "HIGH",
                })
                break

    return conflicts


def main():
    parser = argparse.ArgumentParser(description="WordPress Draft Guard")
    parser.add_argument("--slug", help="检查特定 slug")
    parser.add_argument("--strict", action="store_true", help="严格模式")
    parser.add_argument("--drafts-dir", default="drafts", help="草稿目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    # 从环境变量读取配置
    wp_url = os.environ.get("WP_URL", "https://mubibai.com")
    wp_user = os.environ.get("WP_USER", "kai")
    wp_pass = os.environ.get("WP_APP_PASS")

    if not wp_pass:
        print("❌ WP_APP_PASS not set")
        sys.exit(1)

    threshold = 0.5 if args.strict else 0.7

    print("🔍 Fetching published posts...")
    posts = get_wp_posts(wp_url, wp_user, wp_pass)
    wp_slugs = {p["slug"] for p in posts}
    wp_titles = [p["title"]["rendered"] for p in posts]
    print(f"   Found {len(posts)} published posts")

    if args.slug:
        # 检查特定 slug
        if args.slug in wp_slugs:
            print(f"❌ Slug '{args.slug}' already exists!")
            sys.exit(1)
        else:
            print(f"✅ Slug '{args.slug}' is available")
            sys.exit(0)

    print(f"\n🔍 Scanning local drafts in {args.drafts_dir}/...")
    conflicts = check_local_drafts(args.drafts_dir, wp_slugs, wp_titles, threshold)

    if args.json:
        print(json.dumps(conflicts, indent=2))
    elif conflicts:
        print(f"\n⚠️  Found {len(conflicts)} potential conflict(s):\n")
        for c in conflicts:
            icon = "🔴" if c["severity"] == "HIGH" else "🟡"
            print(f"  {icon} [{c['severity']}] {c['file']}")
            print(f"     {c['type']}: {c['match']}")
        sys.exit(1)
    else:
        print("\n✅ No conflicts found. Safe to publish.")
        sys.exit(0)


if __name__ == "__main__":
    main()
