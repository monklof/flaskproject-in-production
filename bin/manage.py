#!/usr/bin/env python2.7
# coding:utf-8
import sys, os
from os import path
sys.path.append(
    path.realpath(
        path.join(path.dirname(__file__), "../src")
    )
)
# acticate configuration 
from swing import get_env_var,refresh_config,config
import settings

import multiprocessing
# 计算CPU核数，默认worker数量为2*CPU + 1
DEFAULT_WORKERS = multiprocessing.cpu_count()*2 + 1
from utils import docopt

def init_app_logger(app):
    import logging
    import logging.config
    from logging import Formatter, StreamHandler
    from utils.outputdependhandler import OutputDependHandler
    # DEBUG模式自带日志
    if not app.debug:
        handler = OutputDependHandler(
            logging.handlers.TimedRotatingFileHandler(
                config.DEFAULT_ERROR_LOG, 'D', 1, 30),
            (StreamHandler(sys.stdout)))
        handler.setLevel(config.LOG_APP_LEVEL)
        handler.setFormatter(Formatter(config.LOG_BASE_FORMAT))
        app.logger.addHandler(handler)

    handler_root = OutputDependHandler(
        logging.handlers.TimedRotatingFileHandler(
            config.ROOT_LOG, 'D', 1, 30),
        (StreamHandler(sys.stdout)))
    handler_root.setLevel(config.ROOT_LOG_LEVEL)
    handler_root.setFormatter(Formatter(config.LOG_BASE_FORMAT))
    logging.getLogger().addHandler(handler_root)
    logging.getLogger().setLevel(config.ROOT_LOG_LEVEL)

def _prepare_flask_app(confname):
    os.environ[get_env_var()] = confname
    refresh_config()
    from main import app
    init_app_logger(app)
    return app

def debug_server(config='dev', host='0.0.0.0', port=5000, **options):
    """调试运行 Web API Service

    @=config, c
    @=host, h
    @=port, p
    """
    app = _prepare_flask_app(config)
    port = int(port)
    app.run(host=host, port=port, debug=True)

def gunicorn_server(
        config='dev',
        host='0.0.0.0', port=5000,
        workers=DEFAULT_WORKERS,
        accesslog=config.DEFAULT_ACCESS_LOG,
        errorlog=config.DEFAULT_ERROR_LOG,
        **options):
    """以Gunicorn Application模式运行Service

    @=config, c
    @=host, h
    @=port, p
    @=workers, w
    @=max-requests
    @=accesslog
    @=errorlog
    """
    #删除命令行参数, 防止gunicorn Application重复解析命令行
    del sys.argv[1:] #TODO: Do this in docopt as an option

    port = int(port)

    from gunicorn.app.base import Application
    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            gunicorn_options = {
                'bind': '{0}:{1}'.format(host, port),
                'workers': workers,
                'max_requests': options.pop('max-requests', 0),
                'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" %(p)s %(T)s.%(D)6s "%(i)s" "%(o)s"',
                'accesslog': accesslog,
                'errorlog': errorlog
            }
            gunicorn_options.update(options)
            return gunicorn_options

        def load(self):
            return _prepare_flask_app(config)

    FlaskApplication().run()


def run(settings='dev', **options):
    """
    @=settings
    """
    # do nothing
    return {}


if __name__ == "__main__":
    docopt.run(
        entry=run,
        cmdfuncs=[
            debug_server,
            gunicorn_server
        ]
    )
