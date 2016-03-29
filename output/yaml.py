import yaml

def run(in_dict):
    return yaml.dump(in_dict, default_flow_style=False)