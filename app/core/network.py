import requests
import socket
import urllib.parse
import logging

class NetworkService:
    ISP_MAPPING = {
        "中国电信": "@telecom",
        "中国移动": "@cmcc",
        "中国联通": "@unicom",
        "校园网": "@campus"
    }

    @staticmethod
    def get_local_ip():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            logging.error(f"IP detection failed: {str(e)}")
            return ""

    @classmethod
    def build_login_url(cls, base_url, username, password, isp):
        encoded_user = urllib.parse.quote(username)
        encoded_pass = urllib.parse.quote(password)
        isp_code = cls.ISP_MAPPING.get(isp, "@campus")
        ip = cls.get_local_ip()
        return (
            f"{base_url}?c=Portal&a=login&callback=dr1004&"
            f"login_method=1&user_account={encoded_user}{isp_code}&"
            f"user_password={encoded_pass}&wlan_user_ip={ip}"
        )

    @staticmethod
    def send_login_request(url):
        try:
            response = requests.get(url, timeout=10)
            return response.text
        except requests.RequestException as e:
            logging.error(f"Login request failed: {str(e)}")
            return None