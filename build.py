import os
import re
import socket
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# 絶対にブロックしてはならないLINE/Google/決済/ニュース画像のコアホワイトリスト
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
    "news-obs.line-scdn.net",
    
    # Payments & Utilities
    "paypay.ne.jp",
    "linepay.line.me",

    # Yahoo! JAPAN Core & Auth & Media Images
    "yahoo.co.jp",
    "yimg.jp",
    "im.c.yimg.jp",
    "c.yimg.jp",
    "sso.yahoo.co.jp",
    "login.yahoo.co.jp",
    "m.yimg.jp",
    
    # LINE / Yahoo Unified Platform
    "line-scdn.net",
    "line-apps.com",
    "line.me",
    "line-website.com",
}

# LINEヤフーエコシステムに関連する許可ドメインパターン
LY_ALLOWED_PATTERNS = [
    "line", "line-scdn", "line-apps", "line-ads", "flvcdn", "slim01",
    "yahoo", "yimg", "yjtag", "sentry", "facebook", "googletagmanager"
]

def clean_domain(raw_entry):
    """URLのコピペミスやAdBlock記号、記号等をパース前に安全に除去して純粋なドメイン名を取り出す"""
    raw_entry = raw_entry.strip().lower()
    
    raw_entry = re.sub(r'^[\|*@.]+', '', raw_entry)
    raw_entry = re.sub(r'[\^/*]+$', '', raw_entry)
    
    if not raw_entry.startswith(('http://', 'https://')):
        parsed = urlparse('http://' + raw_entry)
    else:
        parsed = urlparse(raw_entry)
    
    domain = parsed.netloc or parsed.path
    domain = domain.split(':')[0].split('/')[0]
    domain = re.sub(r'^[\|*.]+', '', domain)
    domain = re.sub(r'[\^/*]+$', '', domain)
    
    return domain.strip()

def check_single_domain_alive(domain):
    """単一ドメインのDNS通信チェック"""
    try:
        socket.setdefaulttimeout(5.0)
        socket.gethostbyname(domain)
        return domain, True
    except (socket.gaierror, socket.timeout, Exception):
        print(f"[DEAD/TIMEOUT DOMAIN SKIPPED] DNS resolution skipped for: {domain}")
        return domain, True

def filter_alive_domains(domains):
    """マルチスレッドで高速並列通信チェック"""
    alive_domains = set()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(check_single_domain_alive, d) for d in domains]
        for future in as_completed(futures):
            domain, is_alive = future.result()
            if is_alive:
                alive_domains.add(domain)
    return alive_domains

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

    raw_domains = set()
    with open("filter.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            
            domain = clean_domain(line)
            if not domain:
                continue

            if is_whitelisted(domain):
                print(f"[SECURITY GUARD] Protected domain removed: {domain}")
                continue
            
            if not is_ly_ecosystem(domain):
                print(f"[SCOPE GUARD] Non-LY Ecosystem domain removed: {domain}")
                continue

            raw_domains.add(domain)

    valid_domains = filter_alive_domains(raw_domains)
    sorted_domains = sorted(list(valid_domains))

    header = (
        "! Title: Japanese-Ads-Filter (OISD Specification)\n"
        "! Description: Absolute safety & zero-breakage ad filtering ONLY for LINE & Yahoo! JAPAN ecosystem.\n"
        "! Homepage: https://github.com/aatmnt21-collab/Japanese-Ads-Filter\n"
        "! Syntax: AdBlock / NextDNS / AdGuard Compatible\n\n"
    )

    with open("filter.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join(sorted_domains) + "\n")

    with open("adblock.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join([f"||{d}^" for d in sorted_domains]) + "\n")

    with open("hosts.txt", "w", encoding="utf-8") as f:
        f.write("# Japanese-Ads-Filter (Hosts Format)\n" + "\n".join([f"0.0.0.0 {d}" for d in sorted_domains]) + "\n")

    print(f"[SUCCESS] Built {len(sorted_domains)} active unique domains successfully.")

if __name__ == "__main__":
    clean_and_build()
