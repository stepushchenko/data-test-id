import setting
import requests
import actions
from datetime import datetime
import json
from importlib import reload


def flask_change_page(url):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['page'] = url
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_project(project_id):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['project'] = int(project_id)
    config['env'] = 0
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_env(env):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['env'] = int(env)
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_selenoid(selenoid):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['selenoid'] = int(selenoid)
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_pytest_start_type(start_type):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['pytest_start_type'] = start_type
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_selected_pytest_case(case):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['pytest_case'] = case
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_selected_qase_report_status(status):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['qase_report_status'] = status
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_change_selected_qase_run_id(run):
    # GET CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json") as f:
        config = json.load(f)
    # UPDATE CONFIG
    config['qase_run_id'] = run
    # SAVE CONFIG
    with open(f"{setting.FOLDER_ROOT}/config.json", 'w') as f:
        json.dump(config, f)
    reload(setting)


def flask_dashboard(url):
    # MENU PROJECTS
    count = 0
    menu_projects_content = ""
    for project in setting.FLASK_PROJECTS:
        if count != setting.FLASK_PROJECT_ID:
            menu_projects_content += f"""<li><a class="dropdown-item" href="/dashboard?change_project={count}">{project['title']}</a></li>"""
        count += 1

    # MENU ENV
    count = 0
    menu_env_content = ""
    for env in setting.FLASK_ENVS:
        if count != setting.FLASK_ENV_ID:
            menu_env_content += f"""<li><a class="dropdown-item" href="/dashboard?change_env={count}">{env['title']}</a></li>"""
        count += 1

    # MENU SELENOID
    count = 0
    menu_selenoid_content = ""
    for selenoid in setting.FLASK_SELENOIDS:
        if count != setting.FLASK_SELENOID_ID:
            menu_selenoid_content += f"""<li><a class="dropdown-item" href="/dashboard?change_selenoid={count}">{selenoid['title']}</a></li>"""
        count += 1

    # CASES PAGE
    if url == "cases":

        url = f"https://api.qase.io/v1/case/{setting.QASE_PROJECT_ID}?automation=automated&limit=100&offset=0"
        headers = {
            "Accept": "application/json",
            "Token": setting.QASE_TOKEN
        }
        response = requests.get(url, headers=headers).json()
        cases = response['result']['entities']

        body_content = """
                <table class="table align-middle">
                    <thead>
                        <tr>
                            <th scope="col">ID</th>
                            <th scope="col">Title</th>
                            <th scope="col">Actions</th>
                        </tr>
                    </thead>
                    <tbody>"""

        for case in cases:
            body_content += f"""<tr>
                    <th scope="row">{case['id']}</th>
                        <td>{case['title']}</td>
                        <td>
                            <a href="dashboard?prepare_specific_case={case['id']}" class="btn btn-outline-success btn-sm">Run</a>
                        </td>
                    </tr>"""

        body_content += """
                    </tbody>
                </table>
                """

    # PLANS PAGE
    elif url == "plans":

        body_content = """<a class="btn btn-sm btn-outline-secondary" href="dashboard?create_plan=yes">Create plan</a><br><br>"""
        actions.download_plans()

        body_content += """
        <table class="table align-middle">
            <thead>
                <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Title</th>
                    <th scope="col">Cases count</th>
                    <th scope="col">Actions</th>
                </tr>
            </thead>
            <tbody>"""

        for plan in setting.QASE_PLANS_LIST:
            body_content += f"""<tr>
            <th scope="row">{plan['id']}</th>
                <td>{plan['title']}</td>
                <td>{plan['cases_count']}</td>
                <td>
                    <a href="/dashboard?prepare_run={plan['id']}" class="btn btn-outline-success btn-sm">Run</a>
                    <a href="/dashboard?delete_plan={plan['id']}" class="btn btn-outline-danger btn-sm">Delete</a>
                </td>
            </tr>"""

        body_content += """
            </tbody>
        </table>
        """

    # RUNS PAGE
    elif url == "runs":

        date = datetime.now()
        timestamp = int(round(date.timestamp())) - 7 * 24 * 60 * 60

        url = f"https://api.qase.io/v1/run/{setting.QASE_PROJECT_ID}?from_start_time={timestamp}&limit=10&offset=0"
        headers = {
            "Accept": "application/json",
            "Token": setting.QASE_TOKEN
        }
        response = requests.get(url, headers=headers).json()

        runs = response['result']['entities']
        runs = list(reversed(runs))

        body_content = """
                        <table class="table align-middle">
                            <thead>
                                <tr>
                                    <th scope="col">ID</th>
                                    <th scope="col">Title</th>
                                    <th scope="col">Status</th>
                                    <th scope="col">Cases count</th>
                                    <th scope="col">Failed</th>
                                    <th scope="col">Actions</th>
                                </tr>
                            </thead>
                            <tbody>"""

        for run in runs:

            # GET REPORT LINK
            url = f"https://api.qase.io/v1/run/{setting.QASE_PROJECT_ID}/{run['id']}/public"
            payload = {"status": True}
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Token": setting.QASE_TOKEN
            }
            response = requests.patch(url, json=payload, headers=headers).json()
            report = response['result']['url']

            if run['stats']['failed'] > 0:
                failed = run['stats']['failed']
            else:
                failed = ""

            # CREATE A TABLE WITH RUNS
            body_content += f"""<tr>
                            <th scope="row">{run['id']}</th>
                                <td>{run['title']}</td>
                                <td>{run['status_text']}</td>
                                <td>{run['stats']['total']}</td>
                                <td>{failed}</td>
                                <td>
                                    <a target="_blank" href="{report}" class="btn btn-outline-success btn-sm">View report</a>
                                </td>
                            </tr>"""

        body_content += """
                            </tbody>
                        </table>
                        """

    # PAGE TEMPLATE
    page_content = f"""
    <!doctype html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>          
            <title>Dashboard</title>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container-fluid">
                    <div class="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown1" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <span style="color: red;">Project</span> {setting.FLASK_PROJECT_TITLE}
                                </a>
                                <ul class="dropdown-menu" aria-labelledby="navbarDropdown1">
                                    {menu_projects_content}
                                </ul>
                            </li>
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown2" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <span style="color: red;">Env</span> {setting.FLASK_ENV_TITLE}
                                </a>
                                <ul class="dropdown-menu" aria-labelledby="navbarDropdown2">
                                    {menu_env_content}
                                </ul>
                            </li>
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown3" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <span style="color: red;">Selenoid</span> {setting.FLASK_SELENOID_TITLE}
                                </a>
                                <ul class="dropdown-menu" aria-labelledby="navbarDropdown3">
                                    {menu_selenoid_content}
                                </ul>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="dashboard?url=cases">Cases</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="dashboard?url=plans">Plans</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="dashboard?url=runs">Runs</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            <div class="container"><br>
                <div class="row">
                    <div class="col-12">
                        {body_content}
                    </div>
                </div>
            </div>
        </body>
    """
    return page_content
