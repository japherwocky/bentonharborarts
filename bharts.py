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

from keys import SMTP_USER, SMTP_PASS

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
            (r"/?fonts/(.*)", tornado.web.StaticFileHandler, {'path': 'fonts'}),
            (r"/submit/?", FormSubmit),
            (r"/$", tornado.web.RedirectHandler, {'url': r'/index.html'}),
            (r"/(.*)", Home),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)


class Home(tornado.web.RequestHandler):
    def get(self, path):
        if path in ('index.html', 'contact.html', 'explore.html', 'events.html', 'funding.html'):
            self.render(path)


class FormSubmit(tornado.web.RequestHandler):
    def post(self, **kwargs):
        out = "\n"
        for k in self.request.arguments.keys():
            value = self.request.arguments[k][0].decode('utf-8')

            out += "{}\n-----\n{}\n\n".format(k.capitalize() , value)

        #  args = [self.request.arguments[k] for k in self.request.arguments.keys()]

        self.mailpeople(out)

        #  import pdb;pdb.set_trace()


    def mailpeople(self, body):
        headers = 'From: j4ne@pearachute.com\nSubject: Incoming Message\n\n'
        try:
            m = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
            m.starttls()
            m.login(SMTP_USER, SMTP_PASS)

            recips = ['hello@pearachute.com']
            for recip in recips:
                m.sendmail('j4ne@pearachute.com', recip, body)
            m.quit()
        except:
            # make sure we don't lose the contact anyhow
            error(body)
            raise


def main():
    from tornado.options import define, options
    define("port", default=8001, help="run on the given port", type=int)
    define("debug", default=False, help="run server in debug mode", type=bool)
    define("localssl", default=False, help="enable https with self-signed/arbitrary certs", type=bool)

    tornado.options.parse_command_line()

    if options.localssl:

        here = os.path.dirname(os.path.realpath(__file__))
        opts = {
            "certfile": os.path.join(here, "server.crt"),
            "keyfile": os.path.join(here, "server.key"),
            }

        http_server = tornado.httpserver.HTTPServer( App(debug=options.debug), ssl_options=opts)
    else:
        http_server = tornado.httpserver.HTTPServer( App(debug=options.debug), xheaders=True)
    http_server.listen(options.port)
    info('Serving on port %d' % options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

