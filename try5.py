import json
from deepdiff import DeepDiff

class MyObject:
    def __init__(self, prop1, prop2, prop3=None):
        self.prop1 = prop1
        self.prop2 = prop2
        self.prop3 = prop3

def apply_differences(old_obj, differences):
    for key, change in differences.items():
        if 'new_value' in change and 'old_value' in change:
            if hasattr(old_obj, key):
                setattr(old_obj, key, change['old_value'])

def find_differences(old_obj, new_obj):
    diff = DeepDiff(old_obj.__dict__, new_obj.__dict__)
    return diff

# Example usage
old_obj = MyObject(prop1=1, prop2='A', prop3=True)
new_obj = MyObject(prop1=2, prop2='B')

differences = find_differences(old_obj, new_obj)
print(differences)

# Save differences to the database
# (Database insertion code here)

# Later, when you want to reconstruct the old object
# (Database retrieval code here)

retrieved_row = {
    'differences': differences
}
retrieved_differences = retrieved_row['differences']

# Reconstruct the old object
reconstructed_obj = MyObject(prop1=new_obj.prop1, prop2=new_obj.prop2, prop3=new_obj.prop3)
apply_differences(reconstructed_obj, retrieved_differences)

# Now, reconstructed_obj should be the original object (obj1)
print(reconstructed_obj.__dict__)
