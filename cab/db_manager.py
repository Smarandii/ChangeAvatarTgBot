from create_db import User


class DBManager:
    def __init__(self, session):
        self.session = session

    def add_new_user(self, user: User):
        if self.session.get(User, user.chat_id) is None:
            self.session.add(user)
            self.session.commit()
            return False
        else:
            return True

    def get_user_from_db(self, user: User):
        user = self.session.get(User, user.chat_id)
        return user

    def update_or_add(self, user: User):
        if not self.get_user_from_db(user):
            self.session.add(user)
            self.session.commit()
        else:
            db_user = self.session.get(User, user.chat_id)
            db_user.phone = user.phone
            self.session.flush()
            self.session.commit()
        return user

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()