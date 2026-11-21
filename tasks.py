from invoke import task
from sys import platform

@task
def lint(ctx):
    if platform == "win32":
        ctx.run(
            "pylint --load-plugins pylint_django " \
            "--django-settings-module=flawedsite.settings src/flawedsite")
    else:
        ctx.run(
            "pylint --load-plugins pylint_django " \
            "--django-settings-module=flawedsite.settings src/flawedsite", pty=True)
