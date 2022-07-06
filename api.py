import json
import actions
import setting
import requests
import subprocess
import hashlib
import treelib


def case_create(params):
    pass


def case_get(params):
    url = f"https://api.qase.io/v1/case/{actions.user('project_code')}/{params['case_id']}"
    headers = {
        "Accept": "application/json",
        "Token": actions.user('token')
    }
    response = requests.get(url, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {
                'id': response['result']['id'],
                'title': response['result']['title'],
                'description': response['result']['description'],
                'preconditions': response['result']['preconditions'],
                'postconditions': response['result']['postconditions'],
                'severity': response['result']['severity'],
                'priority': response['result']['priority'],
                'automation': response['result']['automation'],
                'attachments': response['result']['attachments']
            }
        }
        return json.dumps(answer, indent=4)


def case_delete(params):
    pass


def case_run(params):
    user_update({'parameter': 'case_id', 'value': params['case_id']})
    user_update({'parameter': 'run_id', 'value': '0'})
    subprocess.Popen([setting.FOLDER_ROOT + '/static/scripts/pytest_skeleton.sh', setting.PATH])  # start bash script
    answer = {
        'status': 'success',
        'result': {}
    }
    return json.dumps(answer, indent=4)


def case_update(params):
    url = f"https://api.qase.io/v1/case/{actions.user('project_code')}/{params['case_id']}"
    description = "```" + params['description'] + "```"
    payload = {
        'title': params['title'],
        'description': description
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Token": actions.user('token')
    }
    response = requests.patch(url, json=payload, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {}
        }
        return json.dumps(answer, indent=4)


def cases_get(params):
    cases = []
    suites_with_autotests = []
    offset = 0
    while offset <= 100:  # enter the total value of automated tests in qase.io
        url = f"https://api.qase.io/v1/case/{actions.user('project_code')}?automation=automated&limit=100&offset={offset}"
        headers = {
            'Accept': 'application/json',
            'Token': actions.user('token')
        }
        response = requests.request('GET', url, headers=headers).json()
        if response['status'] is True:
            for test_case in response['result']['entities']:
                case = {
                    'id': test_case['id'],
                    'title': test_case['title'],
                    'suite_id': test_case['suite_id']
                }
                cases.append(case)
                suites_with_autotests.append([test_case['suite_id']])  # add suite_id to the list
            offset = offset + 100  # get next list of cases

    # REMOVE DUPLICATES
    remove_duplicates = []
    for i in suites_with_autotests:
        if i not in remove_duplicates:
            remove_duplicates.append(i)
    suites_with_autotests = remove_duplicates

    # SEND RESPONSE
    answer = {
        'status': 'success',
        'result': {
            'cases': cases,
            'suites_with_autotests': suites_with_autotests
        }
    }
    return json.dumps(answer, indent=4)


def plan_get(params):
    url = f"https://api.qase.io/v1/plan/{actions.user('project_code')}/{params['plan_id']}"
    headers = {
        "Accept": "application/json",
        "Token": actions.user('token')
    }
    response = requests.get(url, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {
                'id': response['result']['id'],
                'title': response['result']['title'],
                'description': response['result']['description'],
                'cases_count': response['result']['cases_count'],
                'cases': response['result']['cases']
            }
        }
        return json.dumps(answer, indent=4)


def plan_create(params):
    actions.download_cases()  # update the list of cases to use them in the plan creation
    # send request to create plan
    url = f"https://api.qase.io/v1/plan/{actions.user('project_code')}"
    payload = {
        "cases": actions.user('store_cases_ids'),
        "title": params['title'],
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Token": actions.user('token')
    }
    response = requests.post(url, json=payload, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {
                'id': response['result']['id']
            }
        }
        return json.dumps(answer, indent=4)


def plan_delete(params):
    url = f"https://api.qase.io/v1/plan/{actions.user('project_code')}/{params['plan_id']}"
    headers = {
        "Accept": "application/json",
        "Token": actions.user('token')
    }
    response = requests.delete(url, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {}
        }
        return json.dumps(answer, indent=4)


