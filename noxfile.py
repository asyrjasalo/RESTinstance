import nox

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
# Remove all sessions (`./venv`s) and remove temporary files in this directory:
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

pythons = ["3.6"]

nox.options.envdir = ".venv"
nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = False
nox.options.stop_on_first_error = True

# The sensible default workflow
nox.options.sessions = ["test", "atest"]


@nox.session(reuse_venv=True)
def test(session):
    """Run (py)tests for the package (only failed if any, otherwise all)."""
    session.install("-r", "requirements-dev.txt")
    session.run("pre-commit", "install")
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


@nox.session(reuse_venv=True)
def atest(session):
    """Run Robot Framework acceptance tests for the package"""
    session.install("-r", "requirements.txt")
    session.run(
        "robot",
        "-P",
        "src",
        "--outputdir",
        "results",
        "--xunit",
        "xunit.xml",
        "atest",
    )


@nox.session()
def docs(session):
    """Regenerate library documentation for the package"""
    session.install(".")
    session.run("python", "-m", "robot.libdoc", package_name, "docs/index.html")


@nox.session()
def build(session):
    """Build source and wheel dist to dist/"""
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.run("python", "setup.py", "clean", "--all", "bdist_wheel", "sdist")


@nox.session()
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


@nox.session()
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


@nox.session()
def release(session):
    """Tag, build and publish a new release PyPI"""
    session.install("zest.releaser[recommended]")
    session.run("fullrelease")


@nox.session()
def install(session):
    """Install the latest release from PyPI"""
    session.install("--no-cache-dir", project_name)


@nox.session(python=False)
def clean(session):
    """Remove all .venv/s, remove builds, dists and caches in directory"""
    session.run(
        "rm",
        "-rf",
        "build",
        "dist",
        "src/" + project_name + ".egg-info",
        "__pycache__",
    )
    session.run("rm", "-rf", ".pytest_cache", ".mypy_cache")
    session.run("rm", "-rf", "pip-wheel-metadata")
    session.run("rm", "-rf", ".venv")
    session.run("rm", "-rf", "results")
    session.run("rm", "-f", "log.html", "output.xml", "report.html")
    session.run("rm", "-f", "mb.log", "mb1.log", "mb.pid")
