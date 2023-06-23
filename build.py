#!/usr/bin/env python

import os
import sys
from contextlib import contextmanager

from conans.client import conan_api
from cpt.packager import ConanMultiPackager


@contextmanager
def chdir(new_dir):
    cwd = os.getcwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(cwd)


def inspect_value_from_recipe(attribute, recipe_path):
    dir_name = os.path.dirname(recipe_path) or "./"
    with chdir(dir_name):
        conan_instance, _, _ = conan_api.Conan.factory()
        inspect_result = conan_instance.inspect(path=os.path.basename(recipe_path), attributes=[attribute])
        result = inspect_result.get(attribute)
        return result


def get_repo_branch_from_githubaction():
    branch = os.getenv("GITHUB_REF", "")
    if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
        return os.getenv("GITHUB_BASE_REF", "")
    elif branch.startswith("refs/heads/"):
        return branch[11:]
    else:
        return branch


def has_shared_option(recipe_path):
    options = inspect_value_from_recipe(attribute="options", recipe_path=recipe_path)
    return options and "shared" in options


if __name__ == "__main__":
    recipe_path = os.path.abspath("conanfile.py")
    recipe_name = inspect_value_from_recipe(attribute="name", recipe_path=recipe_path)
    if len(sys.argv) > 1:
        recipe_version = sys.argv[1]
    else:
        branch = get_repo_branch_from_githubaction()
        recipe_version = branch.rsplit("/")[-1]
    reference = f"{recipe_name}/{recipe_version}"
    shared_option_name = f"{recipe_name}:shared" if has_shared_option(recipe_path) else None

    builder = ConanMultiPackager(
        build_policy="missing",
        skip_check_credentials=True,
        docker_run_options="-u 0:0",
    )
    builder.add_common_builds(
        shared_option_name=shared_option_name,
        pure_c=False,
        dll_with_static_runtime=True,
        reference=reference,
        build_all_options_values=None,
    )
    builder.run()
