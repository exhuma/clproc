# pylint: skip-file
"""
Application development tasks
"""
from invoke import Context, task  # type: ignore


@task  # type: ignore
def develop(ctx: Context):
    """
    Install the application in development mode
    """
    ctx.config.run.pty = True
    ctx.run("[ -d env ] || python3 -m venv env")
    ctx.run("env/bin/pip install --upgrade pip")
    ctx.run("env/bin/pip install -e .[dev,test]")
