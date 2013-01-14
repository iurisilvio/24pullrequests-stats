import os
import json
import time

import requests
import dateutil.parser

import settings


def _list_files(root, *childs):
    dir_ = os.path.join(root, *childs)
    for f in os.listdir(dir_):
        yield os.path.join(dir_, f)

def list_github_users(root):
    return _list_files(root, 'github', 'user')

def list_github_pullrequests(root):
    return _list_files(root, 'github', 'pullrequest')

def load_24pullrequests(page=1):
    print '24pullrequests page %d' % page
    url = 'http://24pullrequests.com/users.json?page=%d'
    response = requests.get(url % page)
    data = response.json()

    if data:
        next_page = load_24pullrequests(page + 1)
        data.extend(next_page)
    return data

def load_github_user(username, page=1, auth=None):
    print 'github/%s page %d' % (username, page)
    url = 'https://api.github.com/users/%s/events/public?page=%d'
    response = requests.get(url % (username, page), auth=auth)

    data = response.json()

    if isinstance(data, dict):
        print data
        print rate_limit(auth=auth)
        raise Exception(data)

    if not data:
        # TODO: raise exception?
        return []
    elif get_month(data[-1]) < 11:
        return [item for item in data if get_month(item) in [11, 12]]

    next_page = load_github_user(username, page + 1, auth=auth)
    data.extend(next_page)
    return data

def load_github_pullrequest(url, auth=None):
    response = requests.get(url, auth=auth)

    data = response.json()

    if not data:
        print rate_limit(auth=auth)
        raise Exception(data)

    return data

def pull_requests_without_data(root='data'):
    existent = set([os.path.basename(item).replace('.json', '')
        for item in list_github_pullrequests(root)])

    for f in list_github_users(root):
        with open(f) as ff:
            data = json.loads(ff.read())
            if not data: continue
            pullrequests = [item for item in data
                if item['type'] == 'PullRequestEvent' and
                    item['payload']['action'] == 'opened' and
                        '_'.join([item['payload']['pull_request']['base']['repo']['owner']['login'],
                            item['payload']['pull_request']['base']['repo']['name'],
                            str(item['payload']['pull_request']['id'])]) not in existent]
            for pr in pullrequests:
                yield pr

def users_without_github_data(root='data'):
    all_users = os.listdir(os.path.join(root, '24pullrequests'))
    try:
        github_loaded_users = os.listdir(os.path.join(root, 'github', 'user'))
        not_loaded = set(all_users) - set(github_loaded_users)
    except OSError:
        not_loaded = all_users

    return list(user.replace('.json', '') for user in not_loaded)

def get_month(data):
    d = dateutil.parser.parse(data['created_at'])
    return d.month

def save_data(basename, service, data, root='data'):
    _path = os.path.join(root, service)
    if not os.path.exists(_path):
        os.makedirs(_path)

    _file = os.path.join(_path, basename + '.json')
    with open(_file, 'w') as f:
        json.dump(data, f)

def save_github_user(username, data):
    save_data(username, 'github/user', data)

def save_github_pullrequest(data):
    filename = '_'.join([data['base']['repo']['owner']['login'], data['base']['repo']['name'], str(data['id'])])
    save_data(filename, 'github/pullrequest', data)

def save_24pullrequests_data(data):
    for item in data:
        save_data(item['nickname'], '24pullrequests', item)

def rate_limit(auth):
    url = 'https://api.github.com/rate_limit'
    response = requests.get(url, auth=auth)
    print response.json()


if __name__ == '__main__':
    rate_limit(settings.AUTH)

    for i, username in enumerate(users_without_github_data()):
        print '%d github/%s' % (i, username)
        data = load_github_user(username, auth=settings.AUTH)
        save_github_user(username,  data)

    for i, pr in enumerate(pull_requests_without_data()):
        url = pr['payload']['pull_request']['_links']['self']['href']
        print i, url
        data = load_github_pullrequest(url, auth=settings.AUTH)
        if data.get('message', '') == u'Not Found':
            print 'NOT FOUND', i, url
            continue

        save_github_pullrequest(data)
