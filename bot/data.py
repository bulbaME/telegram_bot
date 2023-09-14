import json
import os

def user_auth(user_name) -> bool:
    users = data_users_get()
    if user_name in users.keys() and users[user_name]['auth']:
        return True
    
    return False


def data_dir():
    if not os.path.isdir('data'):
        os.mkdir('data')

    if not os.path.isfile('data/users.json'):
        f = open('data/users.json', 'w')
        f.write('{}')
        f.close()

    if not os.path.isfile('data/sites.json'):
        f = open('data/sites.json', 'w')
        f.write('{}')
        f.close()

def data_users_get() -> dict:
    return json.load(open('data/users.json'))

def data_users_set(k, v):
    d = data_users_get()
    d[k] = v
    f = open('data/users.json', 'w')
    f.write(json.dumps(d))
    f.close()

def data_sites_get() -> dict:
    return json.load(open('data/sites.json'))

def data_sites_set(d):
    f = open('data/sites.json', 'w')
    f.write(json.dumps(d))
    f.close()

def data_sites_remove_group(g):
    d = data_sites_get()
    d.pop(g)

    data_sites_set(d)

def data_sites_add_group(g):
    d = data_sites_get()
    d[g] = {
        'cred': {
            'username': '',
            'password': ''
        },
        'list': []
    }

    data_sites_set(d)

def data_sites_append(g, v):
    d = data_sites_get()
    if not g in list(d.keys()):
        return
    
    d[g]['list'].append(v)
    d[g]['list'] = list(set(d[g]['list']))

    data_sites_set(d)

def data_sites_remove(g, v):
    d = data_sites_get()
    if not g in list(d.keys()):
        return
    
    try:
        d[g]['list'].remove(v)
    except BaseException:
        pass

    data_sites_set(d)
