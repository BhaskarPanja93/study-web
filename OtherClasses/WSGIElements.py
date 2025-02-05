from datetime import datetime
from ssl import SSLEOFError

from customisedLogs import CustomisedLogs
from gevent.pywsgi import WSGIHandler, WSGIServer


def format_bytes(size_in_bytes):
    if size_in_bytes == 0:
        return "0B"
    units = ["B", "K", "M", "G", "T", "P", "E", "Z", "Y"]
    power = 0
    while size_in_bytes >= 1024 and power < len(units) - 1:
        size_in_bytes /= 1024
        power += 1
    return f"{size_in_bytes:.2f}{units[power]}"


def format_log(delta, client_address, status_code, method, length, path):
    return (
        f"{delta:<{10}} "
        f"{client_address:<{20}} "
        f"{status_code:<{4}} "
        f"{method:<{6}} "
        f"{length:<{10}} "
        f"{path}"
    )


class SSLSuppressedLoggerAttachedWSGIHandler(WSGIHandler):
    def __init__(self, sock, address, server):
        super().__init__(sock, address, server)


    def process_result(self):
        try:
            super().process_result()
        except:
            pass


    def log_error(self, msg, *args):
        pass


    def log_request(self):
        length = '%s' % format_bytes(self.response_length) or '-B'
        if self.time_finish:
            delta = '%.3fms' % ((self.time_finish - self.time_start)*1000)
        else:
            delta = '-ms'
        client_address = '[%s]' % (self.headers.get("X-Forwarded-For") if self.headers.get("X-Forwarded-For") is not None else (self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address))
        logger:CustomisedLogs = self.server.logger
        color = logger.Colors.green_800 if self.code == -200 else logger.Colors.green_700_accent if self.code == 200 else logger.Colors.green_400 if 200 < self.code < 400 else logger.Colors.red_800
        #logger.log(color, self.application.name, format_log(delta, client_address , self.code, self.command, length, self.path))


class LoggerAttachedWSGIServer(WSGIServer):
    def __init__(self, listener, application, logger:CustomisedLogs, **ssl_args):
        self.logger:CustomisedLogs = logger
        self.handler_class: SSLSuppressedLoggerAttachedWSGIHandler|None = None
        super().__init__(listener, application=application, log=None, error_log=None, handler_class=SSLSuppressedLoggerAttachedWSGIHandler, **ssl_args)

    def handle(self, sock, address):
        try:
            handler = self.handler_class(sock, address, self)
            handler.handle()
        except:
            pass

    def wrap_socket_and_handle(self, client_socket, address):
        try:
            super().wrap_socket_and_handle(client_socket, address)
        except:
            pass
