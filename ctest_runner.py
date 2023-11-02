import yaml
import subprocess
import sys
from collections import OrderedDict

# Custom loader with OrderedDict
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

# Custom dumper to maintain order
def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

def update_yaml_hierarchy(file_path, hierarchy, value):
    # Load the existing YAML data from file
    with open(file_path, 'r') as file:
        data = ordered_load(file, yaml.SafeLoader)

    # Split the hierarchy input by dots to get the keys
    keys = hierarchy.split('.')

    # Traverse the data based on the hierarchy and set the value
    temp_data = data
    for key in keys[:-1]:
        temp_data = temp_data[key]

    temp_data[keys[-1]] = value

    # Write the modified data back to the file
    with open(file_path, 'w') as file:
        ordered_dump(data, file, Dumper=yaml.SafeDumper, default_flow_style=False)

def run_jest_test(test_case_path):
    print("Running the npx jest command")
    try:
        result = subprocess.run(['npx', 'jest', test_case_path], check=True)
        if result.returncode == 0:
            print("CTest PASS")
        else:
            print(f"CTest FAIL: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"CTest FAIL: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: script_name.py <yaml_file_path> <dot-separated hierarchy> <new value> <jest_test_case_path>")
        sys.exit(1)

    yaml_file_path = './config/' + sys.argv[1]
    hierarchy = sys.argv[2]
    value = sys.argv[3]

    # Try to convert value to int or float if possible
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass

    test_case_path = sys.argv[4]

    # Update YAML file
    update_yaml_hierarchy(yaml_file_path, hierarchy, value)

    # Run Jest test case
    run_jest_test(test_case_path)
