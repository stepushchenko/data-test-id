import requests
import ast
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import platform
import setting
from datetime import datetime
import json


def download_cases():
    store_cases = []
    store_cases_ids = []
    offset = 0
    while offset <= 100:  # enter the total value of automated tests in qase.io
        url = f"https://api.qase.io/v1/case/{user('project_code')}?automation=automated&limit=100&offset={offset}"
        headers = {
            'Accept': 'application/json',
            'Token': user('token')
        }
        response = requests.request('GET', url, headers=headers).json()
        for test_case in response['result']['entities']:
            store_cases.append(test_case)  # full answer from the QASE.io
            store_cases_ids.append(test_case['id'])  # list of all test automated tests IDd
        offset = offset + 100  # get next list of cases
    user_update('store_cases', store_cases)
    user_update('store_cases_ids', store_cases_ids)


def download_plans():
    url = f"https://api.qase.io/v1/plan/{user('project_code')}?limit=100&offset=0"
    headers = {
        "Accept": "application/json",
        "Token": user('token')
    }
    response = requests.get(url, headers=headers).json()

    user_update('store_plans', response['result']['entities'])


def download_runs():
    date = datetime.now()
    timestamp = int(round(date.timestamp())) - 14 * 24 * 60 * 60

    url = f"https://api.qase.io/v1/run/{user('project_code')}?from_start_time={timestamp}&limit=100&offset=0"
    headers = {
        "Accept": "application/json",
        "Token": user('token')
    }
    response = requests.get(url, headers=headers).json()
    runs = response['result']['entities']
    runs = list(reversed(runs))
    store_runs = []

    for run in runs:

        if run['stats']['failed'] > 0:
            failed = run['stats']['failed']
        else:
            failed = ""

        current_run = {
            'id': run['id'],
            'title': run['title'],
            'status': run['status_text'],
            'total_count': run['stats']['total'],
            'failed_count': failed
        }
        store_runs.append(current_run)
    user_update('store_runs', store_runs)


def delete_plan(plan_id):
    url = f"https://api.qase.io/v1/plan/{user('project_code')}/{plan_id}"
    headers = {
        "Accept": "application/json",
        "Token": user('token')
    }
    response = requests.delete(url, headers=headers).json()


def prepare_case_data(case):
    parent_description = case['description'].replace('\n', '')  # clear QASE description field
    parent_description = parent_description.replace(']', '],')  # add comma in the end of the list
    parent_description = '[' + parent_description + ']'
    parent_description = ast.literal_eval(parent_description)

    qase_ids = user('qase_ids')
    qase_ids.append(case['id'])  # add items to the QASE ID variable
    user_update('qase_ids', qase_ids)

    qase_cases = user('qase_cases')
    qase_cases.append(parent_description)  # add items to the QASE TESTS variable
    user_update('qase_cases', qase_cases)

    if len(case['attachments']) != 0:  # save file from attachments to the local folder titled elements
        for attachment in case['attachments']:
            r = requests.get(attachment['url'], allow_redirects=True)
            with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/elements/{case['id']}_{attachment['filename']}", 'wb') as f:
                f.write(r.content)


def prepare_case(case_id):
    url = f"https://api.qase.io/v1/case/{user('project_code')}/{case_id}"
    headers = {
        "Accept": "application/json",
        "Token": user('token')
    }
    response = requests.get(url, headers=headers).json()

    if response['status'] is True and response['result']['description'] is not None:  # will choose only automated test cases
        user_update('qase_ids', [])
        user_update('qase_cases', [])
        prepare_case_data(response['result'])


def check_run_availability():
    url = f"https://api.qase.io/v1/run/{user('project_code')}?status=active&limit=10&offset=0"  # get the list of runs
    headers = {
        "Accept": "application/json",
        "Token": user('token')
    }
    runs = requests.get(url, headers=headers).json()
    if runs['result']['count'] >= 2:  # if the run count is equal or more than 2, do nothing
        return "no"
    elif runs['result']['count'] == 1 and runs['result']['entities'][0]['description'] == "Automatic test run":  # if the run count is one and description == Automatic test run, do nothing
        return "no"
    else:
        return "yes"


