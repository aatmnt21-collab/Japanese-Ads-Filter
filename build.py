import os
import re
import socket
from urllib.parse import urlparse

# 絶対にブロックしてはならないLINE/Google/決済のコアホワイトリスト
WHITELIST = {
    # Google & Android System
    "play.googleapis.com",
    "connectivitycheck.gstatic.com",
    "android.clients.google.com",
    "clients4.google.com",
    "inputtools.google.com",
    "googleapis.com",
    "gstatic.com",
    "google.com",
    "gvt1.com",
    
    # LINE Core Functions (Messaging, Calls, Auth, Images)
    "legy-jp.line-apps.com",
    "vos.line-scdn.net",
    "a.line.me",
    "profile.line-scdn.net",
    "wcc-image.line-scdn.net",
    "ch.line-scdn.net",
    "d.line-scdn.net",
    "obs.line-apps.com",
    "obs-jp.line-apps.com",
    
    # Payments & Utilities
    "paypay.ne.jp",
    "linepay.line.me",
}

# LINEヤフーエコシステムに関連する許可ドメインパターン
LY_ALLOWED_PATTERNS = [
    "line", "line-scdn", "line-apps", "line-ads", "flvcdn", "slim01",
    "yahoo", "yimg", "yjtag", "sentry", "facebook", "googletagmanager"
]

def clean_domain(raw_entry):
    """URLのコピペミスや不要な記号、パス等を削ぎ落として純粋なドメイン名を取り出す"""
    raw_entry = raw_entry.strip().lower()
    
    if not raw_entry.startswith(('http://', 'https://')):
        parsed = urlparse('http://' + raw_entry)
    else:
        parsed = urlparse(raw_entry)
    
    domain = parsed.netloc or parsed.path
    domain = domain.split(':')[0].split('/')[0]
    domain = re.sub(r'^[\|*.]+', '', domain)
    domain = re.sub(r'[\^/*]+$', '', domain)
    
    return domain.strip()

def is_domain_alive(domain):
    """DNS解決を実行し、使われていない/存在しないドメイン（Dead Domain）を除外する"""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        print(f"[DEAD DOMAIN REMOVED] DNS resolution failed: {domain}")
        return False

def is_whitelisted(domain):
    for safe in WHITELIST:
        if domain == safe or domain.endswith("." + safe):
            return True
    return False

def is_ly_ecosystem(domain):
    return any(pattern in domain for pattern in LY_ALLOWED_PATTERNS)

def clean_and_build():
    if not os.path.exists("filter.txt"):
        return

    domains = set()
    with open("filter.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            
            # 1. URL整形・超強力クレンジング（コピペ誤入力救済）
            domain = clean_domain(line)
            if not domain:
                continue

            # 2. 安全装置（ホワイトリスト）チェック
            if is_whitelisted(domain):
                print(f"[SECURITY GUARD] Protected domain removed: {domain}")
                continue
            
            # 3. LINEヤフー系限定ガード
            if not is_ly_ecosystem(domain):
                print(f"[SCOPE GUARD] Non-LY Ecosystem domain removed: {domain}")
                continue
            
            # 4. デッドドメイン（現在使われていないドメイン）チェック
            if not is_domain_alive(domain):
                continue

            # 全通過したドメインを追加（setにより自動重複排除）
            domains.add(domain)

    sorted_domains = sorted(list(domains))

    header = (
        "! Title: Japanese-Ads-Filter (OISD Specification)\n"
        "! Description: Absolute safety & zero-breakage ad filtering ONLY for LINE & Yahoo! JAPAN ecosystem.\n"
        "! Homepage: https://github.com/aatmnt21-collab/Japanese-Ads-Filter\n"
        "! Syntax: AdBlock / NextDNS / AdGuard Compatible\n\n"
    )

    # 1. Wildcard / NextDNS (filter.txt)
    with open("filter.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join(sorted_domains) + "\n")

    # 2. AdBlock / Brave (adblock.txt)
    with open("adblock.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join([f"||{d}^" for d in sorted_domains]) + "\n")

    # 3. Hosts (hosts.txt)
    with open("hosts.txt", "w", encoding="utf-8") as f:
        f.write("# Japanese-Ads-Filter (Hosts Format)\n" + "\n".join([f"0.0.0.0 {d}" for d in sorted_domains]) + "\n")

    print(f"[SUCCESS] Built {len(sorted_domains)} active unique domains successfully.")

if __name__ == "__main__":
    clean_and_build()
