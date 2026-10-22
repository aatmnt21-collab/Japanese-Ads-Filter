#!/usr/bin/env python3
"""
Japanese-Ads-Filter Build Engine
LINE / Yahoo! JAPAN エコシステム専用 広告・トラッカーブロックフィルター自動構築システム
"""

import os
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# 1. 安全保護規約（ホワイトリスト設定）
# ---------------------------------------------------------------------------

# 最重要コア保護ドメイン（ファイル未存在・破損時でもシステム崩壊を防ぐハードコード領域）
BASE_WHITELIST = {
    "vos.line-scdn.net",
    "im.c.yimg.jp",
    "paypay.ne.jp",
    "pay.line.me",
}

# 共有TLD・パブリックサフィックス（誤った親判定・剪定事故を防止するホワイトリスト）
PUBLIC_SUFFIXES = {
    "co.jp", "ne.jp", "or.jp", "go.jp", "ac.jp", "gr.jp",
    "com", "net", "org", "info", "me", "jp", "site", "online",
    "top", "xyz", "tech", "biz", "app", "dev", "io", "store"
}

# LINE & Yahoo! JAPAN エコシステムドメイン（スコープガード判定用キーワード）
LY_ECOSYSTEM_KEYWORDS = (
    "line", "yimg", "yahoo", "yjtag", "line-scdn", "line-apps", "line-corp"
)

# ---------------------------------------------------------------------------
# 2. ユーティリティ関数 & ホワイトリスト読み込み
# ---------------------------------------------------------------------------

def extract_domain(text: str) -> str:
    """各種フォーマット（AdBlock構文、URL、箇条書き記号等）から純粋なドメイン名を正規抽出"""
    if not text:
        return ""
    
    # コメント（#）および前後の余分な空白を除去
    line = text.split("#")[0].strip()
    if not line:
        return ""
    
    # 箇条書き記号（- や * 等）の除去
    line = re.sub(r"^[\s\-*\d\.]+\s*", "", line)
    
    # AdBlock / ABP 構文 (||domain.com^) の除去
    line = re.sub(r"^\|\|", "", line)
    line = re.sub(r"\^.*$", "", line)
    
    # URL スキップ (http:// や https://) の除去
    line = re.sub(r"^https?://", "", line)
    
    # パス・ポート番号の切り捨て
    line = line.split("/")[0].split(":")[0].strip()
    
    # RFC準拠ドメイン正規表現バリデーション
    domain_pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    if re.match(domain_pattern, line):
        return line.lower()
    
    return ""


def load_whitelist() -> set:
    """BASE_WHITELIST と extra_whitelist.txt を動的に統合読み込み"""
    whitelist = set(BASE_WHITELIST)
    whitelist_file = "extra_whitelist.txt"
    
    if os.path.exists(whitelist_file):
        with open(whitelist_file, "r", encoding="utf-8") as f:
            for line in f:
                domain = extract_domain(line)
                if domain:
                    whitelist.add(domain)
                    
    return whitelist


# 動的統合ホワイトリストの生成
CRITICAL_WHITELIST = load_whitelist()


