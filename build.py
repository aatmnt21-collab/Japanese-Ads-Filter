from __future__ import annotations
import os
import re

# ---------------------------------------------------------------------------
# 1. 絶対保護ガード（LINE/Yahooのコア機能：ピンポイント指定のみ）
# ---------------------------------------------------------------------------
CRITICAL_WHITELIST = {
    # LINE 通話・重要メディア・決済
    "vos.line-scdn.net",
    "news-obs.line-scdn.net",
    "obs.line-scdn.net",
    "pay.line.me",
    # Yahoo! JAPAN ニュース画像・検索アセット・決済
    "im.c.yimg.jp",
    "s.yimg.jp",
    "news.yahoo.co.jp",
    "paypay.ne.jp",
    "paypay.jp",
}

WHITELIST_PATTERNS = [
    r"^im\.c\.yimg\.jp$",
    r"^news-obs\.line-scdn\.net$",
    r"^vos\.line-scdn\.net$",
    r"^pay\.line\.me$",
    r".*\.paypay\.ne\.jp$",
    r".*\.paypay\.jp$",
]

def is_whitelisted(domain: str) -> bool:
    """100% Zero-Breakage 保証用の安全ガード"""
    domain = domain.lower().strip()
    
    # ピンポイントでの完全一致および指定ドメインのサブドメイン保護
    for parent in CRITICAL_WHITELIST:
        if domain == parent or domain.endswith("." + parent):
            return True
            
    # 正規表現パターンのチェック
    for pattern in WHITELIST_PATTERNS:
        if re.match(pattern, domain):
            return True
            
    return False

# ---------------------------------------------------------------------------
# 2. スコープ判定（LINE / Yahoo! JAPAN エコシステム限定）
# ---------------------------------------------------------------------------
LY_TARGET_KEYWORDS = [
    "line", "yahoo", "yimg", "yj", "paypay", "sentry", "flvcdn", "slim01",
    "facebook", "googletagmanager"
]

def is_ly_ecosystem(domain: str) -> bool:
    """対象サービス以外の不必要な無関係ドメイン混入をブロック"""
    domain = domain.lower().strip()
    return any(kw in domain for kw in LY_TARGET_KEYWORDS)

# ---------------------------------------------------------------------------
# 3. 超強力軽量化アルゴリズム（親ドメインが存在する場合、サブドメインを剪定）
# ---------------------------------------------------------------------------
def prune_subdomains(domains: set[str]) -> set[str]:
    """親ドメイン（例: line-ads.com）が存在する場合、
    サブドメイン（例: sub.line-ads.com）を自動削除して劇的に軽量化する
    """
    sorted_domains = sorted(domains, key=lambda d: (d.count('.'), len(d), d))
    retained_domains = set()

    for domain in sorted_domains:
        parts = domain.split('.')
        is_redundant = False
        for i in range(1, len(parts) - 1):
            parent = '.'.join(parts[i:])
            if parent in retained_domains:
                is_redundant = True
                break
        if not is_redundant:
            retained_domains.add(domain)

    return retained_domains

# ---------------------------------------------------------------------------
# 4. フォーマット自動クレンジング＆高度抽出
# ---------------------------------------------------------------------------
def extract_domain(raw_line: str) -> str | None:
    """AdBlock記法、Hosts形式、URL、箇条書き記号等から純粋なドメイン名だけを全自動抽出"""
    line = raw_line.strip()
    if not line or line.startswith(('!', '#', '//')):
        return None
    
    # 箇条書き記号（- や * 、先頭の記号や空白）およびAdBlock記法のクレンジング
    line = re.sub(r'^[\-\*\•\s]+', '', line)
    line = re.sub(r'^\|\|', '', line)
    line = re.sub(r'[\^$].*$', '', line)
    line = re.sub(r'^(0\.0\.0\.0|127\.0\.0\.1)\s+', '', line)
    line = re.sub(r'^https?://', '', line)
    
    # パス・ポート・クエリ等の除去
    line = line.split('/')[0].split('?')[0].split('#')[0].split(':')[0].rstrip('.').lower()
    
    # 正しいFQDNドメイン形式かチェック
    if re.match(r'^[a-z0-9\-\.]+\.[a-z]{2,}$', line):
        return line
    return None

# ---------------------------------------------------------------------------
# 5. メインビルド処理
# ---------------------------------------------------------------------------
def build_filters():
    print("[1/5] 既存ドメインおよび追加拒否リスト（Denylist）を読み込み中...")
    raw_domains = set()

    source_files = ["filter.txt", "extra_denylist.txt", "denylist.txt", "raw_domains.txt"]
    for file_path in source_files:
        if os.path.exists(file_path):
            print(f"  - 読み込み中: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    dom = extract_domain(line)
                    if dom:
                        raw_domains.add(dom)

    print(f"  -> 検出された全抽出ドメイン数: {len(raw_domains)} 件")

    print("[2/5] セーフティガード＆スコープチェック適用中...")
    valid_domains = set()
    for dom in raw_domains:
        if is_whitelisted(dom):
            print(f"  [安全保護 - ホワイトリスト除外]: {dom}")
            continue
        if not is_ly_ecosystem(dom):
            print(f"  [対象外 - スコープ外除外]: {dom}")
            continue
        valid_domains.add(dom)

    print(f"  -> ガード通過ドメイン数: {len(valid_domains)} 件")

    print("[3/5] サブドメインの自動削ぎ落とし（軽量化）実行中...")
    pruned_domains = prune_subdomains(valid_domains)
    pruned_count = len(valid_domains) - len(pruned_domains)
    print(f"  -> 軽量化成功: {pruned_count} 件の冗長サブドメインをカット (残り {len(pruned_domains)} 件)")

    alive_domains = sorted(list(pruned_domains))

    if not alive_domains:
        print("[ERROR] 採用可能なドメインが0件のため、上書き防止インターロックが作動しました。")
        return

    print("[4/5] マルチフォーマット出力ファイルを自動生成中...")
    
    # 1. filter.txt (メイン AdBlock 形式)
    with open("filter.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("![ Title: Japanese-Ads-Filter ]\n")
        f.write("![ Description: Zero-breakage ad/tracker filter for LINE & Yahoo! JAPAN ]\n")
        f.write("![ Homepage: https://github.com/aatmnt21-collab/Japanese-Ads-Filter ]\n")
        f.write(f"![ Total Domains: {len(alive_domains)} ]\n\n")
        for dom in alive_domains:
            f.write(f"||{dom}^\n")

    # 2. adblock.txt (AdBlock Plus 互換形式)
    with open("adblock.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("[Adblock Plus 2.0]\n")
        f.write("! Title: Japanese-Ads-Filter\n\n")
        for dom in alive_domains:
            f.write(f"||{dom}^\n")

    # 3. hosts.txt (Hosts 形式)
    with open("hosts.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("# Title: Japanese-Ads-Filter (Hosts)\n\n")
        for dom in alive_domains:
            f.write(f"0.0.0.0 {dom}\n")

    print(f"[5/5] ビルド完了！ 合計 {len(alive_domains)} 件の最適化済みドメインを出力しました。")

    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file and os.path.exists(summary_file):
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write("### 🚀 Filter Build Summary\n")
            f.write(f"- **Total Input:** {len(raw_domains)} domains\n")
            f.write(f"- **Pruned (Lightened):** -{pruned_count} subdomains\n")
            f.write(f"- **Final Active Domains:** {len(alive_domains)} domains\n")

if __name__ == "__main__":
    build_filters()
