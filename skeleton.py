import pytest
import setting
import actions
import web

if setting.FLASK_PYTEST_START_TYPE == "prepare_specific_case" and setting.FLASK_CASE is not None:
    web.flask_change_selected_qase_report_status("not active")  # deactivate reports
    actions.prepare_specific_case(setting.FLASK_CASE)  # prepare specific case
else:
    web.flask_change_selected_qase_report_status("active")  # deactivate reports
    actions.prepare_run(setting.FLASK_CASE)  # prepare run


@pytest.mark.parametrize('parameter', setting.QASE_TESTS, ids=setting.QASE_IDS)
def test_(parameter):

    for action_data in parameter:
        actions.choose_action(action_data)

    setting.DRIVER.browser_quit()  # close browser
