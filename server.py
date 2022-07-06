from flask import Flask, request, session, render_template
import actions
import setting
import api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cdsjknc0239er23jnweedckjn832njkwe!kjdc s..dscdkjcn'


@app.route('/')
def profile():
    if 'user_id' in session:
        return f"""<meta http-equiv="Refresh" content="0; url=/dashboard" />"""
    else:
        return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    session.permanent = True
    if 'user_id' in session:
        if actions.user('page') == "profile":
            return render_template('profile.html', user=actions.user('all'))
        elif actions.user('page') == "settings":
            return render_template('settings.html', user=actions.user('all'))
        elif actions.user('page') == "cases":
            return render_template('cases.html', user=actions.user('all'))
        elif actions.user('page') == "runs":
            actions.download_plans()
            actions.download_runs()
            return render_template('runs.html', user=actions.user('all'))
        elif actions.user('page') == "logout":
            session.clear()
            return f"""<meta http-equiv="Refresh" content="0; url=/" />"""
        else:
            return render_template('profile.html', user=actions.user('all'))
    else:
        return f"""<meta http-equiv="Refresh" content="0; url=/" />"""


@app.route('/api', methods=['GET', 'POST'])
def activate_api_method():
    if request.method == 'GET':
        return render_template('api.html', user=actions.user('all'))
    if request.method == 'POST':
        output = request.get_json()
        method = output['method']
        params = output['params']

        if method == 'case.get':
            return api.case_get(params)
        elif method == 'case.create':
            return api.case_create(params)
        elif method == 'case.update':
            return api.case_update(params)
        elif method == 'case.delete':
            return api.case_delete(params)
        elif method == 'case.run':
            return api.case_run(params)
        elif method == 'cases.get':
            return api.cases_get(params)
        elif method == 'plan.create':
            return api.plan_create(params)
        elif method == 'plan.get':
            return api.plan_get(params)
        elif method == 'plan.delete':
            return api.plan_delete(params)
        elif method == 'run.run':
            return api.run_run(params)
        elif method == 'run.get.report':
            return api.run_get_report(params)
        elif method == 'suite.get':
            return api.suite_get(params)
        elif method == 'suites.get':
            return api.suites_get(params)
        elif method == 'user.get':
            return api.user_get(params)
        elif method == 'user.password.change':
            return api.user_password_change(params)
        elif method == 'user.sign_up':
            session['user_id'] = 1
            return api.user_sign_up(params)
        elif method == 'user.sign_in':
            session['user_id'] = 1
            return api.user_sign_in(params)
        elif method == 'user.update':
            return api.user_update(params)
        elif method == 'users.get':
            return api.users_get(params)
        else:
            return 'Error: unsupported method'


if __name__ == '__main__':
    app.run(host=setting.URL_FLASK, port=11100, debug=True)