def run_run(params):
    user_update({'parameter': 'case_id', 'value': '0'})
    actions.user_update('run_id', params['run_id'])
    subprocess.Popen([setting.FOLDER_ROOT + '/static/scripts/pytest_skeleton.sh', setting.PATH])  # start bash script
    answer = {
        'status': 'success',
        'result': {}
    }
    return json.dumps(answer, indent=4)


def run_get(params):
    # GET REPORT LINK
    url = f"https://api.qase.io/v1/run/{actions.user('project_code')}/{params['run_id']}"
    payload = {"status": True}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Token": actions.user('token')
    }
    response = requests.patch(url, json=payload, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {
                'id': response['result']['id'],
                'title': response['result']['title'],
                'description': response['result']['description'],
                'status': response['result']['status'],
                'status_text': response['result']['status_text'],
                'start_time': response['result']['start_time'],
                'end_time': response['result']['end_time'],
                'public': response['result']['public'],
                'stats': response['result']['stats'],
                'time_spent': response['result']['time_spent']
            }
        }
        return json.dumps(answer, indent=4)


def run_get_report(params):
    # GET REPORT LINK
    url = f"https://api.qase.io/v1/run/{actions.user('project_code')}/{params['run_id']}/public"
    payload = {"status": True}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Token": actions.user('token')
    }
    response = requests.patch(url, json=payload, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {
                'report_link': response['result']['url']
            }
        }
        return json.dumps(answer, indent=4)


def suite_get(params):
    url = f"https://api.qase.io/v1/suite/{actions.user('project_code')}/{params['suite_id']}"
    headers = {
        "Accept": "application/json",
        "Token": actions.user('token')
    }
    response = requests.get(url, headers=headers).json()
    if response['status'] is True:
        answer = {
            'status': 'success',
            'result': {
                'suite_id': response['result']['id'],
                'title': response['result']['title'],
                'parent_id': response['result']['parent_id']
            }
        }

        print(answer)
        return json.dumps(answer, indent=4)


def suites_get(params):
    # GET DATA FROM QASE
    suite_ids = []
    suites = []
    offset = 0
    while offset <= 300:  # enter the total value of automated tests in qase.io
        url = f"https://api.qase.io/v1/suite/{actions.user('project_code')}?limit=100&offset={offset}"
        headers = {
            'Accept': 'application/json',
            'Token': actions.user('token')
        }
        response = requests.request('GET', url, headers=headers).json()
        if response['status'] is True:
            for suite in response['result']['entities']:
                if suite['parent_id'] is None:
                    suite['parent_id'] = 0
                suite_ids.append(suite['id'])  # add id to the list of suites_ids
                suites.append(suite)  # save all suites data
            offset = offset + 100  # get next list of suites
    suite_ids.append(0)
    suite_ids.sort()

    # SORT SUITS FROM TOP TO BOTTOM
    for x in range(300):
        for suite in suites:
            position_parent_id = suite_ids.index(suite['parent_id'])
            position_id = suite_ids.index(suite['id'])
            parent_id = suite['parent_id']
            if position_parent_id > position_id:
                suite_ids.remove(suite['parent_id'])
                suite_ids.insert(suite_ids.index(suite['id']), parent_id)
        x += x

    # CREATE FULL DATA LIST
    sorted_full_data_list = []
    for suite_id in suite_ids:
        for suite in suites:
            if suite_id == suite['parent_id']:
                sorted_full_data_list.append(suite)

    # CREATE TREE
    tree = treelib.Tree()
    tree.create_node('navigation', 0, data={'id': 0, 'title': 'Navigation', 'parent_id': 0})
    for suite in sorted_full_data_list:
        tree.create_node(suite['title'], suite['id'], parent=suite['parent_id'], data={'id': suite['id'], 'title': suite['title'], 'parent_id': suite['parent_id']})

    # REMOVE ROOT FROM TREE
    tree = tree.to_json(with_data=True)
    tree = json.loads(tree)
    tree = tree['navigation']['children']

    # SEND ANSWER
    answer = {
        'status': 'success',
        'result': {
            'suites': tree
        }
    }
    return json.dumps(answer, indent=4)


