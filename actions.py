from importlib import reload
import requests
import ast
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import platform
import setting
import web


def download_cases():
    setting.STORE_QASE_DATA = []
    setting.STORE_QASE_IDS = []
    offset = 0
    while offset <= 200:  # указываем общее количество существующих автоматических тестов в qase.io
        url = f"https://api.qase.io/v1/case/{setting.QASE_PROJECT_ID}?automation=automated&limit=100&offset={offset}"
        offset = offset + 100  # увеличиваем пропуск еще на 100 тест кейсов
        headers = {
            'Accept': 'application/json',
            'Token': setting.QASE_TOKEN
        }
        response = requests.request('GET', url, headers=headers).json()
        for test_case in response['result']['entities']:
            setting.STORE_QASE_DATA.append(test_case)  # full answer from the QASE.io
            setting.STORE_QASE_IDS.append(test_case['id'])  # list of all test automated tests IDd


def download_plans():
    url = f"https://api.qase.io/v1/plan/{setting.QASE_PROJECT_ID}?limit=100&offset=0"
    headers = {
        "Accept": "application/json",
        "Token": "6bd3e12b43dbac2f119b1f1b278868bc20d20a83"
    }
    response = requests.get(url, headers=headers).json()

    setting.QASE_PLANS_LIST = response['result']['entities']


def create_plan(title):
    # update the list of cases
    download_cases()

    # send request to create plan
    url = f"https://api.qase.io/v1/plan/{setting.QASE_PROJECT_ID}"
    payload = {
        "cases": setting.STORE_QASE_IDS,
        "title": title,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Token": setting.QASE_TOKEN
    }
    response = requests.post(url, json=payload, headers=headers).json()
    reload(setting)


def delete_plan(plan_id):
    url = f"https://api.qase.io/v1/plan/{setting.QASE_PROJECT_ID}/{plan_id}"
    headers = {
        "Accept": "application/json",
        "Token": setting.QASE_TOKEN
    }
    response = requests.delete(url, headers=headers).json()
    reload(setting)


def prepare_case_data(case):
    parent_description = case['description'].replace('\n', '')  # clear QASE description field
    parent_description = parent_description.replace('`', '')  # clear QASE description field
    parent_description = parent_description.replace(']', '],')  # add comma in the end of the list
    parent_description = '[' + parent_description + ']'
    parent_description = ast.literal_eval(parent_description)

    setting.QASE_IDS.append(case['id'])  # add items to the QASE ID variable
    setting.QASE_TESTS.append(parent_description)  # add items to the QASE TESTS variable

    if len(case['attachments']) != 0:  # save file from attachments to the local folder titled elements
        for attachment in case['attachments']:
            r = requests.get(attachment['url'], allow_redirects=True)
            with open(f"{setting.FOLDER_ELEMENTS}/{case['id']}_{attachment['filename']}", 'wb') as f:
                f.write(r.content)


def prepare_specific_case(case_id):
    url = f"https://api.qase.io/v1/case/{setting.QASE_PROJECT_ID}/{case_id}"
    headers = {
        "Accept": "application/json",
        "Token": setting.QASE_TOKEN
    }
    response = requests.get(url, headers=headers).json()

    if response['status'] is True and response['result']['description'] is not None:  # will choose only automated test cases
        prepare_case_data(response['result'])


def prepare_run(plan_id):
    url = f"https://api.qase.io/v1/run/{setting.QASE_PROJECT_ID}?status=active&limit=10&offset=0"  # get the list of runs
    headers = {
        "Accept": "application/json",
        "Token": setting.QASE_TOKEN
    }
    runs = requests.get(url, headers=headers).json()
    if runs['result']['count'] >= 2:  # if the run count is equal or more than 2, do nothing
        pass
    elif runs['result']['count'] == 1 and runs['result']['entities'][0]['description'] == "Automatic test run":  # if the run count is one and description == Automatic test run, do nothing
        pass
    else:
        """url = f"https://api.qase.io/v1/plan/{setting.QASE_PROJECT_ID}?limit=1&offset=0"  # get the oldest plan
        headers = {
            "Accept": "application/json",
            "Token": setting.QASE_TOKEN
        }
        plans = requests.get(url, headers=headers).json()

        if plans['result']['count'] != 0:  # if plan exists"""

        url = f"https://api.qase.io/v1/plan/{setting.QASE_PROJECT_ID}/{plan_id}"  # get data from plan
        headers = {
            "Accept": "application/json",
            "Token": setting.QASE_TOKEN
        }
        plan = requests.get(url, headers=headers).json()

        # start the run preparing
        plan_cases = []  # get the list of cases
        for test_case in plan['result']['cases']:
            plan_cases.append(test_case['case_id'])

        url = f"https://api.qase.io/v1/run/{setting.QASE_PROJECT_ID}"  # create a run
        payload = {
            "cases": plan_cases,
            "title": plan['result']['title'],
            "description": "Automatic test run"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Token": setting.QASE_TOKEN
        }
        new_run = requests.post(url, json=payload, headers=headers).json()

        if new_run['result']['id'] > 0:  # if run is created

            web.flask_change_selected_qase_run_id(new_run['result']['id'])  # save the run's id
            delete_plan(plan['result']['id'])  # delete the plan
            download_cases()  # get all cases from the qase.io

            for case in setting.STORE_QASE_DATA:  # select needed cases
                if case['id'] in plan_cases and case['description'] is not None:  # will choose only automated test cases in the selected run
                    prepare_case_data(case)


