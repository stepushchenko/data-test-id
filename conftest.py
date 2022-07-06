import copy
import json

import pytest
import requests
import time
import additional_api_requests
import setting
import actions
from selenium import webdriver
import platform
import ast


@pytest.fixture(autouse=True, scope="session")
def run():

    actions.user_update('variables', {})

    yield

    if actions.user('report') == "active":
        url = f"https://api.qase.io/v1/run/{actions.user('project_code')}/{actions.user('run_id')}/complete"
        headers = {
            "Accept": "application/json",
            "Token": actions.user('token')
        }
        requests.request("POST", url, headers=headers).json()


@pytest.fixture(autouse=True, scope="function")
def clear_database():
    classAPI = additional_api_requests.API()

    if platform.system() == "Darwin":
        classAPI.dev_clear_storage()  # clear database

    parameters_sign_up_admin = {
        "email": "coach1@example.com",
        "code_keyboard": ["NUMPAD1", "NUMPAD2", "NUMPAD3", "NUMPAD4", "NUMPAD5", "NUMPAD6"],
        "code": "123456",
        "name": "Coach 1 (admin)",
        "practice_title": "Admin practice",
        "practice_description": "Admin practice description"
    }

    if platform.system() == "Darwin":
        classAPI.user_auth_send_code_to_website(parameters_sign_up_admin)
        classAPI.user_auth_sign_up(parameters_sign_up_admin)
        classAPI.user_profile_become_coach()
        classAPI.user_profile_update(parameters_sign_up_admin)
        classAPI.admin_gamification_tiers_list()
        classAPI.admin_gamification_tiers_update()
        classAPI.user_auth_logout()

    yield


@pytest.fixture(autouse=True, scope="function")
def qase_preconditions(request):
    actions.user_update('qase_case_status', '')

    try:

        # get a test number
        qase_test_case_id = request.node.name
        qase_test_case_id = qase_test_case_id.replace("]", "")
        qase_test_case_id = qase_test_case_id.partition('[')
        qase_test_case_id = qase_test_case_id[-1]
        actions.user_update('case_id', qase_test_case_id)

        # try to start the kids

        if platform.system() == "Darwin":  # open local browser
            setting.DRIVER = actions.Actions(webdriver.Chrome())
        else:  # tests will run on the remote server
            setting.DRIVER = actions.Actions(webdriver.Remote(command_executor=setting.URL_SELENOID, desired_capabilities=actions.user('selenoid_capabilities')))

        url = f"https://api.qase.io/v1/case/{actions.user('project_code')}/{qase_test_case_id}"
        headers = {
            "Accept": "application/json",
            "Token": actions.user('token')
        }
        response = requests.get(url, headers=headers).json()

        if response['status']:
            parent_case = response['result']

            if parent_case['description'] is not None:  # will choose only automated test cases

                if parent_case['preconditions'] is not None:
                    it_can_be_a_list = parent_case['preconditions'].rsplit("]")
                    it_can_be_a_list = it_can_be_a_list[0] + ']'
                    if it_can_be_a_list.find('[') >= 0:
                        it_can_be_a_list = ast.literal_eval(it_can_be_a_list)
                        if len(it_can_be_a_list) > 0:

                            for child_case_id in it_can_be_a_list:
                                url = f"https://api.qase.io/v1/case/{actions.user('project_code')}/{child_case_id}"
                                headers = {
                                    "Accept": "application/json",
                                    "Token": actions.user('token')
                                }
                                response = requests.get(url, headers=headers).json()
                                if response['result']['description'] is not None:  # will choose only automated test cases
                                    child_description = response['result']['description'].replace('\n', '')  # clear QASE description field
                                    child_description = child_description.replace(']', '],')  # add comma in the end of the list
                                    child_description = '[' + child_description + ']'
                                    child_description = ast.literal_eval(child_description)

                                    for action_data in child_description:
                                        actions.choose_action(action_data)
    except Exception as e:
        actions.user_update('qase_case_status', 'blocked')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True, scope="function")
def case_result(request):

    if actions.user('report') == "active":
        # get a test number
        qase_test_case_id = request.node.name
        qase_test_case_id = qase_test_case_id.replace("]", "")
        qase_test_case_id = qase_test_case_id.partition('[')
        qase_test_case_id = qase_test_case_id[-1]
        actions.user_update('case_id', qase_test_case_id)

        # start of the time tracking
        time_start = int(time.time())

    yield

    if actions.user('report') == "active":

        # duration of the case
        duration = int(time.time()) - time_start

        # status of the case
        comment = ''  # empty comment for passed cases
        if actions.user('qase_case_status') != "blocked":
            if request.node.rep_setup.passed:
                if request.node.rep_call.failed:
                    actions.user_update('qase_case_status', 'failed')
                    comment = comment + str(request.node.rep_call.longreprtext)  # comment with error in description
                else:
                    actions.user_update('qase_case_status', 'passed')

        # post
        url = f"https://api.qase.io/v1/result/{actions.user('project_code')}/{actions.user('run_id')}"
        payload = {
            "case_id": qase_test_case_id,
            "status": actions.user('qase_case_status'),
            "time": duration,
            "comment": comment
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Token": actions.user('token')
        }
        requests.request("POST", url, json=payload, headers=headers).json()
