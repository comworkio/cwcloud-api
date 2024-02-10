from entities.User import User

def get_user_email(id, db):
    user = User.getUserById(int(id), db)
    if user:
        return user.email
    
    return None

def get_owner_email(payload, db):
    return get_user_email(payload.owner_id, db)

def get_invoker_email(payload, db):
    return get_user_email(payload.invoker_id, db)
