#!/usr/bin/env python
"""
Starts a Tornado static file server in a given directory.
To start the server in the current directory:

    tserv .

Then go to http://localhost:8000 to browse the directory.

Use the --prefix option to add a prefix to the served URL,
for example to match GitHub Pages' URL scheme:

    tserv . --prefix=jiffyclub

Then go to http://localhost:8000/jiffyclub/ to browse.

Use the --port option to change the port on which the server listens.

"""

from __future__ import print_function

import os
import sys
from argparse import ArgumentParser

import tornado.ioloop
import tornado.web
import tornado.template

class IndexHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET']

    def get(self, path):
        """ GET method to list contents of directory or
        write index page if index.html exists."""

        # remove heading slash
        #path = path[1:]

        for index in ['index.html', 'index.htm']:
            index = os.path.join(path, index)
            if os.path.exists(index):
                with open(index, 'rb') as f:
                    self.write(f.read())
                    self.finish()
                    return
        html = self.generate_index(path)
        self.write(html)
        self.finish()

    def generate_index(self, path):
        """ generate index html page, list all files and dirs.
        """
        if path:
            files = os.listdir(path)
        else:
            files = os.listdir('.')
        files = [filename + '/'
                if os.path.isdir(os.path.join(path, filename))
                else filename
                for filename in files]
        html_template = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>
        <title>Directory listing for /{{ path }}</title>
        <body>
        <h2>Directory listing for /{{ path }}</h2>
        <hr>
        <ul>
        {% for filename in files %}
        <li><a href="{{ filename }}">{{ filename }}</a>
        {% end %}
        </ul>
        <hr>
        </body>
        </html>
        """
        t = tornado.template.Template(html_template)
        return t.generate(files=files, path=path)




class Handler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + 'index.html'
        return url_path


def mkapp(prefix=''):
    application = tornado.web.Application([
        (r"/(.*)/$", IndexHandler),
        (r"/(astro_data)$", IndexHandler),
        (r"/astro_data/(.*)", Handler, {'path': "/home/astronomer/astro_data"}),
        (r"/(real-time\.html)", Handler, {'path' : "/home/astronomer"}),
        (r"/(expcontrol\.html)", Handler, {'path' : "/home/astronomer"}),
        (r"/(jquery.*\.js)", Handler, {'path' : "/home/astronomer"}),
        (r"/(experiment.*\.json)", Handler, {'path' : "/home/astronomer"})
    ], debug=False)

    return application


def start_server(prefix='', port=8000):
    app = mkapp(prefix)
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()


def parse_args(args=None):
    parser = ArgumentParser(
        description=(
            'Start a Tornado server to serve static files out of a '
            'given directory and with a given prefix.'))
    parser.add_argument(
        '-f', '--prefix', type=str, default='',
        help='A prefix to add to the location from which pages are served.')
    parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='Port on which to run server.')
    parser.add_argument(
        'dir', help='Directory from which to serve files.')
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    os.chdir(args.dir)
    print('Starting server on port {}'.format(args.port))
    start_server(prefix=args.prefix, port=args.port)


if __name__ == '__main__':
    sys.exit(main())
