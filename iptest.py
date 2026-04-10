import socket
import urllib.error
import urllib.request


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def get_public_ip(timeout: float = 10.0) -> str:
    """經由對外 HTTPS 服務查目前連線的公網 IP（與區網 192.168.x.x 不同）。"""
    urls = (
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
    )
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "iptest/1"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                text = r.read().decode().strip()
                if text:
                    return text
        except (OSError, urllib.error.URLError, ValueError):
            continue
    raise RuntimeError("無法取得對外 IP（請檢查網路或防火牆）")


if __name__ == "__main__":
    print("區網 IP:", get_local_ip())
    print("對外 IP:", get_public_ip())
