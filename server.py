import subprocess
from flask import Flask, request, abort
import actions
import setting
import web

app = Flask(__name__)


@app.route('/dashboard')
def dashboard():
    if request.args.get('url') is not None:
        web.flask_change_page(request.args.get('url'))

    if request.args.get('update_selenoid_config') is not None:
        web.flask_change_page(request.args.get('update_selenoid_config'))

    if request.args.get('change_project') is not None:
        web.flask_change_project(request.args.get('change_project'))

    if request.args.get('change_env') is not None:
        web.flask_change_env(request.args.get('change_env'))

    if request.args.get('change_selenoid') is not None:
        web.flask_change_selenoid(request.args.get('change_selenoid'))

    if request.args.get('create_plan') is not None:
        actions.create_plan("Automated tests")

    if request.args.get('delete_plan') is not None:
        actions.delete_plan(request.args.get('delete_plan'))

    if request.args.get('prepare_specific_case') is not None:
        web.flask_change_pytest_start_type("prepare_specific_case")
        web.flask_change_selected_pytest_case(request.args.get('prepare_specific_case'))
        subprocess.Popen([setting.FOLDER_ROOT + '/scripts/pytest_skeleton.sh', setting.FLASK_PATH])  # start bash script

    if request.args.get('prepare_run') is not None:
        web.flask_change_pytest_start_type("prepare_run")
        web.flask_change_selected_pytest_case(request.args.get('prepare_run'))
        subprocess.Popen([setting.FOLDER_ROOT + '/scripts/pytest_skeleton.sh', setting.FLASK_PATH])  # start bash script

    if request.args.get('url') is not None:
        return web.flask_dashboard(request.args.get('url'))
    elif request.args.get('url') is None:
        return f"""<meta http-equiv="Refresh" content="0; url='/dashboard?url={setting.FLASK_PAGE}'" />"""


if __name__ == '__main__':
    app.run(host=setting.URL_FLASK, port=11100, debug=True)