def prepare_run(plan_id):
    user_update('qase_ids', [])
    user_update('qase_cases', [])
    if check_run_availability() == "yes":
        url = f"https://api.qase.io/v1/plan/{user('project_code')}/{plan_id}"  # get data from plan
        headers = {
            "Accept": "application/json",
            "Token": user('token')
        }
        plan = requests.get(url, headers=headers).json()

        # start the run preparing
        plan_cases = []  # get the list of cases
        for test_case in plan['result']['cases']:
            plan_cases.append(test_case['case_id'])

        url = f"https://api.qase.io/v1/run/{user('project_code')}"  # create a run
        payload = {
            "cases": plan_cases,
            "title": plan['result']['title'],
            "description": "Automatic test run"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Token": user('token')
        }
        new_run = requests.post(url, json=payload, headers=headers).json()

        if new_run['result']['id'] > 0:  # if run is created

            user_update('run_id', new_run['result']['id'])  # save the run's id
            delete_plan(plan['result']['id'])  # delete the plan
            download_cases()  # get all cases from the qase.io

            for case in user('store_cases'):  # select needed cases
                if case['id'] in plan_cases and case['description'] is not None:  # will choose only automated test cases in the selected run
                    prepare_case_data(case)


def user_update(parameter, value):
    # GET USER
    with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/user.json") as f:
        config = json.load(f)
    # UPDATE USER
    if parameter in ["page", "variables", "report", "qase_ids", "qase_cases", "qase_case_status", "store_plans", "store_cases", "store_runs", "store_cases_ids"]:
        config[parameter] = value
    elif parameter in ["env_id", "run_id", "case_id"]:
        config[parameter] = int(value)
    elif parameter == "project_id":
        config[parameter] = int(value)
        config['env_id'] = 0
        config['envs'] = user('projects')[int(value)]['envs']
        config['url_frontend'] = config['envs'][user('env_id')]['url_frontend']
        config['url_backend'] = config['envs'][user('env_id')]['url_backend']
        config['token'] = user('projects')[int(value)]['qase_token']
        config['project_code'] = user('projects')[int(value)]['qase_project_code']
    elif parameter == "selenoid_id":
        config[parameter] = int(value)
        config['selenoid_capabilities'] = user('selenoids')[int(value)]
    # SAVE USER
    with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/user.json", 'w') as f:
        json.dump(config, f)


def user(parameter):
    with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/user.json") as f:
        config = json.load(f)
    if parameter == "all":
        return config
    else:
        return config[parameter]


def choose_action(data):
    if data[0] == "openPage":
        setting.DRIVER.action_openPage(data[1])
    elif data[0] == "click":
        setting.DRIVER.action_click(data[1])
    elif data[0] == "clicks":
        setting.DRIVER.action_clicks(data[1], data[2])
    elif data[0] == "enterValue":
        setting.DRIVER.action_enterValue(data[1], data[2])
    elif data[0] == "clearValue":
        setting.DRIVER.action_clearValue(data[1])
    elif data[0] == "pressKeyboardNumbers":
        setting.DRIVER.action_pressKeyboardNumbers(data[1])
    elif data[0] == "select":
        setting.DRIVER.action_select(data[1], data[2], data[3])
    elif data[0] == "collect":
        setting.DRIVER.action_collect(data[1], data[2], data[3])
    elif data[0] == "compareVariable":
        setting.DRIVER.action_compareVariable(data[1], data[2])
    elif data[0] == "compareValue":
        setting.DRIVER.action_compareValue(data[1], data[2])
    elif data[0] == "compareText":
        setting.DRIVER.action_compareText(data[1], data[2])
    elif data[0] == "file":
        setting.DRIVER.action_file(data[1], data[2])
    elif data[0] == "findElement":
        setting.DRIVER.action_findElement(data[1])
    elif data[0] == "wait":
        setting.DRIVER.action_wait(data[1])
    elif data[0] == "focus":
        setting.DRIVER.action_focus(data[1])
    else:
        assert 1 == 0, f"Unknown action"


