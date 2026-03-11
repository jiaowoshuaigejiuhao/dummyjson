import json
import time
from copy import deepcopy
from urllib.parse import urljoin
from typing import Any, Dict, Optional

import allure
import requests

from utils.log_util import logger


SENSITIVE_KEYS = {"password", "token", "authorization", "Authorization"}


def _mask(obj: Any) -> Any:
    """脱敏：dict/list/str"""
    if obj is None:
        return None
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if str(k) in SENSITIVE_KEYS:
                new[k] = "***"
            else:
                new[k] = _mask(v)
        return new
    if isinstance(obj, list):
        return [_mask(i) for i in obj]
    return obj


class BaseApi:
    def __init__(
        self,
        base_url: str,
        session: Optional[requests.Session] = None,
        timeout: float = 10.0,
    ) -> None:
        """
        :param base_url: 服务基础地址，如 https://dummyjson.com
        :param session: 可选的复用 Session（用于共享登录态）
        :param timeout: 默认超时时间（秒），可通过 --timeout 覆盖
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.session = session if session else requests.Session()
        self.timeout = timeout

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        统一请求入口：
        - URL 拼接与规范化
        - 默认 timeout
        - 日志 & Allure 附件（请求/响应 + 耗时）
        - 响应 JSON/文本兼容处理
        """
        full_url = urljoin(self.base_url, url.lstrip("/"))

        # 默认 timeout：调用方没传则使用 BaseApi 的配置
        kwargs.setdefault("timeout", self.timeout)

        # 生成脱敏版 kwargs 用于日志和 Allure（避免泄漏 token/password）
        safe_kwargs: Dict[str, Any] = deepcopy(kwargs)
        if "headers" in safe_kwargs:
            safe_kwargs["headers"] = _mask(safe_kwargs["headers"])
        if "json" in safe_kwargs:
            safe_kwargs["json"] = _mask(safe_kwargs["json"])
        if "data" in safe_kwargs and isinstance(safe_kwargs["data"], (dict, list)):
            safe_kwargs["data"] = _mask(safe_kwargs["data"])

        method_u = method.upper()
        step_name = f"{method_u} {url}"

        with allure.step(step_name):
            start = time.time()
            logger.debug(f"[REQ] {method_u} {full_url} kwargs={safe_kwargs}")

            # 附件Request
            try:
                allure.attach(
                    json.dumps(
                        {
                            "method": method_u,
                            "url": full_url,
                            **safe_kwargs,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    name="Request",
                    attachment_type=allure.attachment_type.JSON,
                )
            except TypeError:
                # 无法被 json 序列化就退回到 TEXT
                allure.attach(
                    str({"method": method_u, "url": full_url, **safe_kwargs}),
                    name="Request (text)",
                    attachment_type=allure.attachment_type.TEXT,
                )

            try:
                res = self.session.request(method=method_u, url=full_url, **kwargs)
            except Exception as e:
                elapsed_ms = int((time.time() - start) * 1000)
                logger.exception(f"[REQUEST FAILED] {method_u} {full_url} in {elapsed_ms} ms")
                raise

            elapsed_ms = int((time.time() - start) * 1000)

            # Response meta
            try:
                meta = {
                    "status_code": res.status_code,
                    "elapsed_ms": elapsed_ms,
                    "headers": dict(res.headers),
                    "url": res.url,
                }
                allure.attach(
                    json.dumps(meta, ensure_ascii=False, indent=2),
                    name="Response Meta",
                    attachment_type=allure.attachment_type.JSON,
                )
            except Exception:
                pass

            # 优先 JSON，否则 text
            try:
                body = res.json()
                logger.debug(f"[RES] {method_u} {full_url} status={res.status_code} elapsed={elapsed_ms}ms body={body}")
                allure.attach(
                    json.dumps(body, ensure_ascii=False, indent=2),
                    name="Response Body",
                    attachment_type=allure.attachment_type.JSON,
                )
            except ValueError:
                text_body = res.text
                logger.warning(f"[RES] {method_u} {full_url} JSON decode failed, fallback to text. status={res.status_code}")
                logger.debug(f"[RES] text_body={text_body}")
                allure.attach(
                    text_body,
                    name="Response Body (text)",
                    attachment_type=allure.attachment_type.TEXT,
                )

            return res

    def set_token(self, token: str, scheme: str = "Bearer") -> None:
        """
        将 token 写入 session.headers['Authorization']
        """
        auth_value = f"{scheme} {token}" if scheme else token
        self.session.headers.update({"Authorization": auth_value})
        logger.info("Token set to session headers")