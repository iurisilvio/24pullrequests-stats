import os
import json


def _list_files(root, *childs):
    dir_ = os.path.join(root, *childs)
    for f in os.listdir(dir_):
        yield os.path.join(dir_, f)

def list_github_pullrequests(root):
    return _list_files(root, 'github', 'pullrequest')

merged_file = os.path.join('data', 'github', 'merged.txt')

with open(merged_file, 'w') as m:
    for f in list_github_pullrequests('data'):
        with open(f) as ff:
            data = json.loads(ff.read())
            if data['merged']:
                m.write(os.path.basename(f).replace('.json', '') + '\n')
