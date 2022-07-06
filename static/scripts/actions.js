
//
//  GENERAL FUNCTIONS
//


function cases_get_table(suite_id) {

    document.getElementById('cases_select_suite_button_close').click();  // close popup
    document.getElementById('cases_get_table').innerHTML = '';  // clear table
    spinner_start('cases_get_table', 'spin2');  // start spinner

    var data = {
        'method': 'cases.get',
        'params': {}
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            spinner_stop('spin2');
            if (suite_id in result['result']['suites_with_autotests']) {

                // CREATE TITLE
                var title = document.createElement('div');
                title.id = 'h4_suite_title';
                title.innerHTML = ' ';
                title.setAttribute('style', 'padding-bottom: 15px;');
                title.setAttribute('class', 'text-secondary');
                document.getElementById('cases_get_table').appendChild(title);
                cases_get_suite_title(suite_id);

                // CREATE TABLE
                var table = document.createElement('table');
                table.setAttribute('class', 'table table-sm align-middle');
                document.getElementById('cases_get_table').appendChild(table);

                var thead = document.createElement('thead');
                table.appendChild(thead);

                var tr = document.createElement('tr');
                thead.appendChild(tr);

                var th = document.createElement('th');
                th.setAttribute('scope', 'col');
                th.innerHTML = 'ID';
                tr.appendChild(th);

                var th = document.createElement('th');
                th.setAttribute('scope', 'col');
                th.innerHTML = 'Title';
                tr.appendChild(th);

                var th = document.createElement('th');
                th.setAttribute('scope', 'col');
                th.innerHTML = 'Actions';
                tr.appendChild(th);

                var tbody = document.createElement('tbody');
                table.appendChild(tbody);

                // ADD ROWS
                var cases = result['result']['cases'];
                for (test_case in cases) {
                    if (cases[test_case]['suite_id'] == suite_id) {
                        var tr = document.createElement('tr');
                        tbody.appendChild(tr);

                        var td_id = document.createElement('td');
                        td_id.innerHTML = cases[test_case]['id'];
                        tr.appendChild(td_id);

                        var td_title = document.createElement('td');
                        td_title.innerHTML = cases[test_case]['title'];
                        tr.appendChild(td_title);

                        var td_actions = document.createElement('td');
                        tr.appendChild(td_actions);

                        // ADD ACTION BUTTONS
                        var button_run_onclick = 'case_run(' + cases[test_case]['id'] + ')';
                        var button_edit_onclick = 'case_update_modal(' + cases[test_case]['id'] + ')';

                        var button_run = document.createElement('button');
                        button_run.setAttribute('type', 'button');
                        button_run.setAttribute('class', 'btn btn-link');
                        button_run.setAttribute('onclick', button_run_onclick);
                        button_run.innerHTML = "Run";
                        td_actions.appendChild(button_run);
                    }
                }
            }
        }
    });
}


function cases_get_tables() {
    document.getElementById('cases_get_table').innerHTML = '';  // clear space
    spinner_start('cases_get_table', 'spin3');  // start spinner

    var data = {
        'method': 'cases.get',
        'params': {}
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            spinner_stop('spin3');  // stop spinner

            var suites = result['result']['suites_with_autotests'];
            for (suite in suites) {
                cases_get_table(suites[suite]);
            }
        }
    });
}


var chain = "";
function cases_get_suite_title(suite_id) {
    var data = {
        'method': 'suite.get',
        'params': {
            'suite_id': suite_id
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {

            chain = result['result']['title'] + ' &nbsp;&nbsp; ' + ' > ' + ' &nbsp;&nbsp; ' + chain;

            if (result['result']['parent_id'] !== null) {
                cases_get_suite_title(result['result']['parent_id']);
            } else {
                document.getElementById('h4_suite_title').innerHTML = chain;
            }
        }
    });
}


function case_run(case_id) {
    var data = {
        'method': 'case.run',
        'params': {
            'case_id': case_id
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            show_toast('Success: Case run started')
        }
    });
}


function plan_create() {
    var data = {
        'method': 'plan.create',
        'params': {
            'title': 'Automated tests'
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            console.log(result);
            show_toast('Success: Run created. Reload page!');
        }
    });
}


function page_change(page) {
    var data = {
        'method': 'user.update',
        'params': {
            'parameter': 'page',
            'value': page
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            console.log(result);
            location.href = '/dashboard';
        }
      });
}


