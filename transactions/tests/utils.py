from os import path

from django.contrib.auth import get_user_model

User = get_user_model()


def open_test_file(file_name):
    current_dir = path.dirname(__file__)
    fixture_dir = path.join(current_dir, 'data')
    file_path = path.join(fixture_dir, file_name)
    return open(file_path, 'r')
