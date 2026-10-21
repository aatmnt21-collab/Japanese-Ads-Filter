import os

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

def is_whitelisted(domain):
    for safe in WHITELIST:
        if domain == safe or domain.endswith("." + safe):
            return True
    return False

def clean_and_build():
    if not os.path.exists("filter.txt"):
        return

    domains = set()
    with open("filter.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            
            domain = line.lower().replace("*.", "").replace("||", "").replace("^", "")
            
            if is_whitelisted(domain):
                print(f"[SECURITY GUARD] Protected domain detected and removed: {domain}")
                continue
            
            domains.add(domain)

    sorted_domains = sorted(list(domains))

    header = (
        "! Title: LYEcosystem-Filter (OISD Specification)\n"
        "! Description: Absolute safety & zero-breakage ad filtering for LINE & Yahoo! JAPAN ecosystem.\n"
        "! Homepage: https://github.com/aatmnt21-collab/LYEcosystem-Filter\n"
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
        f.write("# LYEcosystem-Filter (Hosts Format)\n" + "\n".join([f"0.0.0.0 {d}" for d in sorted_domains]) + "\n")

    print(f"[SUCCESS] Built {len(sorted_domains)} domains successfully.")

if __name__ == "__main__":
    clean_and_build()
