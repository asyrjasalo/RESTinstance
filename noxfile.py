"""
In addition to Nox, we use a lot of "classics" (as of 2024), like setuptools, twine and zest.releaser. This likely changes for Python 3.13+...
"""

from os.path import abspath, dirname
from shutil import rmtree

import nox  # pylint: disable = import-error


PROJECT_NAME = "RESTinstance"
PACKAGE_NAME = "REST"
REPO_ROOT_PATH = dirname(abspath(__file__))

nox.options.envdir = ".venv"
nox.options.reuse_existing_virtualenvs = False
nox.options.stop_on_first_error = True

# The default workflow
nox.options.sessions = ["test", "atest"]


@nox.session(venv_backend="venv", reuse_venv=True)
def test(session):
    """Run development tests for the package."""
    session.install("--no-cache-dir", "setuptools")
    session.install("--upgrade", "-r", "requirements-dev.txt")
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


@nox.session(venv_backend="venv", reuse_venv=True)
def atest(session):
    """Run acceptance tests for the project."""
    session.install("--no-cache-dir", "setuptools")
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


@nox.session(venv_backend="venv", reuse_venv=True)
def docs(session):
    """Regenerate documentation for the project."""
    session.install("--no-cache-dir", "setuptools")
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


@nox.session(venv_backend="venv", reuse_venv=True)
def black(session):
    """Reformat Python source code in-place."""
    session.install("--upgrade", "black")
    session.run("black", ".")


@nox.session(venv_backend="venv")
def build(session):
    """Build sdist and wheel dists."""
    session.install("--no-cache-dir", "pip")
    session.install("--no-cache-dir", "setuptools")
    session.install("--no-cache-dir", "wheel")
    session.run("python", "setup.py", "bdist_wheel", "sdist")


@nox.session(venv_backend="venv")
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


@nox.session(venv_backend="venv")
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


@nox.session(venv_backend="venv")
def release(session):
    """Tag, build and publish a new release to PyPI."""
    session.install("zest.releaser[recommended]")
    session.run("fullrelease")


@nox.session(venv_backend="venv")
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
        "python",
        "-c",
        "import pathlib;"
        + "[p.unlink() for p in pathlib.Path('%s').rglob('*.py[co]')]"
        % REPO_ROOT_PATH,
    )
    session.run(
        "python",
        "-c",
        "import pathlib;"
        + "[p.rmdir() for p in pathlib.Path('%s').rglob('__pycache__')]"
        % REPO_ROOT_PATH,
    )
