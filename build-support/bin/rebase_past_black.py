# Copyright 2019 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).


import argparse
import subprocess
import sys

from appdirs import user_cache_dir
from common import git_merge_base

# TODO: would be nice to avoid hardcoding this
BLACK_VERSION = "19.10.b0"
CACHE_DIR = Path(user_cache_dir("black", version=BLACK_VERSION))

# TODO: if black not installed or at incorrect version, warn and exit
def check_black_version():

# TODO: show command to user and let them confirm it
def confirm_remove_command():

# TODO: flag dirty git state. Recommend stashing changes
def detect_dirty_git_repo():

# TODO
def git_pull():

# TODO: fail if branch doesn't exist
def check_branch(branch: str):

# TODO: must be root of pants repo. ./pants must work
def check_directory():

# TODO: detect broken pants
def check_pants():

def format_files(file_list: str):
    black_command = ["black", f"{file_list}"]
    process = subprocess.run(black_command)
    if process.exit_code != 0:
        System.exit process.exit_code

    # TODO: make them confirm before running this command
    clean_cache = ["rm", f"{CACHE_DIR}/cache*.pickle"]
    process = subprocess.run(clean_cache)

    fix_multiline = ["./pants", "run",  "build-support/bin:fix_multiline_strings_after_black", "--", file_list, "--fast"]
    process = subprocess.run(fix_multiline)

def git_branch() -> str:
    get_tracking_branch = [
        "git",
        "rev-parse",
        "--symbolic-full-name",
        "--abbrev-ref",
        "HEAD@{upstream}",
    ]
    process = subprocess.run(
        get_tracking_branch, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
    )
    return str(process.stdout.rstrip()) if process.stdout else "master"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Formats all python files since master with black through pants.",
    )
    parser.add_argument(
        "-b",
        "--branch",
        action="store_true",
        help="Instead of erroring on files with incorrect formatting, fix those files.",
    )
    return parser


def main() -> None:
    args = create_parser().parse_args()
    merge_base = git_merge_base()
    goal = "fmt-v2" if args.fix else "lint-v2"
    command = ["./pants", f"--changed-parent={merge_base}", goal]
    process = subprocess.run(command)
    sys.exit(process.returncode)


if __name__ == "__main__":
    main()
