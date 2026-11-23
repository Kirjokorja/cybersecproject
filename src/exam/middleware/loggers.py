import logging
import sys
from exam.models import Log, LogEvent

class EventLogger:

    def __init__(self,
                django_logger=logging.getLogger("django"),
    ):
        self._logger = django_logger

    def _parse_request(self, request):
        request_text = ""
        for h in request.headers:
            request_text = request_text + "\n\n" + h + ": " + request.headers.get(h)
        # if request.COOKIES:
        #     for c in request.COOKIES:
        #         request_text = request_text + "\n\n" + c
        return request_text

    # FLAW 5: Security Logging and Monitoring Failures
    def log_event(self, request, event, msg="", actor=None):
        event_obj = LogEvent.objects.get(event_name=event)
        message = msg + "\n" + self._parse_request(request)
        log_id = Log.objects.create(event_type=event_obj, message=message, actor=actor).pk
        message = "Log ID: " + str(log_id) + "\n" + msg

        if event_obj.severity_level.level == 1:
            self._logger.info(msg=message)
        if event_obj.severity_level.level == 2:
            self._logger.warning(msg=message)
        if event_obj.severity_level.level == 3:
            self._logger.error(msg=message)
        if event_obj.severity_level.level == 4:
            self._logger.critical(msg=message)

class ExceptionLogger:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            self.log_exception(request, e)
            raise
        return response

    def _parse_request(self, request):
            request_text = ""
            for h in request.headers:
                request_text = request_text + "\n\n" + h + ": " + request.headers.get(h)
            return request_text

    def log_exception(self, request, exception):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        event_obj = LogEvent.objects.get(event_name=exc_type)
        msg = exc_type + ": " + exc_value + "\n" + exc_traceback
        if not event_obj:
            event_obj = LogEvent.objects.get(event_name="Exception")
        Log.objects.create(event_type=event_obj,
                                    message=msg,
                                    actor=request.user)

class ExceptionDbLogger:

    def log_exception(self, reporter, msg=""):
        event_obj = LogEvent.objects.get(event_name=reporter.exc_type)
        if not event_obj:
            event_obj = LogEvent.objects.get(event_name="Exception")
        log_id = Log.objects.create(event_type=event_obj,
                                    message=msg,
                                    actor=reporter.request.user).pk
        return log_id

default_event_logger = EventLogger()