class Actions:

    def __init__(self, browser_t):
        self.action = None
        self.browser = browser_t
        self.browser.implicitly_wait(5)
        self.browser.set_window_size(1340, 1000)

    def action_openPage(self, link):  # openPage
        link = link.replace(link, user('url_frontend'))  # replace localhost by setting.FRONTEND_URL
        self.browser.get(link)
        time.sleep(setting.SLEEP * 2)

    def action_click(self, selector):  # click
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        element.click()

    def action_clicks(self, selector, position):  # clicks
        position = '[' + str(position) + ']'
        position = ast.literal_eval(position)
        for number in position:
            time.sleep(setting.SLEEP)
            assert self.is_element_present(By.TAG_NAME, f"[data-test-id='{selector}']"), f"Can not find {selector}"
            number = self.browser.find_elements(By.TAG_NAME, f"[data-test-id='{selector}']")[int(number)]
            number.click()

    def action_clearValue(self, selector):  # clearValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        if platform.system() == 'Darwin':
            element.send_keys(Keys.COMMAND + "a")
            element.send_keys(Keys.DELETE)
        else:
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)

    def action_enterValue(self, selector, value):  # enterValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        element.send_keys(value)

    def action_pressKeyboardNumbers(self, number):  # pressKeyboardNumbers
        time.sleep(setting.SLEEP)
        self.action = ActionChains(self.browser)
        for num in number:
            numpad = 'NUMPAD' + num
            self.action.send_keys(Keys.__str__(numpad))
        self.action.perform()

    def action_select(self, element_type, selector, value):  # select (element_type: li, option)
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.XPATH, f"//*[@data-test-id = '{selector}']//{element_type}[contains(text(), '{value}')]"), f"Can not find {selector} with value={value}"
        element = self.browser.find_element(By.XPATH, f"//*[@data-test-id = '{selector}']//{element_type}[contains(text(), '{value}')]")
        element.click()

    def action_collect(self, element_type, selector, name):  # collect (element_type: text, value)
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        if element_type == "text":
            element = element.text
        elif element_type == "value":
            element = element.get_attribute('value')
        # setting.VARIABLES[name] = element
        dict_data = user('variables')
        dict_data[name] = element
        user_update('variables', dict_data)

    def action_compareVariable(self, variable_name, value):  # compareVariable
        time.sleep(setting.SLEEP)
        dict_data = user('variables')
        assert dict_data[variable_name] == value, f"Expected result: {value}, actual result: {dict_data[variable_name]}"

    def action_compareText(self, selector, value):  # compareText
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']").text
        assert element == value, f"Expected result: {value}, actual result: {element}"

    def action_compareValue(self, selector, value):  # compareValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        element = element.get_attribute('value')
        assert element == value, f"Expected result: {value}, actual result: {element}"

    def action_file(self, selector, filename):  # file
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        link = f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/elements/{user('case_id')}_{filename}"
        element.send_keys(link)

    def action_findElement(self, selector):  # findElement
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"

    def action_wait(self, time_in_sec):  # wait
        time.sleep(int(time_in_sec))

    def action_focus(self, selector):  # focus
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        self.focus(element)



    #
    # SUB methods
    #

    def is_element_present(self, how, what):
        try:
            self.browser.find_element(how, what)
        except NoSuchElementException:
            return False
        return True

    def selector_name(self, value):
        selector = (By.TAG_NAME, f"*[data-test-id='{value}']")
        return selector

    def selectors_click(self, selector, number):
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        elements = self.browser.find_elements(By.TAG_NAME, f"*[data-test-id='{selector}']")
        number = '[' + str(number) + ']'
        number = ast.literal_eval(number)
        i = 0
        for element in elements:
            if i in number:
                element.click()
                time.sleep(setting.SLEEP)
            i += 1

    def browser_quit(self):
        time.sleep(2)
        self.browser.quit()

    def focus(self, element_name):
        self.browser.execute_script("return arguments[0].scrollIntoView(true);", element_name)
