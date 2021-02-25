import os
import json
import smtplib

from logging import info, debug, error
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.web import HTTPError
from markdown import markdown

class App (tornado.web.Application):
    def __init__(self, debug=False):
        """
        Settings for our application
        """
        from keys import cookie
        settings = dict(
            cookie_secret=cookie,
            login_url="/login",
            template_path="templates",
            # static_path="static",
            xsrf_cookies=False,
            autoescape = None,
            debug = debug,  # restarts app server on changes to local files
        )

        """
        map URLs to Handlers, with regex patterns
        """


        handlers = [
            (r"/?img/(.*)", tornado.web.StaticFileHandler, {'path': 'media/img'}),
            (r"/?js/(.*)", tornado.web.StaticFileHandler, {'path': 'js'}),
            (r"/?css/(.*)", tornado.web.StaticFileHandler, {'path': 'css'}),
            (r"/$", tornado.web.RedirectHandler, {'url': r'/index.html'}),
            (r"/(.*)", Home),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)


class Home(tornado.web.RequestHandler):
    def get(self, path):
        if path in ('index.html', 'contact.html', 'explore.html', 'events.html'):
            self.render(path)



def main():
    from tornado.options import define, options
    define("port", default=8001, help="run on the given port", type=int)
    define("debug", default=False, help="run server in debug mode", type=bool)

    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer( App(debug=options.debug), xheaders=True)
    http_server.listen(options.port)
    info('Serving on port %d' % options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