function plan_delete(plan_id) {
    var data = {
        'method': 'plan.delete',
        'params': {
            'plan_id': plan_id
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            var element_id = 'plan_' + plan_id;
            document.getElementById(element_id).innerHTML = "";  // delete row
            show_toast('Success: Plan deleted')
        }
    });
}


function run_run(run_id) {
    var data = {
        'method': 'run.run',
        'params': {
            'run_id': run_id
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            show_toast('Success: Run started')
        }
    });
}


function run_get_report(run_id) {
    var data = {
        'method': 'run.get.report',
        'params': {
            'run_id': run_id
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            result = result['result'];
            var element_id = 'run_link_' + run_id;
            var element_id_2 = 'run_get_link_' + run_id;
            document.getElementById(element_id).setAttribute('href', result['report_link']);
            document.getElementById(element_id).setAttribute('style', '');
            document.getElementById(element_id_2).setAttribute('style', 'display:none;');
        }
    });
}


function suits_get(data) {

    spinner_start('suits_get', 'spin1')

    var data = {
        'method': 'suites.get',
        'params': {}
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {

            spinner_stop('spin1')

            ul = document.createElement('ul');
            ul.setAttribute('id','suits_get_ul')
            document.getElementById('suits_get').appendChild(ul);

            suites_get_prepare(result['result']['suites']);
        }
    });
}


var ul = Array();
var li = Array();
var span = Array();
function suites_get_prepare(suites) {
    for (suite in suites) { // get child elements
        var key = Object.keys(suites[suite])[0]
        var id = suites[suite][key]['data']['id'];
        var parent_id = suites[suite][key]['data']['parent_id'];
        var title = suites[suite][key]['data']['title'];
        if ('children' in suites[suite][key]) {
            var child = suites[suite][key]['children'];
        }
        else {
            var child = []
        }

        if (parent_id == 0) {  // parent == 0
            li[id] = document.createElement('li');
            li[id].setAttribute('style','list-style-type: none;');
            document.getElementById('suits_get_ul').appendChild(li[id]);

            var span_onclick = 'cases_get_table(' + id + ')';
            span[id] = document.createElement('span');
            span[id].innerHTML = title;
            span[id].setAttribute('onclick', span_onclick);
            span[id].setAttribute('class','text-secondary');
            span[id].setAttribute('style','cursor: pointer;');
            li[id].appendChild(span[id]);
        }
        else {  // parent != 0
            ul[id] = document.createElement('ul');
            ul[id].setAttribute('style', 'padding-left: 1rem;');
            li[parent_id].appendChild(ul[id]);

            li[id] = document.createElement('li');
            li[id].setAttribute('style','list-style-type: none;');
            ul[id].appendChild(li[id]);

            var span_onclick = 'cases_get_table(' + id + ')';
            span[id] = document.createElement('span');
            span[id].innerHTML = title;
            span[id].setAttribute('onclick', span_onclick);
            span[id].setAttribute('class','text-secondary');
            span[id].setAttribute('style','cursor: pointer;');
            li[id].appendChild(span[id]);
        }

        if (child.length != 0) {  // if child elements more than 0
            suites_get_prepare(child);  // start working with them
        }
    }
}


function user_logout() {
    window.localStorage.clear();
    page_change('logout');
}


function user_password_change() {
    var new_password = document.getElementById("user_password_change_newPassword").value;
    var new_password2 = document.getElementById("user_password_change_newPassword2").value;

    if (new_password.length < 3 || new_password2.length < 3) {
        show_toast('Error: Passwords must be at least 3 characters long');
        return ""
    }
    if (new_password != new_password2) {
        show_toast('Error: New passwords dont match');
        return ""
    }

    var data = {
        'method': 'user.password.change',
        'params': {
            'user_id': window.localStorage.getItem('user_id'),
            'password': new_password
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            show_toast('Success: Password changed');
            document.getElementById("user_password_change_close").click()
        }
    });
}


function user_sign_in() {
    document.getElementById("emailHelp").innerHTML = "";
    document.getElementById("passwordHelp").innerHTML = "";

    var email = document.getElementById("sign_in_email").value;
    var password = document.getElementById("sign_in_password").value;

    if (email.length < 3) {
        document.getElementById("emailHelp").innerHTML = "Email length must be at least 3";
        return "email failed"
    }
    if (password.length < 3) {
        document.getElementById("passwordHelp").innerHTML = "Password length must be at least 3";
        return "password failed"
    }

    var data = {
        'method': 'user.sign_in',
        'params': {
            'email': email,
            'password': password
        }
    }

    api_request(data).then(result => {
        if (result['status'] == 'success') {
            window.localStorage.setItem('user_id', result['result']['id']);  // save user_id to localStorage
            page_change('projects');
        }
    });
}