def user_password_change(params):
    user_id = int(params['user_id'])
    password = str(params['password'])

    # OPEN USERS
    with open(f"{setting.FOLDER_ROOT}/users/users.json") as f:
        users = json.load(f)

    # GET CURRENT USER EMAIL
    email = ""
    for user in users:
        if user['id'] == user_id:
            email = user['email']

    # CREATE NEW HASH
    summary = email + password
    summary = summary.encode()
    hash_result = hashlib.sha256(summary).hexdigest()

    # ADD NEW HASH TO USERS
    users[user_id]['hash'] = hash_result

    # SAVE USERS
    with open(f"{setting.FOLDER_ROOT}/users/users.json", 'w') as f:
        json.dump(users, f)

    # SEND ANSWER
    answer = {
        'status': 'success',
        'result': {
            'config': users
        }
    }
    return json.dumps(answer, indent=4)


def user_get(params):
    with open(f"{setting.FOLDER_ROOT}/users/users.json") as f:
        users = json.load(f)

    with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/user.json") as f:
        config = json.load(f)

    # SEARCH FOR A USER
    for user in users:
        if user['id'] == params['user_id']:
            config['email'] = user['email']

    answer = {
        'status': 'success',
        'result': {
            'config': config
        }
    }
    return json.dumps(answer, indent=4)


def user_sign_in(params):
    summary = params['email'] + params['password']
    summary = summary.encode()
    hash_result = hashlib.sha256(summary).hexdigest()

    # OPEN USERS CONFIG
    with open(f"{setting.FOLDER_ROOT}/users/users.json") as f:
        users = json.load(f)

    # SEARCH FOR A USER
    for user in users:
        if user['hash'] == hash_result:
            answer = {
                'status': 'success',
                'result': {
                    'id': user['id'],
                    'email': params['email']
                }
            }
            return json.dumps(answer, indent=4)


def user_sign_up(params):
    summary = params['email'] + params['password']
    summary = summary.encode()
    hash_result = hashlib.sha256(summary).hexdigest()
    # OPEN USER CONFIG
    with open(f"{setting.FOLDER_ROOT}/users/users.json") as f:
        users = json.load(f)
    # PREPARE UPDATES

    if len(users) == 0:
        user_id = 0
    else:
        last_id = users[-1]['id']
        user_id = last_id + 1

    users.append({'id': user_id, 'hash': hash_result, 'email': params['email']})
    # SAVE UPDATES
    with open(f"{setting.FOLDER_ROOT}/users/users.json", 'w') as f:
        json.dump(users, f)

    answer = {
        'status': 'success',
        'result': {
            'id': user_id
        }
    }
    return json.dumps(answer, indent=4)


def user_update(params):
    # GET USER
    with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/user.json") as f:
        config = json.load(f)
    # UPDATE USER CONFIG
    if params['parameter'] in ["page", "variables", "report", "qase_ids", "qase_cases", "qase_case_status", "store_plans", "store_cases", "store_runs", "store_cases_ids"]:
        config[params['parameter']] = params['value']
    elif params['parameter'] in ["env_id", "run_id", "case_id"]:
        config[params['parameter']] = int(params['value'])
    elif params['parameter'] == "project_id":
        config[params['parameter']] = int(params['value'])
        config['env_id'] = 0
        config['envs'] = actions.user('projects')[int(params['value'])]['envs']
        config['url_frontend'] = config['envs'][actions.user('env_id')]['url_frontend']
        config['url_backend'] = config['envs'][actions.user('env_id')]['url_backend']
        config['token'] = actions.user('projects')[int(params['value'])]['qase_token']
        config['project_code'] = actions.user('projects')[int(params['value'])]['qase_project_code']
    elif params['parameter'] == "selenoid_id":
        config[params['parameter']] = int(params['value'])
        config['selenoid_capabilities'] = actions.user('selenoids')[int(params['value'])]
    # SAVE USER
    with open(f"{setting.FOLDER_ROOT}/users/user_{setting.USER_ID}/user.json", 'w') as f:
        json.dump(config, f)
    answer = {
        'status': 'success',
        'result': {
            'config': config
        }
    }
    return json.dumps(answer, indent=4)


def users_get(params):
    with open(f"{setting.FOLDER_ROOT}/users/users.json") as f:
        users = json.load(f)

    answer = {
        'status': 'success',
        'result': {
            'users': users
        }
    }
    return json.dumps(answer, indent=4)
