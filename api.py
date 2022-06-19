# import requests
# import inspect
# import setting


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

    """
    Feel free to add your project API methods here 
    for using them in preconditions and postconditions in conftest.py
    """
