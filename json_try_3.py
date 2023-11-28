import json
from jsondiff import diff

def detect_changes(v2, v1):
    # Calculate the difference between v2 and v1
    difference = diff(json.loads(v1), json.loads(v2))

    # Separate the changes into untracked, modified, and deleted
    untracked = {key: value for key, value in difference.items() if key.startswith('_')}
    modified = {key: value for key, value in difference.items() if not key.startswith('_') and key in v1}
    deleted = {key: value for key, value in difference.items() if not key.startswith('_') and key not in v1}

    # Store the changes in a JSON object
    changes_json = {
        "untracked": untracked,
        "modified": modified,
        "deleted": deleted
    }

    return changes_json

def move_to_version(version, changes):
    def convert_keys(obj):
        if isinstance(obj, dict):
            return {str(key): convert_keys(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_keys(item) for item in obj]
        else:
            return obj

    changes = convert_keys(changes)

    # Apply the changes to the version to generate the previous version
    version_copy = version.copy()

    for key, value in changes["untracked"].items():
        version_copy[key] = value

    for key, value in changes["modified"].items():
        version_copy[key] = value

    for key in changes["deleted"]:
        if key in version_copy:
            del version_copy[key]

    return version_copy

# Example usage
v1 = {
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
                        "name": "widget 1",
                        "page_id": 1
                    }
                ]
            }
        ]
    }
}

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

changes = detect_changes(json.dumps(v2, indent=2),json.dumps(v1, indent=2))
print("gokul:")
print(changes)
v1_generated = move_to_version(v2, changes)

# Use custom encoder to handle non-JSON serializable keys
print("Changes:")
# print(json.dumps(changes, indent=2, default=str))
print("\nGenerated v1:")
print(json.dumps(v1_generated, indent=2, default=str))
