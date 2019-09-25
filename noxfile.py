"""
We use Nox (over `make`, `invoke`, `tox`, `pipenv`, `poetry` and `conda`):
1. Supports multiple Python versions, each session can be ran on `pythonX.X`.
2. A single session is stored in a single virtualenv in .venv/<session_name>.
3. Each `nox` resets the session (venv), unless explicitly `reuse_venv=True`.

Setup `nox` user-wide by `pip install --user --upgrade nox` - also on Windows.

What do you want to do then? List all possible sessions (think as of tasks):

   nox -l

To go with sensible defaults (running all tests) before submitting your PR:

    nox

You can also run only a session for acceptance testing with Robot Framework:

   nox -s atest

Using separate virtualenvs even for tasks like `-m robot.libdoc` is not bad:

   nox -s docs

Remove all sessions (`.venv/`s) and remove temporary files in source tree:

   nox -s clean

This workflow is preferred when (pre-)releasing a new version to TestPyPI:

   nox -s test atest docs clean build release_testpypi install_testpypi

If the above installed well, it'll be fine to let the final release to PyPI:

   nox -s release install
"""

from os.path import abspath, dirname
from shutil import rmtree

import nox  # pylint: disable = import-error


PROJECT_NAME = "RESTinstance"
PACKAGE_NAME = "REST"
REPO_ROOT_PATH = dirname(abspath(__file__))

PYTHON = "3.6"

nox.options.envdir = ".venv"
nox.options.reuse_existing_virtualenvs = False
nox.options.stop_on_first_error = True

# The sensible default workflow
nox.options.sessions = ["test", "atest"]


@nox.session(python=PYTHON, venv_backend="venv", reuse_venv=True)
def test(session):
    """Run development tests for the package."""
    session.install("--upgrade", "-r", "requirements-dev.txt")
    session.run("pre-commit", "install")
    session.run("python", "-m", "unittest", "discover")
    if session.posargs:
        pytest_args = session.posargs
    else:
        pytest_args = ("--last-failed", "--last-failed-no-failures", "all")
    session.run("pytest", *pytest_args)


@nox.session(python=False)
def testenv(session):
    """Run test environment for acceptance tests."""
    session.run("npm", "upgrade", "npm", "--no-save")
    session.run("npm", "install", "--no-save")
    session.run(
        "npm",
        "run",
        "mb_restart",
        "--",
        "--host",
        "127.0.0.1",
        "--localOnly",
        "true",
        "--ipWhitelist",
        "127.0.0.1",
        "--allowInjection",
        "--configfile",
        "testapi/apis.ejs",
    )


@nox.session(python=PYTHON, venv_backend="venv", reuse_venv=True)
def atest(session):
    """Run acceptance tests for the project."""
    session.install("--upgrade", "-r", "requirements.txt")
    if session.posargs:
        robot_args = session.posargs
    else:
        robot_args = ("--xunit", "xunit.xml", "atest")
    session.run(
        "python",
        "-m",
        "robot",
        "-P",
        "src",
        "--outputdir",
        "results",
        *robot_args
    )


@nox.session(python=PYTHON, venv_backend="venv", reuse_venv=True)
def docs(session):
    """Regenerate documentation for the project."""
    session.install("--upgrade", "-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "robot.libdoc",
        "-P",
        "src",
        PACKAGE_NAME,
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
    """Build sdist and wheel dists."""
    session.install("--no-cache-dir", "pip")
    session.install("--no-cache-dir", "setuptools")
    session.install("--no-cache-dir", "wheel")
    session.run("python", "setup.py", "bdist_wheel", "sdist")


@nox.session(python="3.6", venv_backend="venv")
def release_testpypi(session):
    """Publish dist/* to TestPyPI."""
    session.install("zest.releaser[recommended]")
    session.run("twine", "check", "dist/*")
    session.run(
        "twine",
        "upload",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "dist/*",
    )


@nox.session(python=PYTHON, venv_backend="venv")
def install_testpypi(session):
    """Install the latest (pre-)release from TestPyPI."""
    session.install(
        "--no-cache-dir",
        "--pre",
        "--index-url",
        "https://test.pypi.org/simple",
        "--extra-index-url",
        "https://pypi.org/simple",
        PROJECT_NAME,
    )


@nox.session(python="3.6", venv_backend="venv")
def release(session):
    """Tag, build and publish a new release to PyPI."""
    session.install("zest.releaser[recommended]")
    session.run("fullrelease")


@nox.session(python=PYTHON, venv_backend="venv")
def install(session):
    """Install the latest release from PyPI."""
    session.install("--no-cache-dir", PROJECT_NAME)


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files and caches in the directory."""
    rmtree("build", ignore_errors=True)
    rmtree("dist", ignore_errors=True)
    rmtree("node_modules", ignore_errors=True)
    rmtree("pip-wheel-metadata", ignore_errors=True)
    rmtree("src/" + PROJECT_NAME + ".egg-info", ignore_errors=True)
    rmtree(".mypy_cache", ignore_errors=True)
    rmtree(".pytest_cache", ignore_errors=True)
    rmtree(".venv", ignore_errors=True)
    session.run(
        "python3",
        "-c",
        "import pathlib;"
        + "[p.unlink() for p in pathlib.Path('%s').rglob('*.py[co]')]"
        % REPO_ROOT_PATH,
    )
    session.run(
        "python3",
        "-c",
        "import pathlib;"
        + "[p.rmdir() for p in pathlib.Path('%s').rglob('__pycache__')]"
        % REPO_ROOT_PATH,
    )
