

def get_user_name(user) -> str:
    name = user.full_name
    if not name:
        name = f'{user.last_name} {user.first_name}'
    elif not name:
        name = user.username
    elif not name:
        name = user.id

    return name