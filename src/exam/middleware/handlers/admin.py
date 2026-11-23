import warnings

from copy import copy
from django.conf import settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import RemovedInDjango2028Warning, django_file_prefixes
from django.utils.log import AdminEmailHandler
from django.utils.module_loading import import_string
from exam.middleware.loggers import ExceptionDbLogger as default_logger

class SafeAdminHandler(AdminEmailHandler):
    """An exception log handler that emails log entries to site admins.

    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.
    """
    def __init__(
        self,
        db_logger=default_logger,
        include_html=False,
        email_backend=None,
        reporter_class=None,
        using=None
    ):
        self._db_logger = db_logger
        super().__init__()

        # RemovedInDjango2028Warning: email_backend arg and connection error.
        if email_backend:
            if using:
                raise ImproperlyConfigured(
                    "The 'email_backend' argument is not compatible with 'using'."
                )
            if mail.mailers._is_configured:
                raise ImproperlyConfigured(
                    "The 'email_backend' argument is not valid when "
                    "settings.MAILERS is defined."
                )
            warnings.warn(
                "The 'email_backend' argument is deprecated. Use 'using' instead.",
                RemovedInDjango2028Warning,
                skip_file_prefixes=django_file_prefixes(),
            )
        if hasattr(self, "connection"):
            raise AttributeError(
                "The undocumented AdminEmailHandler.connection() method is no longer "
                "used."
            )

        self.include_html = include_html
        self.email_backend = email_backend
        self.using = using
        self.reporter_class = import_string(
            reporter_class or settings.DEFAULT_EXCEPTION_REPORTER
        )

    def emit(self, record):
        # Early return when no email will be sent.
        if (
            not settings.ADMINS
            # Method not overridden.
            and self.send_mail.__func__ is AdminEmailHandler.send_mail
        ):
            return
        try:
            request = record.request
            subject = "%s (%s IP): %s" % (
                record.levelname,
                (
                    "internal"
                    if request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
                    else "EXTERNAL"
                ),
                record.getMessage(),
            )
        except Exception:
            subject = "%s: %s" % (record.levelname, record.getMessage())
            request = None
        subject = self.format_subject(subject)

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = self.reporter_class(request, is_email=True, *exc_info)
        formated_record = self.format(no_exc_record)
        traceback = reporter.get_traceback_text()
        if reporter.exc_type:
            message = "%s\n\n%s" % (
                formated_record,
                traceback,
            )
            log_id = self._db_logger.log_exception(reporter=reporter, msg=message)
            formated_record = "Log ID: " + log_id + "\n\n" + formated_record
        html_message = reporter.get_traceback_html() if self.include_html else None
        self.send_mail(subject, formated_record, html_message=html_message)
