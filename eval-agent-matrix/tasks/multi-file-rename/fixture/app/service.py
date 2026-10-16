from app.repo import fetch_user


def display_name(uid):
    return fetch_user(uid)["name"].title()
