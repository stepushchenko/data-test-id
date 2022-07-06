import requests
import inspect
import setting
import actions


class API:

    def __init__(self):
        self.TIERS_LIST = None
        self.PROGRAM_TITLE = None
        self.COACH_CODE = None
        self.COACH_EMAIL = None
        self.CREATED_EDITION_ID = None
        self.CREATED_PROGRAM_ID = None
        self.ACCESS_TOKEN = None
        self.USER_ID = None
        self.AUTH = None
        self.TRUE = bool("true")
        self.API_VERSION = [9, 0]

    def log(self, request, response, function_title):
        if response["error"] is None:
            return print(f"Success: {function_title}")
        else:
            return print(f"Error: {response['error']['code']} \n\n {response['error']} \n\n {request} \n\n")

    def user_auth_send_code_dry_run(self):
        data = {
            "id": 1,
            "method": "user.auth.send_code",
            "meta": {
                "token": "valid",
                "version": self.API_VERSION
            },
            "params":
                {
                    "dry_run": self.TRUE,
                    "email": self.COACH_EMAIL,
                    "platform": "web"
                }
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)

    def user_auth_send_code_to_website(self, data):
        data = {
            "id": 1,
            "method": "user.auth.send_code",
            "meta": {
                "token": "valid",
                "version": self.API_VERSION
            },
            "params":
                {
                    "to_website": self.TRUE,
                    "email": data["email"],
                    "platform": "web",
                }
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)

    def user_auth_send_code(self):
        data = {
            "id": 1,
            "method": "user.auth.send_code",
            "meta": {
                "token": "valid",
                "version": self.API_VERSION
            },
            "params":
                {
                    "email": self.COACH_EMAIL,
                    "platform": "web",
                }
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)

    def user_auth_sign_up(self, data):
        data = {
            "id": 1,
            "method": "user.auth.signup",
            "meta": {
                "token": "valid",
                "version": self.API_VERSION
            },
            "params":
                {
                    "code": data["code"],
                    "device": "Google Chrome",
                    "email": data["email"],
                    "name": data["name"],
                    "platform": "web",
                    "push_token": None
                }
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)
        self.AUTH = response["result"]["session"]["token"]
        self.ACCESS_TOKEN = response["result"]["access"]["token"]
        self.USER_ID = response["result"]["user"]["_id"]

    def dev_clear_storage(self):
        data = {
            "id": 1,
            "meta":
                {
                    "version": self.API_VERSION
                },
            "method": "dev.clear_storage",
            "params": {}
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)

    def admin_gamification_tiers_list(self):
        data = {
            'id': 1,
            'meta':
                {
                    'access_token': self.ACCESS_TOKEN,
                    'version': self.API_VERSION
                },
            'method': 'admin.gamification.tiers.list',
            'params':
                {
                    'limit': 51,
                    'sort': [['level', 1]]
                }
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)
        self.TIERS_LIST = response["result"]["_items"]

    def admin_gamification_tiers_update(self):
        for tier in self.TIERS_LIST:
            data = {
                "id": 1,
                "meta":
                    {
                        "access_token": self.ACCESS_TOKEN,
                        "version": self.API_VERSION
                    },
                "method": "admin.gamification.tiers.update",
                "params":
                    {
                        'upgrade_point_limit': 1000000,
                        '_id': tier['_id']
                    }
            }
            post = requests.post(actions.user('url_backend'), json=data)
            response = post.json()
            self.log(data, response, inspect.currentframe().f_code.co_name)

    def user_profile_become_coach(self):
        data = {
            "id": 1,
            "meta":
                {
                    "access_token": self.ACCESS_TOKEN,
                    "version": self.API_VERSION
                },
            "method": "user.profile.become_coach",
            "params": {}
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)

    def user_profile_update(self, data):
        data = {
            "id": 1,
            "meta":
                {
                    "access_token": self.ACCESS_TOKEN,
                    "version": self.API_VERSION
                },
            "method": "user.profile.update",
            "params":
                {
                    "coach_categories": [],
                    "coach_description": data["practice_description"],
                    "coach_logo_id": None,
                    "coach_title": data["practice_title"]
                }
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)

    def user_auth_logout(self):
        data = {
            "id": 1,
            "meta":
                {
                    "access_token": self.ACCESS_TOKEN,
                    "version": self.API_VERSION
                },
            "method": "user.auth.logout",
            "params": {}
        }
        post = requests.post(actions.user('url_backend'), json=data)
        response = post.json()
        self.log(data, response, inspect.currentframe().f_code.co_name)
