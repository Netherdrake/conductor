import json
from os.path import expanduser

config_file = expanduser('~/.conductor.json')


def new_config():
    c = dict()
    c['witness'] = {
        'name': '',
        'url': 'https://steemdb.com/witnesses',
    }
    c['props'] = {
        'account_creation_fee': '0.500 STEEM',
        'maximum_block_size': 65536,
        'sbd_interest_rate': 0,
    }

    return c


def get_config():
    # todo check if our local config is current with blockchain state
    # as someone might have modified their witness without using conductor
    with open(config_file, 'r') as f:
        return json.loads(f.read())


def set_config(config: dict):
    with open(config_file, 'w') as f:
        f.write(json.dumps(config, indent=4))


def witness(prop: str):
    return get_config()['witness'][prop]


def props():
    return get_config()['props']


if __name__ == '__main__':
    conf = new_config()
    set_config(conf)
    print(dict(get_config()['props']))
