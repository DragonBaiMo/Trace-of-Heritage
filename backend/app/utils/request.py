"""请求相关的工具函数。"""
from fastapi import Request


def extract_client_ip(request: Request) -> str:
    """尽可能从 Request 中提取客户端 IP 地址，若无法识别则返回 ``unknown``。"""

    if request.client and request.client.host:
        return request.client.host
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return "unknown"
