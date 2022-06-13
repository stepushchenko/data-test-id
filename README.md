# data-test-id framework

### About

Web application UI automated testing framework

### What is inside

1. Python 
2. Selenium
3. Selenoid
4. Pytest
5. Flask
6. QASE

### Environments

1. Different projects
2. Different project stages (dev, stg, prod and etc.)
3. Different browser versions

### What you need before first start

1. Create a QASE.io account with at least 2 test-cases
2. Add information about project, env and selenoid into the `setting.py` 
3. Add `data-test-id` attributes inside each HTML-element which you want to operate with

### How to run for the first time

1. Run your project (it should to be available at the address which you entered in `url_frontend`)
2. Open the data-test-id framework directory in the console
3. Run the `python3 server.py` command
4. Open the `http://localhost:11100/dashboard` to verify that the data-test-id dashboard is running
5. Open the `Cases` page
6. Press the `Run` button 

### Additional opportunities

1. Feel free to update web interface of the data-test-id framework in `web.py`
2. Feel free to create new python methods for operating with your project HTML-elements in `actions.py`
3. Feel free to add your project API methods in `api.py` for using them in preconditions and postconditions in `conftest.py`