import pytest
import requests
import time
# import api
import setting
import actions
from selenium import webdriver
import platform
import ast


@pytest.fixture(autouse=True, scope="session")
def run():

    yield

    if setting.QASE_REPORT == "active":
        url = f"https://api.qase.io/v1/run/{setting.QASE_PROJECT_ID}/{setting.QASE_RUN_ID}/complete"
        headers = {
            "Accept": "application/json",
            "Token": setting.QASE_TOKEN
        }
        requests.request("POST", url, headers=headers).json()


@pytest.fixture(autouse=True, scope="function")
def clear_database():
    # classAPI = api.API()

    """
    Feel free to add your project API methods in api.py
    for using them in preconditions
    """

    yield

    """
    Feel free to add your project API methods in api.py
    for using them in postconditions
    """


@pytest.fixture(autouse=True, scope="function")
def qase_preconditions(request):
    setting.QASE_CASE_STATUS = ""
    try:
        # get a test number
        qase_test_case_id = request.node.name
        qase_test_case_id = qase_test_case_id.replace("]", "")
        qase_test_case_id = qase_test_case_id.partition('[')
        qase_test_case_id = qase_test_case_id[-1]
        setting.QASE_CASE_ID = qase_test_case_id

        # try to start the kids

        if platform.system() == "Darwin":  # open local browser
            setting.DRIVER = actions.Actions(webdriver.Chrome())
        else:  # tests will run on the remote server
            setting.DRIVER = actions.Actions(webdriver.Remote(command_executor=setting.URL_SELENOID, desired_capabilities=setting.SELENOID_CAPABILITIES))

        url = f"https://api.qase.io/v1/case/{setting.QASE_PROJECT_ID}/{qase_test_case_id}"
        headers = {
            "Accept": "application/json",
            "Token": setting.QASE_TOKEN
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
                                url = f"https://api.qase.io/v1/case/{setting.QASE_PROJECT_ID}/{child_case_id}"
                                headers = {
                                    "Accept": "application/json",
                                    "Token": setting.QASE_TOKEN
                                }
                                response = requests.get(url, headers=headers).json()
                                if response['result']['description'] is not None:  # will choose only automated test cases
                                    child_description = response['result']['description'].replace('\n', '')  # clear QASE description field
                                    child_description = child_description.replace('`', '')  # clear QASE description field
                                    child_description = child_description.replace(']', '],')  # add comma in the end of the list
                                    child_description = '[' + child_description + ']'
                                    child_description = ast.literal_eval(child_description)

                                    for action_data in child_description:
                                        actions.choose_action(action_data)
    except Exception as e:
        setting.QASE_CASE_STATUS = "blocked"


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

    if setting.QASE_REPORT == "active":
        # get a test number
        qase_test_case_id = request.node.name
        qase_test_case_id = qase_test_case_id.replace("]", "")
        qase_test_case_id = qase_test_case_id.partition('[')
        qase_test_case_id = qase_test_case_id[-1]

        # start of the time tracking
        time_start = int(time.time())

    yield

    if setting.QASE_REPORT == "active":

        # duration of the case
        duration = int(time.time()) - time_start

        # status of the case
        comment = ''  # empty comment for passed cases
        if setting.QASE_CASE_STATUS != "blocked":
            if request.node.rep_setup.passed:
                if request.node.rep_call.failed:
                    setting.QASE_CASE_STATUS = "failed"
                    comment = comment + str(request.node.rep_call.longreprtext)  # comment with error in description
                else:
                    setting.QASE_CASE_STATUS = "passed"

        # post
        url = f"https://api.qase.io/v1/result/{setting.QASE_PROJECT_ID}/{setting.QASE_RUN_ID}"
        payload = {
            "case_id": qase_test_case_id,
            "status": setting.QASE_CASE_STATUS,
            "time": duration,
            "comment": comment
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Token": setting.QASE_TOKEN
        }
        requests.request("POST", url, json=payload, headers=headers).json()
