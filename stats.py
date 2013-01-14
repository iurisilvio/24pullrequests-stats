from __future__ import division
import os
import itertools
import json

import dateutil.parser

def _list_files(root, *child):
    dir_ = os.path.join(root, *child)
    for f in os.listdir(dir_):
        yield os.path.join(dir_, f)

def list_github_files(root='data'):
    return _list_files(root, 'github', 'user')

def list_24pullrequests_files(root='data'):
    return _list_files(root, '24pullrequests')

_cache_pr = None

def get_all_github_pr():
    global _cache_pr
    if not _cache_pr:
        _cache_pr = []
        f = lambda x: x['type'] == 'PullRequestEvent'
        data = (_load_json_file(x) for x in list_github_files())
        for item in data:
            if not item: continue
            _cache_pr.extend(filter(f, item))
    return _cache_pr

def get_date(data):
    return dateutil.parser.parse(data['created_at'])

def get_month(data):
    return get_date(data).month

def get_day(data):
    return get_date(data).day

def _get_user(filename):
    return filename.split('/')[-1].replace('.json', '')

def all_developers():
    all_files = list_24pullrequests_files()
    return list(all_files)

def _load_json_file(filename):
    with open(filename) as f:
        return json.loads(f.read())

def active_developers():
    return filter(lambda x: _load_json_file(x)['pull_requests_count'] > 0, list_24pullrequests_files())

def pullrequests(month):
    return [item for item in get_all_github_pr() if get_month(item) == month and item['payload']['action'] == 'opened']

def merged_pullrequests(month):
    merged_file = os.path.join('data', 'github', 'merged.txt')
    with open(merged_file) as f:
        merged = set(f.read().split('\n'))
    all_ = pullrequests(month)
    return [item for item in all_
        if '_'.join([item['payload']['pull_request']['base']['repo']['owner']['login'],
            item['payload']['pull_request']['base']['repo']['name'],
            str(item['payload']['pull_request']['id'])]) in merged]

def pullrequests_per_day(month):
    data = pullrequests(month)
    result = [(group[0], len(list(group[1])))
        for group in itertools.groupby(sorted(data, key=get_day), key=get_day)]
    return result

def pullrequests_per_developer(month):
    data = pullrequests(month)
    f = lambda x: x['payload']['pull_request']['user']['login']
    result = [(group[0], len(list(group[1])))
        for group in itertools.groupby(sorted(data, key=f), key=f)]
    return list(sorted(result, key=lambda x: x[1], reverse=True))

def pullrequests_per_project(month):
    data = pullrequests(month)
    f = lambda x: x['payload']['pull_request']['base']['repo']['name']
    result = [(group[0], len(list(group[1])))
        for group in itertools.groupby(sorted(data, key=f), key=f)]
    return list(sorted(result, key=lambda x: x[1], reverse=True))

def merged_pullrequests_per_developer(month):
    data = merged_pullrequests(month)
    f = lambda x: x['payload']['pull_request']['user']['login']
    result = [(group[0], len(list(group[1])))
        for group in itertools.groupby(sorted(data, key=f), key=f)]
    return list(sorted(result, key=lambda x: x[1], reverse=True))

def group_by_month(data):
    return dict((group[0], list(group[1]))
        for group in itertools.groupby(data, key=get_month) if group[0] in [11, 12])

if __name__ == '__main__':

    print 'Total developers: %d' % len(all_developers())
    print 'Active developers: %d' % len(active_developers())
    print 'Total pull requests in december: %d' % len(pullrequests(12))
    print 'Total pull requests in november: %d' % len(pullrequests(11))
    print 'Merged pull requests in december: %d' % len(merged_pullrequests(12))
    print 'Merged pull requests in november: %d' % len(merged_pullrequests(11))
    print 'Total projects in december: %d' % len(merged_pullrequests(11))
    print 'Pull requests/project in december: %s' % pullrequests_per_project(12)
    print 'Pull requests/project in november: %s' % pullrequests_per_project(11)
    print 'Pull requests/day in december: %s' % pullrequests_per_day(12)
    print 'Pull requests/day in november: %s' % pullrequests_per_day(11)
    print 'Pull requests/developer in december: %s' % pullrequests_per_developer(12)
    print 'Pull requests/developer in november: %s' % pullrequests_per_developer(11)
    print 'Merged pull requests/developer in december: %s' % merged_pullrequests_per_developer(12)
    print 'Merged pull requests/developer in november: %s' % merged_pullrequests_per_developer(11)