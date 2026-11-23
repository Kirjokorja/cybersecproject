from django.template import Context, Engine
from django.views.debug import ExceptionReporter

# Minimal Django templates engine to render the error templates
# regardless of the project's TEMPLATES setting. Templates are
# read directly from the filesystem so that the error handler
# works even if the template loader is broken.
DEBUG_ENGINE = Engine(
    debug=True,
    libraries={"i18n": "django.templatetags.i18n"},
)

class AdminExceptionReporter(ExceptionReporter):
    """Organize and coordinate reporting on exceptions."""

    def get_traceback_text(self):
        """Return plain text version of debug 500 HTTP error page."""
        with self.text_template_path.open(encoding="utf-8") as fh:
            t = DEBUG_ENGINE.from_string(fh.read())
        c = Context(self.get_traceback_data(), autoescape=False, use_l10n=False)
        return t.render(c)
