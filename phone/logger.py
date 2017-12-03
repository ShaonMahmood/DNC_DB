import logging


class VimmLogger(object):

    def __init__(self, name, host_info=None):
        self.logger = logging.getLogger(name)
        self.host_info = host_info or {'hostname': 'send_number'}

    @property
    def name(self):
        return self.logger.name

    @name.setter
    def name(self, value):
        self.logger.name = value

    @property
    def level(self):
        return self.logger.level

    @level.setter
    def level(self, value):
        self.logger.level = value

    @property
    def parent(self):
        return self.logger.parent

    @parent.setter
    def parent(self, value):
        self.logger.parent = value

    @property
    def propagate(self):
        return self.logger.propagate

    @propagate.setter
    def propagate(self, value):
        self.logger.propagate = value

    @property
    def handlers(self):
        return self.logger.handlers

    @handlers.setter
    def handlers(self, value):
        self.logger.handlers = value

    @property
    def disabled(self):
        return self.logger.disabled

    @disabled.setter
    def disabled(self, value):
        self.logger.disabled = value

    @property
    def filters(self):
        return self.logger.filters

    @filters.setter
    def filters(self, value):
        self.logger.filters = value

    def setLevel(self, level):
        self.logger.setLevel(level)

    def debug(self, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.warning(msg, *args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.exception(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.critical(msg, *args, **kwargs)

    fatal = critical

    def log(self, level, msg, *args, **kwargs):
        kwargs.setdefault('extra', self.host_info)
        self.logger.log(level, msg, *args, **kwargs)

    def findCaller(self):
        return self.logger.findCaller()

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        return self.logger.makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra)

    def handle(self, record):
        self.logger.handle(record)

    def addHandler(self, hdlr):
        self.logger.addHandler(hdlr)

    def removeHandler(self, hdlr):
        self.logger.removeHandler(hdlr)

    def callHandlers(self, record):
        self.logger.callHandlers(record)

    def getEffectiveLevel(self):
        return self.logger.getEffectiveLevel()

    def isEnabledFor(self, level):
        return self.logger.isEnabledFor(level)

    def getChild(self, suffix):
        return self.logger.getChild(suffix)

    def addFilter(self, filter):
        self.logger.addFilter(filter)

    def removeFilter(self, filter):
        self.logger.removeFilter(filter)

    def filter(self, record):
        return self.logger.filter(record)
