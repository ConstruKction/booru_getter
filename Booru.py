import os
import pathlib
import argparse
from datetime import datetime

from BooruRequest import BooruRequest
from Exclusion import Exclusion
from LocalImage import LocalImage
from BooruImage import BooruImage
from Tag import Tag

ILLEGAL_CHARACTERS = '<>:"/\\|?*.'
DATE = datetime.now().strftime('%Y_%m_%d')


def get_local_files(directory_path):
    filepath_list = []
    files = os.listdir(directory_path)
    for file in files:
        filepath_list.append(LocalImage(f"{directory_path}/{file}"))
    return filepath_list


def print_filename_exists_message(booru_image_filename, local_image_filename):
    if booru_image_filename != local_image_filename:
        print(f"{booru_image_filename} exists as {local_image_filename}")
    else:
        print(f"{booru_image_filename} exists")


def create_tag_object_list(tags_string, exclude):
    tag_object_list = []
    if tags_string is None:
        return tag_object_list

    for tag_value in tags_string.split(","):
        tag_object = Tag(tag_value, exclude)
        tag_object_list.append(tag_object)
    return tag_object_list


def sanitize(string):
    if 'None' in string:
        return string.replace('_None', '')

    for illegal_character in ILLEGAL_CHARACTERS:
        if illegal_character in string:
            return DATE

    return string.replace(',', '_')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tags', help='tags split by a comma (e.g. cute,vanilla)')
    parser.add_argument('-e', '--exclude', help='tags to exclude split by a comma')
    parser.add_argument('-c', '--count', help='amount of images desired, max 100', default=10, type=int)
    args = parser.parse_args()

    booru_request = BooruRequest(create_tag_object_list(args.tags, Exclusion.INCLUDED) +
                                 create_tag_object_list(args.exclude, Exclusion.EXCLUDED), args.count)

    target_directory_name = sanitize(f"{DATE}_{args.tags}")
    target_directory_path = f"{pathlib.Path().resolve()}/{target_directory_name}"

    try:
        os.makedirs(target_directory_name)
    except FileExistsError:
        print(f"{target_directory_name} directory exists, storing there")
        pass

    local_images = get_local_files(target_directory_name)

    for json_object in booru_request.get_json():
        booru_image = BooruImage(json_object)

        file_found = False

        for local_image in local_images:
            if local_image.hash == booru_image.hash:
                print_filename_exists_message(booru_image.filename, local_image.filename)
                file_found = True

        if file_found:
            continue

        booru_image.download(target_directory_path)
