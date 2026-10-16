_USERS = {1: {"id": 1, "name": "ada"}, 2: {"id": 2, "name": "linus"}}


def fetch_user(uid):
    return dict(_USERS[uid])
