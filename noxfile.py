import nox  # pylint: disable = import-error

from os.path import abspath, dirname
from shutil import rmtree


# https://nox.thea.codes/en/stable/ ############################################
#
# We advance from `pip install nox` for dev tasks. It also works on Windows and:
#
# 1. Supports multiple Python versions, each session can be ran on `pythonX.X`.
# 2. A single session is stored to a single virtualenv in .venv/<session_name>.
# 3. Each `nox` resets the session (venv), unless explicitly `reuse_venv=True`.
#
#
# What do you want to do? List all possible sessions (think as of tasks):
#
#   nox -l
#
# To go with sensible defaults (running tests) before submitting your PR:
#
#   nox
#
# You can also run only a session for acceptance testing with Robot Framework:
#
#   nox -s atest
#
# Using separate virtualenvs even for generating robot.libdoc is not a bad idea:
#
#   nox -s docs
#
# Remove all sessions (`.venv/`s) and remove temporary files in this directory:
#
#   nox -s clean
#
# This workflow is preferred for prereleasing to TestPyPI:
#
#   nox -s test atest docs clean build release_testpypi install_testpypi
#
# If that worked well, it should be fine to let the final release to PyPI:
#
#   nox -s release install
#
################################################################################

project_name = "RESTinstance"
package_name = "REST"
repo_root_path = dirname(abspath(__file__))

python = "3.6"

nox.options.envdir = ".venv"
nox.options.reuse_existing_virtualenvs = False
nox.options.stop_on_first_error = True

# The sensible default workflow
nox.options.sessions = ["test", "atest"]


@nox.session(python=python, venv_backend="venv", reuse_venv=True)
def test(session):
    """Run development tests for the package"""
    session.install("--upgrade", "-r", "requirements-dev.txt")
    session.run("pre-commit", "install")
    session.run("python", "-m", "unittest", "discover")
    session.run("pytest", "--last-failed", "--last-failed-no-failures", "all")


@nox.session(python=False)
def testenv(session):
    """Run development server for acceptance tests"""
    session.run(
        "npx",
        "mountebank",
        "start",
        "--localOnly",
        "--allowInjection",
        "--configfile",
        "testapi/apis.ejs",
    )


@nox.session(python=python, venv_backend="venv", reuse_venv=True)
def atest(session):
    """Run acceptance tests for the project"""
    session.install("--upgrade", "-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "robot",
        "-P",
        "src",
        "--outputdir",
        "results",
        "--xunit",
        "xunit.xml",
        "atest",
    )


@nox.session(python=python, venv_backend="venv", reuse_venv=True)
def docs(session):
    """Regenerate documentation for the project"""
    session.install("--upgrade", "-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "robot.libdoc",
        "-P",
        "src",
        package_name,
        "docs/index.html",
    )


@nox.session(python="3.6", venv_backend="venv", reuse_venv=True)
def black(session):
    """Reformat/unify/"blacken" Python source code in-place."""
    session.install("--upgrade", "black")
    session.run("black", ".")


@nox.session(python="3.6", venv_backend="venv", reuse_venv=True)
def prospector(session):
    """Run various static analysis tools for the package."""
    session.install(
        "--upgrade", "-r", "requirements.txt", "prospector[with_mypy]"
    )
    session.run("prospector", "--with-tool", "mypy")


@nox.session(python="3.6", venv_backend="venv")
def build(session):
    """Build sdist and wheel to dist/"""
    session.install("pip")
    session.install("setuptools")
    session.install("wheel")
    session.run("python", "setup.py", "bdist_wheel", "sdist")


@nox.session(python="3.6", venv_backend="venv")
def release_testpypi(session):
    """Publish dist/* to TestPyPI"""
    session.install("zest.releaser[recommended]")
    session.run("twine", "check", "dist/*")
    session.run(
        "twine",
        "upload",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "dist/*",
    )


@nox.session(python=python, venv_backend="venv")
def install_testpypi(session):
    """Install the latest (pre-)release from TestPyPI"""
    session.install(
        "--no-cache-dir",
        "--pre",
        "--index-url",
        "https://test.pypi.org/simple",
        "--extra-index-url",
        "https://pypi.org/simple",
        project_name,
    )


@nox.session(python="3.6", venv_backend="venv")
def release(session):
    """Tag, build and publish a new release to PyPI"""
    session.install("zest.releaser[recommended]")
    session.run("fullrelease")


@nox.session(python=python, venv_backend="venv")
def install(session):
    """Install the latest release from PyPI"""
    session.install("--no-cache-dir", project_name)


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files and caches in the directory"""
    rmtree("build", ignore_errors=True)
    rmtree("dist", ignore_errors=True)
    rmtree("pip-wheel-metadata", ignore_errors=True)
    rmtree("src/" + project_name + ".egg-info", ignore_errors=True)
    rmtree(".pytest_cache", ignore_errors=True)
    rmtree(".mypy_cache", ignore_errors=True)
    rmtree(".venv", ignore_errors=True)
    session.run(
        "python",
        "-c",
        "import pathlib;"
        + "[p.unlink() for p in pathlib.Path('%s').rglob('*.py[co]')]"
        % repo_root_path,
    )
    session.run(
        "python",
        "-c",
        "import pathlib;"
        + "[p.rmdir() for p in pathlib.Path('%s').rglob('__pycache__')]"
        % repo_root_path,
    )
