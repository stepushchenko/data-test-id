import os.path
import json

# FOLDERS URLs

FOLDER_ROOT = os.path.dirname(os.path.realpath(__file__))
FOLDER_ELEMENTS = FOLDER_ROOT + '/elements'

# GET CONFIG
with open(f"{FOLDER_ROOT}/config.json") as f:
    config = json.load(f)

FLASK_PROJECTS = [
    {
        "title": "",  # add project title
        "qase_token": "6bd3e12b43dbac2f119b1f1b278868bc20d20a83",  # add QASE.io token
        "qase_project_id": "CASE",  # add QASE.io project title
        "env": [
            {
                "title": "localhost",  # add ENV title
                "url_flask": "localhost",  # add FLASK URL
                "path_pytest": "documents/yourcoach/test_ui",  # add PYTHONPATH here
                "url_frontend": "http://localhost",  # add frontend URL for API methods
                "url_backend": "http://localhost",  # add backend URL for API methods
                "url_selenoid": "http://localhost:4444/wd/hub"  # add Selenoid URL
            }
        ]
    }
]
FLASK_SELENOIDS = [
    {
        "title": "Chrome 101",  # add Selenoid capabilities title here
        "browserName": "chrome",  # add browser title
        "browserVersion": "101.0",  # add browser version
        "platform": "LINUX",  # add Platform
        "selenoid:options": {
            "enableVNC": "True",
            "enableVideo": "True",
            "videoName": "video_title.mp4"
        }
    }
]

selected_selenoid_data = FLASK_SELENOIDS[config['selenoid']]
selected_project_data = FLASK_PROJECTS[config['project']]
selected_env_data = FLASK_PROJECTS[config['project']]['env'][config['env']]

FLASK_PAGE = config['page']
FLASK_PROJECT_ID = config['project']
FLASK_ENV_ID = config['env']
FLASK_SELENOID_ID = config['selenoid']
FLASK_PYTEST_START_TYPE = config['pytest_start_type']
FLASK_CASE = config['pytest_case']

FLASK_PROJECT_TITLE = selected_project_data['title']
FLASK_ENVS = selected_project_data['env']
FLASK_ENV_TITLE = selected_env_data['title']
FLASK_SELENOID_TITLE = selected_selenoid_data['title']
FLASK_PYTEST_PATH = selected_env_data['path_pytest']

QASE_TOKEN = selected_project_data['qase_token']
QASE_PROJECT_ID = selected_project_data['qase_project_id']
QASE_RUN_ID = config['qase_run_id']
QASE_IDS = []
QASE_TESTS = []
QASE_ATTACHMENTS = {}
QASE_REPORT = config['qase_report_status']
QASE_CASE_ID = ""
QASE_CASE_STATUS = ""
QASE_PLANS_LIST = {}

STORE_QASE_IDS = []
STORE_QASE_DATA = []

DRIVER = ""
VARIABLES = {}

# LINKS

URL_FLASK = selected_env_data['url_flask']
URL_FRONTEND = selected_env_data['url_frontend']
URL_SELENOID = selected_env_data['url_selenoid']
URL_BACKEND = selected_env_data['url_backend']

# SELENOID

SELENOID_CAPABILITIES = selected_selenoid_data

# TIME

SLEEP = 0.5
