import os

# 絶対にブロックしてはならないLINE/Google/決済のコアホワイトリスト
WHITELIST = {
    "play.googleapis.com",
    "connectivitycheck.gstatic.com",
    "android.clients.google.com",
    "clients4.google.com",
    "inputtools.google.com",
    "legy-jp.line-apps.com",
    "vos.line-scdn.net",
    "a.line.me",
    "profile.line-scdn.net",
    "wcc-image.line-scdn.net",
    "ch.line-scdn.net",
    "d.line-scdn.net",
}

def clean_and_build():
    if not os.path.exists("filter.txt"):
        return

    domains = set()
    with open("filter.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # コメント行や空行はスキップ
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            # ドメインを小文字化
            domain = line.lower().replace("*.", "").replace("||", "").replace("^", "")
            
            # ホワイトリストチェック（誤爆防止）
            if domain in WHITELIST:
                print(f"[WARNING] Safe domain blocked! Removed: {domain}")
                continue
            
            domains.add(domain)

    # アルファベット順にソート
    sorted_domains = sorted(list(domains))

    # 1. 標準 Wildcard/NextDNS 形式 (filter.txt)
    header = (
        "! Title: LYEcosystem-Filter (OISD Specification)\n"
        "! Description: Absolute safety & zero-breakage ad filtering for LINE & Yahoo! JAPAN ecosystem.\n"
        "! Homepage: https://github.com/aatmnt21-collab/LYEcosystem-Filter\n"
        "! Syntax: AdBlock / NextDNS / AdGuard Compatible\n\n"
    )
    with open("filter.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join(sorted_domains) + "\n")

    # 2. AdBlock / Brave 形式 (adblock.txt)
    with open("adblock.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join([f"||{d}^" for d in sorted_domains]) + "\n")

    # 3. Hosts 形式 (hosts.txt)
    with open("hosts.txt", "w", encoding="utf-8") as f:
        f.write("# LYEcosystem-Filter (Hosts Format)\n" + "\n".join([f"0.0.0.0 {d}" for d in sorted_domains]) + "\n")

    print(f"[SUCCESS] Built {len(sorted_domains)} domains successfully.")

if __name__ == "__main__":
    clean_and_build()
