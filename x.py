v2={"dashboard": {"id": 1, "name": "Dashboard 1", "description": "This is the first dashboard", "pages": [{"id": 1, "name": "page 1", "dashboard_id": 1, "widgets": [{"id": 1, "name": "widget 1", "page_id": 1}]}]}}
v1=[{"op": "add", "path": "/dashboard", "value": {"id": 1, "name": "Dashboard 1", "description": "This is the first dashboard", "pages": [{"id": 1, "name": "page 1", "dashboard_id": 1, "widgets": [{"id": 1, "name": "widget 1", "page_id": 1}]}]}}]
import json
import jsonpatch

def apply_json_patch(original_json, json_patch):
    # Apply JSON Patch to the original JSON
    patched_json = jsonpatch.apply_patch(original_json, json_patch)
    return patched_json
# modified_json = apply_json_patch(v2, v1)
# print("\nModified JSON after applying the patch:")
# print(json.dumps(modified_json, indent=2))

def apply_patches(versions):
    print(versions)
    resp=versions[0]
    for version in versions[1:]:
        resp=apply_json_patch(resp,version)
        print(resp)
    return resp

x=apply_patches([v2,v1])
# print(json.dumps(x, indent=2))

