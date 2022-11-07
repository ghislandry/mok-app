from pybuilder.core import use_plugin, init, task, os
from git import Repo

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("pypi:pybuilder_pytest")
use_plugin("pypi:pybuilder_pytest_coverage")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("exec")


default_task = ["install_dependencies", "run_unit_tests"]


@init
def initialize(project):
    os.environ["PYTHONPATH"] = "./src:$PYTHONPATH"
    project.set_property("dir_source_unittest_python", "tests")
    project.set_property("unittest_module_glob", "test_*")
    project.get_property("pytest_extra_args").append("-x")


@init
def set_properties(project):
    project.set_property("dir_source_pytest_python", "tests")
    project.set_property("dir_source_main_python", "src")
    project.set_property("dir_source_unittest_python", "tests")
    project.set_property("unittest_module_glob", "test_*")

    project.set_property(
        "run_unit_tests_command",
        f"pytest {project.expand_path('$dir_source_unittest_python')}",
    )
    project.set_property("run_unit_tests_propagate_stdout", True)
    project.set_property("run_unit_tests_propagate_stderr", True)
    project.set_property("teamcity_output", True)


@task
def sonar():
    repo = Repo(os.getcwd())
    branch = repo.active_branch
    print("Current branch is", branch.name)

    os.system(
        "pyb & sonar-scanner -Dsonar.branch.target=development -Dsonar.branch.name="
        + branch.name
    )
