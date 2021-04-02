import logging

import apprise

NOTIFICATION_LEVEL = logging.CRITICAL + 10
SUCCESS_LEVEL = NOTIFICATION_LEVEL + 10
logging.addLevelName(level=NOTIFICATION_LEVEL, levelName="NOTIFICATION")
logging.addLevelName(level=SUCCESS_LEVEL, levelName="SUCCESS")

APPRISE_SUPPORTED_FORMATS_URL = "https://github.com/caronc/apprise#supported-notifications"


class NotificationHandler(logging.Handler):

    def __init__(self, *apprise_urls: str) -> None:
        super().__init__(level=logging.CRITICAL)
        self._notifier = apprise.Apprise(servers=apprise_urls, debug=False)

    def add_apprise_url(self, *apprise_urls: str):
        for url in apprise_urls:
            self._notifier.add(servers=url)

    def clear_apprise_urls(self):
        self._notifier.clear()

    def emit(self, record: logging.LogRecord) -> None:
        level = record.levelno
        attach = None
        try:
            # noinspection PyUnresolvedReferences
            attach = record.attach
        except AttributeError:
            pass
        notification_title = str(record.levelname)
        try:
            # noinspection PyUnresolvedReferences
            notification_title = record.notification_title
        except AttributeError:
            pass
        notify_type = None
        if level == logging.CRITICAL:
            notify_type = apprise.NotifyType.FAILURE
        elif level == NOTIFICATION_LEVEL:
            notify_type = apprise.NotifyType.INFO
        elif level == SUCCESS_LEVEL:
            notify_type = apprise.NotifyType.SUCCESS
        if notify_type is not None:
            self._notifier.notify(title=notification_title, body=record.message, notify_type=notify_type, attach=attach)
