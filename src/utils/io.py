import json 
def read_file(file_path):
    with open(file_path) as f:
        return f.readlines()
def read_json(file_path):
    with open(file_path) as f:
        return json.load(f)