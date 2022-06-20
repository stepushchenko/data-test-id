# import requests
# import inspect
# import setting


class API:

    def __init__(self):
        pass

    def log(self, request, response, function_title):
        if response["error"] is None:
            return print(f"Success: {function_title}")
        else:
            return print(f"Error: {response['error']['code']} \n\n {response['error']} \n\n {request} \n\n")

    """
    Feel free to add your project API methods here 
    for using them in preconditions and postconditions in conftest.py
    """
