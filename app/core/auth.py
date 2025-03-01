import logging
import requests
import json
import urllib.parse

class Auth:
    def __init__(self, config):
        self.config = config

    def perform_login(self, username, password, isp):
        encoded_username = urllib.parse.quote(username)
        encoded_password = urllib.parse.quote(password)
        isp_codes = {
            "中国电信": "@telecom",
            "中国移动": "@cmcc",
            "中国联通": "@unicom",
            "校园网": "@campus",
        }
        selected_isp_code = isp_codes.get(isp, "@campus")
        login_url = f"{self.config['api_url']}?c=Portal&a=login&callback=dr1004&login_method=1&user_account={encoded_username}{selected_isp_code}&user_password={encoded_password}"
        
        try:
            response = requests.get(login_url, timeout=5).text
            response_dict = json.loads(response[response.find("{"): response.rfind("}") + 1])
            return response_dict
        except Exception as e:
            logging.error(f"登录过程中发生异常：{e}", exc_info=True)
            return None