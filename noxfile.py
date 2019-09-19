import nox
import shutil

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
# This workflow is what is preferred for prereleasing to TestPyPI:
#
#   nox -s test atest docs build release_testpypi install_testpypi
#
# If that worked well, it should be fine to let the final release go to PyPI:
#
#   nox -s test atest docs build release install
#
#
################################################################################

project_name = "RESTinstance"
package_name = "REST"

python = "3.6"

nox.options.envdir = ".venv"
nox.options.reuse_existing_virtualenvs = False
nox.options.stop_on_first_error = True

# The sensible default workflow
nox.options.sessions = ["test", "atest"]


@nox.session(python=python, venv_backend="venv", reuse_venv=True)
def test(session):
    """Run unittest and pytest tests"""
    session.install("-r", "requirements-dev.txt")
    session.run("pre-commit", "install")
    session.run("python", "-m", "unittest", "discover")
    session.run("pytest", "--last-failed", "--last-failed-no-failures", "all")


@nox.session(python=False)
def testenv(session):
    """Start a local test environment for acceptance tests"""
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
    """Run Robot Framework acceptance tests"""
    session.install("-r", "requirements.txt")
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
    """Regenerate library documentation"""
    session.install("-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "robot.libdoc",
        "-P",
        "src",
        package_name,
        "docs/index.html",
    )


@nox.session(python="3.6", venv_backend="venv")
def build(session):
    """Build sdist and wheel to dist/"""
    session.install("pip")
    session.install("setuptools")
    session.install("wheel")
    session.run("python", "setup.py", "clean", "--all", "bdist_wheel", "sdist")


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
    """Tag, build and publish a new release PyPI"""
    session.install("zest.releaser[recommended]")
    session.run("fullrelease")


@nox.session(python=python, venv_backend="venv")
def install(session):
    """Install the latest release from PyPI"""
    session.install("--no-cache-dir", project_name)


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files, caches and testenv logs"""
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("pip-wheel-metadata", ignore_errors=True)
    shutil.rmtree("src/" + project_name + ".egg-info", ignore_errors=True)
    shutil.rmtree("__pycache__", ignore_errors=True)
    shutil.rmtree(".pytest_cache", ignore_errors=True)
    shutil.rmtree(".mypy_cache", ignore_errors=True)
    shutil.rmtree(".venv", ignore_errors=True)