function user_sign_up() {
    document.getElementById("signUpEmailHelp").innerHTML = "";
    document.getElementById("signUpPassword1Help").innerHTML = "";
    document.getElementById("signUpPassword2Help").innerHTML = "";

    var email = document.getElementById("sign_up_email").value;
    var password = document.getElementById("sign_up_password1").value;
    var password2 = document.getElementById("sign_up_password2").value;

    if (email.length < 3) {
        document.getElementById("signUpEmailHelp").innerHTML = "Email length must be at least 3";
        return "email failed"
    }
    if (password.length < 3) {
        document.getElementById("signUpPassword1Help").innerHTML = "Password length must be at least 3";
        return "password failed"
    }
    if (password2.length < 3) {
        document.getElementById("signUpPassword2Help").innerHTML = "Password length must be at least 3";
        return "password failed"
    }
    if (password2 != password) {
        document.getElementById("signUpPassword2Help").innerHTML = "Passwords must be equal";
        return "password failed"
    }

    var data = {
        'method': 'users.get',
        'params': {}
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {

            var users = result['result']['users'];
            var users_count = users.length;

            if (users_count == 0) {
                var data = {
                    'method': 'user.sign_up',
                    'params': {
                        'email': email,
                        'password': password
                    }
                }
                api_request(data).then(result => {
                    if (result['status'] == 'success') {
                        window.localStorage.setItem('user_id', result['result']['id']);  // save user_id to localStorage
                        page_change('projects');
                    }
                });
            } else {
                show_toast('No more users can be added. Limit = 1.');
            }
        }
    });
}


function user_update_env() {
    var value = document.getElementById("env").value;
    var data = {
        'method': 'user.update',
        'params': {
            'parameter': 'env_id',
            'value': value
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            show_toast('Success: Env selected');
        }
    });
}


function user_update_project() {
    var value = document.getElementById("project").value;
    var data = {
        'method': 'user.update',
        'params': {
            'parameter': 'project_id',
            'value': value
        }
    }
    api_request(data).then(result => {  // save new PROJECT value
        if (result['status'] == 'success') {
            show_toast('Success: Project selected');

            var envs = result['result']['config']['envs'];  // get actual list of envs
            document.getElementById('env').innerHTML='';  // remove all options from ENV select

            for (env in envs) {
                var option = document.createElement('option');  // create new option
                option.value = envs[env]['id'];  // add value to the option
                option.innerHTML = envs[env]['title'];  // add text to the option
                document.getElementById('env').appendChild(option);  // add option to select
            }
        }
    });
}


function user_update_selenoid() {
    var value = document.getElementById("selenoid").value;
    var data = {
        'method': 'user.update',
        'params': {
            'parameter': 'selenoid_id',
            'value': value
        }
    }
    api_request(data).then(result => {
        if (result['status'] == 'success') {
            show_toast('Success: Selenoid selected')
        }
    });
}


//
//  SPECIAL FUNCTIONS
//


function show_toast(message) {
    var element = document.getElementById("toastShow");
    var toast = new bootstrap.Toast(element);
    document.getElementById('toastMessage').innerHTML = message;
    toast.show();
}


function api_request(data) {
    var fetchResult = fetch('http://localhost:11100/api', {
        method: 'POST',
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    return fetchResult.then(res => res.json());
}


function spinner_start(parent_element, delete_element) {
    var div_center = document.createElement('div');
    div_center.setAttribute('class', 'text-center');
    document.getElementById(parent_element).appendChild(div_center);

    var div_parent = document.createElement('div');
    div_parent.id = delete_element;
    div_center.appendChild(div_parent);

    var div_spinner = document.createElement('div');
    div_spinner.id = 'spinner';
    div_spinner.setAttribute('class', 'spinner-border m-5');
    div_spinner.setAttribute('role', 'status');
    div_parent.appendChild(div_spinner);

    var span_spinner = document.createElement('span');
    span_spinner.setAttribute('class', 'visually-hidden');
    span_spinner.innerHTML = 'Loading...';
    div_spinner.appendChild(span_spinner);
}


function spinner_stop(delete_element) {
    document.getElementById(delete_element).innerHTML = "";  // remove spinner
}
