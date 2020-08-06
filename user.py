import telegram as tg
from document import Document


class User():

    def __init__(self, tg_user: tg.User, language: str):

        self.tg_user = tg_user
        self.document = None
        self.language = language

    def append_document(self, document: Document):

        self.document = document

    def delete_document(self):

        if self.document is not None:

            self.document.delete_doc()
            self.document = None

    def change_language(self, language):

        self.language = language


class ListUsers(list):

    def get_user(self, username) -> User:

        for user in self:

            if username == user.tg_user.username:
                return user

    def delete_user(self, username):

        for index, user in enumerate(self):

            if username == user.tg_user.username:

                user.delete_document()

                return self.pop(index)
