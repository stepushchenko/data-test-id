import os.path

FOLDER_ROOT = os.path.dirname(os.path.realpath(__file__))
SLEEP = 0.5
PATH = 'repos/yourcoach/test_ui'
URL_FLASK = 'localhost'
URL_API = 'http://localhost:11100/api'

URL_SELENOID = 'http://localhost:4444/wd/hub'
USER_ID = 0
DRIVER = ""

SUITS = [
    {
        "id": 112,
        "title": "Web-app",
        "parent_id": 0,
        "children": [
            {
                "id": 326,
                "title": "Unit",
                "parent_id": 112,
                "children": [
                    {
                        "id": 1,
                        "title": "Sign up",
                        "parent_id": 326,
                        "children": []
                    },
                    {
                        "id": 353,
                        "title": "Profile",
                        "parent_id": 326,
                        "children": [
                            {
                                "id": 361,
                                "title": "Create",
                                "parent_id": 353,
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Practice",
                        "parent_id": 326,
                        "children": [
                            {
                                "id": 354,
                                "title": "Create",
                                "parent_id": 4,
                                "children": []
                            },
                            {
                                "id": 355,
                                "title": "Update",
                                "parent_id": 4,
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    }
]
