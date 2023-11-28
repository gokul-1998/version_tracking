v2 = {
    "dashboard": {
        "id": 1,
        "name": "Dashboard 1",
        "description": "This is the first dashboard",
        "pages": [
            {
                "id": 1,
                "name": "page 1",
                "dashboard_id": 1,
                "widgets": [
                    {
                        "id": 1,
                        "name": "widget 1 edited",
                        "page_id": 1
                    },
                    {
                        "id": 2,
                        "name": "widget 2",
                        "page_id": 1
                    }
                ]
            }
        ]
    }
}

import json
print(json.dumps(v2, indent=2))