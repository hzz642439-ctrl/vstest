import hashlib
import string
import random

def is_english(s: str) -> bool:
    """判断字符串是否全是英文（字母和数字）"""
    return all(c.isascii() and c.isalnum() for c in s)

def stable_random_name(name: str, length: int = 10) -> str:
    """根据名字生成固定的 10 位随机字符串"""
    md5_hash = hashlib.md5(name.encode("utf-8")).hexdigest()
    chars = string.ascii_letters + string.digits
    return ''.join(chars[int(md5_hash[i:i+2], 16) % len(chars)] for i in range(length))