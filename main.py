import base64
import binascii
import json
import logging
import os
import shlex
import subprocess

import pykeepass
import tap

BASE64_ENDING = '_BASE64'


class ScriptArgumentParser(tap.Tap):
    keepass_file_path: str
    keepass_master_password: str
    keepass_group_filter: str


def is_entry_in_filter(keepass_group_filter: str, group_path: list[str]) -> bool:
    if keepass_group_filter == '':
        return True
    group_path_start_options = [x.split('/') for x in keepass_group_filter.split(',')]
    for group_path_start_option in group_path_start_options:
        if group_path_start_option == group_path[:len(group_path_start_option)]:
            return True
    return False


def augment_mappings(env_var_mappings: dict[str, str]) -> dict[str, str]:
    augmented_env_var_mappings = {}
    for name, value in env_var_mappings.items():
        augmented_env_var_mappings[name] = value
        if name.endswith(BASE64_ENDING):
            decoded_name = name[:-len(BASE64_ENDING)]
            try:
                decoded_value = base64.b64decode(value).decode('utf-8')
            except (binascii.Error, UnicodeDecodeError):
                continue
            augmented_env_var_mappings[decoded_name] = decoded_value
    return augmented_env_var_mappings


def get_env_var_mappings(
        keepass_file_path: str, keepass_master_password: str, keepass_group_filter: str) -> dict[str, str]:
    keepass_database = pykeepass.PyKeePass(keepass_file_path, password=keepass_master_password)
    logging.info(f'successfully opened the keepass file at location "{os.path.abspath(keepass_file_path)}"')
    filtered_entries = [entry for entry in keepass_database.entries
                        if is_entry_in_filter(keepass_group_filter, entry.group.path) and
                        not contains_whitespace(entry.title) and
                        not contains_equal_sign(entry.title)]
    env_var_mappings = {entry.title: entry.password for entry in filtered_entries}
    augmented_env_var_mappings = augment_mappings(env_var_mappings)
    return augmented_env_var_mappings


def get_environment_file_path() -> str:
    return os.environ['GITHUB_ENV']


def contains_whitespace(value: str) -> bool:
    return any([x.isspace() for x in value])


def contains_equal_sign(value: str) -> bool:
    return '=' in value


def set_environment_value(name: str, value: str) -> None:
    logging.info(f'setting "{name}" in the environment')
    subprocess.run([f'echo "{name}<<EOF" >> {get_environment_file_path()}'], shell=True, check=True)
    subprocess.run([f'echo {shlex.quote(value)} >> {get_environment_file_path()}'], shell=True, check=True)
    subprocess.run([f'echo "EOF" >> {get_environment_file_path()}'], shell=True, check=True)
    subprocess.run([f'echo "::add-mask::{shlex.quote(value)}"'], shell=True, check=True)


def set_mappings_in_env_vars(env_var_mappings: dict[str, str]) -> None:
    for name, value in env_var_mappings.items():
        set_environment_value(name, value)


def save_mappings_to_file(env_var_mappings: dict[str, str]) -> None:
    with open('env.json', 'w') as file:
        json.dump(env_var_mappings, file, ensure_ascii=False, allow_nan=False, sort_keys=True)


def main() -> None:
    args = ScriptArgumentParser().parse_args()
    env_var_mappings = get_env_var_mappings(
        args.keepass_file_path, args.keepass_master_password, args.keepass_group_filter)
    set_mappings_in_env_vars(env_var_mappings)
    save_mappings_to_file(env_var_mappings)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
