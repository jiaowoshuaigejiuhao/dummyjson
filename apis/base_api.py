import requests
import allure
from utils.log_util import logger


class BaseApi:
    def __init__(self, base_url: str, session: requests.Session = None):
        """
        :param base_url: 基础地址
        :param session: (关键修改) 默认为 None
                        如果传入 session，则复用
                        如果不传，则新建
        """
        self.base_url = base_url.rstrip("/")

        self.session = session if session else requests.Session()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        基础封装
        """
        full_url = self.base_url + url


        with allure.step(f"{method.upper()} {url}"):
            logger.debug(f'[REQ] method: {method} url: {full_url}, kwargs: {kwargs}')

            try:
                res = self.session.request(method=method, url=full_url, **kwargs)
            except Exception as e:
                logger.error(f"[REQUEST FAILED] {e}")
                raise e

            # 响应处理
            try:
                res_body = res.json()
                logger.debug(f'[RES] status_code:{res.status_code} res_body: {res_body}')

                # 将响应体附件到 Allure 报告中
                allure.attach(str(res_body), "Response Body", allure.attachment_type.TEXT)

            except ValueError:
                res_body = res.text
                logger.warning(f'[RESPONSE JSON FAILED] Fallback to text. Status: {res.status_code}')
                logger.debug(f'[RES] res_text: {res_body}')

            return res

    def set_token(self, token: str, scheme: str = 'Bearer'):
        """
        将token插入session.headers
        """
        auth_value = f"{scheme} {token}" if scheme else token
        self.session.headers.update({
            "Authorization": auth_value
        })
        logger.info(f"Token set to headers. Scheme: {scheme}")