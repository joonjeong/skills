from app import repo
from app.service import display_name


def get(uid):
    user = repo.fetch_user(uid)
    return {"user": user, "label": display_name(uid)}
