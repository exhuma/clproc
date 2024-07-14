# pylint: skip-file
"""
Application development tasks
"""
from invoke import task


@task
def develop(ctx):
    """
    Install the application in development mode
    """
    ctx.config.run.pty = True
    ctx.run("[ -d env ] || python3 -m venv env")
    ctx.run("env/bin/pip install --upgrade pip")
    ctx.run("env/bin/pip install -e .[dev,test]")
