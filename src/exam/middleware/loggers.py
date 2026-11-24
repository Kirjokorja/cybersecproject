import logging
import sys
import traceback
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import OperationalError
from exam.models import Log, LogEvent

class EventLogger:

    def __init__(self,
                django_logger=logging.getLogger("django"),
    ):
        self._logger = django_logger

    def _parse_request(self, request, level):
        request_text = ""
        request_text = request_text + "User: " + str(request.user) + "\n"

        if level > 1:
            request_text = request_text + "User: " + str(request.user) + "\n"
            request_text = request_text + "Scheme: " + request.scheme + "\n"
            request_text = request_text + "Method: " + str(request.method) + "\n"
            request_text = request_text + "Path: " + request.get_full_path()
        # if level == 2:
        #     request_text = request_text + "Host: " +request.headers.get("Host") + "\n"
        #     request_text = request_text + "Content-Type: " +request.headers.get("Content-Type") + "\n"
        #     request_text = request_text + "Connection: " +request.headers.get("Connection") + "\n"
        for h in request.headers:
            if level < 3 and h == "Cookie":
                continue
            if level < 2 and h != "Host":
                continue
            request_text = request_text + "\n" + h + ": " + request.headers.get(h)

        return request_text

    # FLAW 5: Security Logging and Monitoring Failures
    def log_event(self, request, event, msg="", actor=None):
        event_obj = LogEvent.objects.get(event_name=event)
        message = msg + "\n" + self._parse_request(request, event_obj.severity_level.level)
        log_id = Log.objects.create(event_type=event_obj, message=message, actor=actor).pk
        message = "Log ID: " + str(log_id) + ". " + msg

        # if event_obj.severity_level.level == 1:
        #     self._logger.info(msg=message)
        # if event_obj.severity_level.level == 2:
        #     self._logger.warning(msg=message)
        # if event_obj.severity_level.level == 3:
        #     self._logger.error(msg=message)
        # if event_obj.severity_level.level == 4:
        #     self._logger.critical(msg=message)

class ExceptionLogger:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def _parse_request(self, request):
        request_text = ""
        request_text = request_text + "User: " + str(request.user) + "\n"
        request_text = request_text + "Scheme: " + request.scheme + "\n"
        request_text = request_text + "Method: " + str(request.method) + "\n"
        request_text = request_text + "Path: " + str(request.get_full_path())
        for h in request.headers:
            request_text = request_text + "\n" + h + ": " + request.headers.get(h)
        return request_text

    def process_exception(self, request, exception):
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
        event_obj = LogEvent.objects.filter(event_name=exc_type)
        if not event_obj:
            event_obj = LogEvent.objects.get(event_name="GeneralException")
        msg = self._parse_request(request) + "\n\n" + "".join(tb.format())
        Log.objects.create(event_type=event_obj,
                                message=msg,
                                actor=request.user)

default_event_logger = EventLogger()