def choose_action(data):
    if data[0] == "openPage":
        setting.DRIVER.open_page(data[1])
    elif data[0] == "click":
        setting.DRIVER.mouse_click(data[1])
    elif data[0] == "clicks":
        setting.DRIVER.mouse_clicks(data[1], data[2])
    elif data[0] == "enterValue":
        setting.DRIVER.enter_value(data[1], data[2])
    elif data[0] == "clearValue":
        setting.DRIVER.clear_value(data[1])
    elif data[0] == "pressKeyboardNumbers":
        setting.DRIVER.press_keyboard_numbers(data[1])
    elif data[0] == "select":
        setting.DRIVER.select_one(data[1], data[2])
    elif data[0] == "collectText":
        setting.DRIVER.collect_text(data[1], data[2])
    elif data[0] == "collectValue":
        setting.DRIVER.collect_value(data[1], data[2])
    elif data[0] == "compareVariable":
        setting.DRIVER.compare_variable_with_data(data[1], data[2])
    elif data[0] == "compareValue":
        setting.DRIVER.compare_value_with_data(data[1], data[2])
    elif data[0] == "compareText":
        setting.DRIVER.compare_text_with_data(data[1], data[2])
    elif data[0] == "file":
        setting.DRIVER.upload_file(data[1], data[2])
    elif data[0] == "findElement":
        setting.DRIVER.find_element(data[1])
    elif data[0] == "wait":
        setting.DRIVER.wait_some_time(data[1])
    elif data[0] == "focus":
        setting.DRIVER.element_focus(data[1])
    else:
        assert 1 == 0, f"Unknown action"


class Actions:

    def __init__(self, browser):
        self.action = None
        if browser == "remote":
            self.browser = webdriver.Remote(
                command_executor=setting.URL_SELENOID,
                desired_capabilities=setting.SELENOID_CAPABILITIES)
        else:
            self.browser = browser
        self.browser.implicitly_wait(5)
        self.browser.set_window_size(1340, 1000)

    def open_page(self, link):  # openPage
        link = link.replace(link, setting.URL_FRONTEND)  # replace localhost by setting.FRONTEND_URL
        self.browser.get(link)
        time.sleep(setting.SLEEP * 2)

    def mouse_click(self, selector):  # click
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        element.click()

    def mouse_clicks(self, selector, position):  # clicks
        position = '[' + str(position) + ']'
        position = ast.literal_eval(position)
        for number in position:
            time.sleep(setting.SLEEP)
            assert self.is_element_present(By.TAG_NAME, f"[data-test-id='{selector}']"), f"Can not find {selector}"
            number = self.browser.find_elements(By.TAG_NAME, f"[data-test-id='{selector}']")[int(number)]
            number.click()

    def clear_value(self, selector):  # clearValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        if platform.system() == 'Darwin':
            element.send_keys(Keys.COMMAND + "a")
            element.send_keys(Keys.DELETE)
        else:
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)

    def enter_value(self, selector, value):  # enterValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        element.send_keys(value)

    def press_keyboard_numbers(self, number):  # pressKeyboardNumbers
        time.sleep(setting.SLEEP)
        self.action = ActionChains(self.browser)
        for num in number:
            numpad = 'NUMPAD' + num
            self.action.send_keys(Keys.__str__(numpad))
        self.action.perform()

    def select_one(self, selector, value):  # select
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.XPATH, f"//*[@data-test-id = '{selector}']//li[contains(text(), '{value}')]"), f"Can not find {selector} with value={value}"
        element = self.browser.find_element(By.XPATH, f"//*[@data-test-id = '{selector}']//li[contains(text(), '{value}')]")
        element.click()

    def collect_text(self, selector, name):  # collectText
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']").text
        setting.VARIABLES[name] = element

    def collect_value(self, selector, name):  # collectValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        setting.VARIABLES[name] = element.get_attribute('value')

    def compare_variable_with_data(self, variable_name, value):  # compareVariable
        time.sleep(setting.SLEEP)
        assert setting.VARIABLES[variable_name] == value, f"Expected result: {value}, actual result: {setting.VARIABLES[variable_name]}"

    def compare_text_with_data(self, selector, value):  # compareText
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']").text
        assert element == value, f"Expected result: {value}, actual result: {element}"

    def compare_value_with_data(self, selector, value):  # compareValue
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        element = element.get_attribute('value')
        assert element == value, f"Expected result: {value}, actual result: {element}"

    def upload_file(self, selector, filename):  # file
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"
        element = self.browser.find_element(By.TAG_NAME, f"*[data-test-id='{selector}']")
        link = f"{setting.FOLDER_ELEMENTS}/{setting.QASE_CASE_ID}_{filename}"
        element.send_keys(link)

    def find_element(self, selector):  # findElement
        time.sleep(setting.SLEEP)
        assert self.is_element_present(By.TAG_NAME, f"*[data-test-id='{selector}']"), f"Can not find {selector}"

    def wait_some_time(self, time_in_sec):  # wait
        time.sleep(int(time_in_sec))

    def element_focus(self, selector):  # focus
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
