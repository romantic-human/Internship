"""密码加密工具 — 使用 Django signing 框架实现对称加密"""
import base64
import hashlib
from django.conf import settings
from django.core.signing import Signer, BadSignature

# 从 SECRET_KEY 派生固定签名前缀
_signer = None


def _get_signer():
    global _signer
    if _signer is None:
        _signer = Signer(salt="nl2sql.datasource.password")
    return _signer


def encrypt_password(plain_text: str) -> str:
    """加密密码 → 返回签名字符串"""
    if not plain_text:
        return ""
    signer = _get_signer()
    return signer.sign(plain_text)


def decrypt_password(encrypted: str) -> str:
    """解密密码 → 返回明文；解密失败返回空字符串"""
    if not encrypted:
        return ""
    try:
        signer = _get_signer()
        return signer.unsign(encrypted)
    except BadSignature:
        return ""
