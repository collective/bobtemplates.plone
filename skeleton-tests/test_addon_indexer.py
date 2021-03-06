# -*- coding: utf-8 -*-

from base import file_exists
from base import generate_answers_ini
from base import run_skeleton_tox_env

import os.path
import subprocess


def test_indexer(tmpdir, capsys, config):
    answers_init_path = os.path.join(tmpdir.strpath, "answers.ini")
    package_dir = os.path.abspath(tmpdir.strpath)
    template = """[variables]
package.description = Dummy package
package.example = True
package.git.init = True

author.name = The Plone Collective
author.email = collective@plone.org
author.github.user = collective

plone.version = {version}
""".format(
        version=config.version
    )
    generate_answers_ini(package_dir, template)

    # generate template addon:
    config.template = "addon"
    config.package_name = "collective.task"
    result = subprocess.call(
        [
            "mrbob",
            "-O",
            config.package_name,
            "bobtemplates.plone:" + config.template,
            "--config",
            answers_init_path,
            "--non-interactive",
        ],
        cwd=tmpdir.strpath,
    )
    assert result == 0

    wd = os.path.abspath(os.path.join(tmpdir.strpath, config.package_name))

    # generate subtemplate content_type:
    template = """[variables]
indexer_name = my_custom_test_indexer
subtemplate_warning = Yes
"""
    generate_answers_ini(package_dir, template)

    config.template = "indexer"
    result = subprocess.call(
        [
            "mrbob",
            "bobtemplates.plone:" + config.template,
            "--config",
            answers_init_path,
            "--non-interactive",
        ],
        cwd=wd,
    )
    assert result == 0

    assert file_exists(wd, "/src/collective/task/indexers/configure.zcml")
    assert file_exists(wd, "/src/collective/task/indexers/my_custom_test_indexer.zcml")
    assert file_exists(wd, "/src/collective/task/indexers/my_custom_test_indexer.py")

    with capsys.disabled():
        returncode = run_skeleton_tox_env(wd, config)
        assert returncode == 0, u"The tests inside the generated package are failing, please check the output above!"