def is_whitelisted(domain: str) -> bool:
    """指定ドメインまたはその親ドメインがホワイトリストに含まれているか判定"""
    domain = domain.lower().strip()
    
    # 直接完全一致
    if domain in CRITICAL_WHITELIST:
        return True
    
    # サブドメイン親マッチ (例: sub.paypay.ne.jp -> paypay.ne.jp)
    parts = domain.split(".")
    for i in range(1, len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in CRITICAL_WHITELIST:
            return True
            
    return False


def is_ly_ecosystem(domain: str) -> bool:
    """LINE / Yahoo! JAPAN エコシステム関連ドメインかスコープ判定"""
    domain = domain.lower().strip()
    return any(keyword in domain for keyword in LY_ECOSYSTEM_KEYWORDS)


def prune_subdomains(domains: set) -> set:
    """共有TLDを保護しながら親ドメインが存在する無駄なサブドメインを自動剪定"""
    sorted_domains = sorted(domains, key=lambda d: len(d.split(".")))
    kept_domains = set()
    
    for domain in sorted_domains:
        parts = domain.split(".")
        should_keep = True
        
        # 親ドメインを順に検証
        for i in range(1, len(parts)):
            parent = ".".join(parts[i:])
            # co.jp 等のパブリックサフィックスは親比較から除外
            if parent in PUBLIC_SUFFIXES:
                continue
            if parent in kept_domains:
                should_keep = False
                break
                
        if should_keep:
            kept_domains.add(domain)
            
    return kept_domains

# ---------------------------------------------------------------------------
# 3. IPv4 / IPv6 デュアルスタック 並列 DNS 死活監視
# ---------------------------------------------------------------------------

def check_dns_single(domain: str, retries: int = 2) -> bool:
    """単一ドメインの DNS 生存確認（AF_UNSPEC により IPv4 / IPv6 両対応）"""
    for attempt in range(retries):
        try:
            res = socket.getaddrinfo(domain, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            if res:
                return True
        except socket.gaierror:
            if attempt < retries - 1:
                time.sleep(0.2 * (attempt + 1))
        except Exception:
            pass
    return False


def filter_live_domains(domains: set) -> set:
    """スレッドプールによるドメイン死活監視の並列実行"""
    live_domains = set()
    max_workers = min(32, (os.cpu_count() or 1) + 4)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_domain = {executor.submit(check_dns_single, domain): domain for domain in domains}
        for future in as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                if future.result():
                    live_domains.add(domain)
            except Exception:
                pass
                
    return live_domains

# ---------------------------------------------------------------------------
# 4. メインビルド処理 & 各フォーマット書き出し
# ---------------------------------------------------------------------------

def build():
    global CRITICAL_WHITELIST
    # ビルド実行時に最新の extra_whitelist.txt を再ロード
    CRITICAL_WHITELIST = load_whitelist()
    
    denylist_file = "extra_denylist.txt"
    raw_domains = set()
    
    if os.path.exists(denylist_file):
        with open(denylist_file, "r", encoding="utf-8") as f:
            for line in f:
                domain = extract_domain(line)
                if domain:
                    raw_domains.add(domain)
                    
    # 1. ホワイトリスト保護 ＆ スコープガード適用
    filtered_domains = set()
    for domain in raw_domains:
        if is_whitelisted(domain):
            print(f"[SKIP / WHITELISTED] {domain}")
            continue
        if not is_ly_ecosystem(domain):
            print(f"[SKIP / OUT OF SCOPE] {domain}")
            continue
        filtered_domains.add(domain)
        
    # 2. TLD考慮型 サブドメイン剪定（最速化・軽量化）
    pruned_domains = prune_subdomains(filtered_domains)
    
    # 3. 死活確認（実体チェック）
    final_domains = sorted(list(filter_live_domains(pruned_domains)))
    
    # --- 共通 LF 改行でファイル生成 ---
    
    # filter.txt (AdGuard / uBlock 用)
    with open("filter.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("! Title: Japanese Ads Filter (LINE & Yahoo! JAPAN)\n")
        f.write("! Homepage: https://github.com/aatmnt21-collab/Japanese-Ads-Filter\n")
        f.write("! License: MIT\n")
        f.write("!\n")
        for d in final_domains:
            f.write(f"||{d}^\n")
            
    # adblock.txt (ABP 互換用)
    with open("adblock.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("[Adblock Plus 2.0]\n")
        f.write("! Title: Japanese Ads Filter (LINE & Yahoo! JAPAN)\n")
        for d in final_domains:
            f.write(f"||{d}^\n")
            
    # hosts.txt (Pi-hole / Hosts 形式用)
    with open("hosts.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("# Japanese Ads Filter (Hosts Format)\n")
        f.write("# https://github.com/aatmnt21-collab/Japanese-Ads-Filter\n")
        for d in final_domains:
            f.write(f"0.0.0.0 {d}\n")
            
    print(f"Build completed successfully. Total active domains: {len(final_domains)}")


if __name__ == "__main__":
    build()
