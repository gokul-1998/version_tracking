import json
import jsonpatch

def generate_json_patch(old_json, new_json):
    # Generate JSON Patch
    patch = jsonpatch.make_patch(old_json, new_json)
    return patch

def apply_json_patch(original_json, json_patch):
    # Apply JSON Patch to the original JSON
    patched_json = jsonpatch.apply_patch(original_json, json_patch)
    return patched_json

# Example JSON objects
original_json = {
    "name": "Alice",
    "age": 25,
    "address": {
        "city": "Wonderland",
        "country": "Fantasyland"
    }
}

new_json = {
    "name": "Alice",
    "age": 26,
    "phone": "123-456-7890",
    "address": {
        "city": "Wonderland",
        "country": "Fantasyland"
    }
}

# Generate JSON Patch
json_patch = generate_json_patch(original_json, new_json)

# Apply JSON Patch to get the modified JSON
modified_json = apply_json_patch(original_json, json_patch)

# Print results
print("Original JSON:")
print(json.dumps(original_json, indent=2))

print("\nNew JSON:")
print(json.dumps(new_json, indent=2))

print("\nGenerated JSON Patch:")
print(json_patch)

print("\nModified JSON after applying the patch:")
print(json.dumps(modified_json, indent=2))
