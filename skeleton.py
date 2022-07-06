import pytest
import setting
import actions

if actions.user('case_id') > 0:
    actions.user_update("report", "not active")  # deactivate reports
    actions.prepare_case(actions.user('case_id'))  # prepare specific case
elif actions.user('run_id') > 0:
    actions.user_update("report", "active")  # activate reports
    actions.prepare_run(actions.user('run_id'))  # prepare run


@pytest.mark.parametrize('parameter', actions.user('qase_cases'), ids=actions.user('qase_ids'))
def test_(parameter):

    for action_data in parameter:
        actions.choose_action(action_data)

    setting.DRIVER.browser_quit()  # close browser
