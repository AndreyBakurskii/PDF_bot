from telegram import File
import img2pdf
import os
import shutil
import re


class Document():

    def __init__(self, username, filename):

        self.username = username
        self.filename = filename

        self.amount_of_photo = 0
        self.index_of_photo = 0
        self.photo_to_convert = []

        self.path_to_directory = self.path2dir(username)
        self.path_to_document = self.path2doc(self.path_to_directory, filename)

    def get_amount_of_photo(self, value):

        self.amount_of_photo += value

    def get_photo(self, photo: File):

        extension_of_photo = photo.file_path[photo.file_path.rfind(".")::].lower()

        name_photo = f"ph{self.index_of_photo}"

        path = self.path_to_directory + name_photo + extension_of_photo

        photo.download(custom_path=path)
        self.photo_to_convert.append(path)

        self.index_of_photo += 1

        if self.index_of_photo == self.amount_of_photo:

            return True

        else:
            return False

    def path2dir(self, username):

        # create user directory
        path_to_directory = f"./{username}/"

        if not os.path.exists(path_to_directory):
            os.mkdir(path_to_directory)

        return path_to_directory

    def path2doc(self, path_to_directory, filename):

        # create path to document
        path_to_document = path_to_directory + f"{filename}.pdf"

        return path_to_document

    def delete_doc(self):

        shutil.rmtree(self.path_to_directory)


class Documents(list):

    def get_document(self, username) -> Document or None:

        for doc in self:

            if doc.username == username:

                return doc

        return None

    def delete_document(self, username):

        for index, doc in enumerate(self):

            if doc.username == username:

                doc.delete_doc()

                return self.pop(index)


def check_filename(filename: str) -> bool:

    pattern = r"[<>|/\:*?\"]"

    if re.search(pattern, filename) is None:
        return True

    else:
        return False


def check_amount_of_photo(value: str) -> bool:

    try:
        value = int(value)
    except ValueError:
        return False

    return True


def convert2pdf(document: Document):

    with open(document.path_to_document, "wb+") as pdf_file:
        pdf_file.write(img2pdf.convert(document.photo_to_convert))

    return document.path_to_document
