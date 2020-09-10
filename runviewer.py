#!/usr/bin/env python3

import asyncio
import os
import re
import subprocess
import sys
import time
import tornado.httpserver
import tornado.ioloop
import tornado.template
import tornado.web

def log(fmt, *args):
    if not args:
        sys.stderr.write(str(fmt) + '\n')
    else:
        sys.stderr.write((str(fmt) % args) + '\n')


async def run_cgi(self, args, env=None):
        if env:
            genv = dict(os.environ)
            genv.update(env)
        else:
            genv = None
        p = await asyncio.create_subprocess_exec(
            *args,
            cwd='viewer/',
            env=genv,
            stdout=asyncio.subprocess.PIPE,
        )

        # Skip headers section
        while 1:
            line = await p.stdout.readline()
            if not line.strip():
                break

        # Forward actual content bytes
        while 1:
            b = await p.stdout.read(1024)
            if not b:
                break
            self.write(b)
            self.flush()
        await p.wait()


class IndexHandler(tornado.web.RequestHandler):
    async def get(self):
        await run_cgi(self, ['./index.cgi'])


class LogsHandler(tornado.web.RequestHandler):
    async def get(self, logid):
        await run_cgi(self, ['./log.cgi'], env={
            'REQUEST_METHOD': 'GET',
            'QUERY_STRING': 'log=%s' % logid,
        })


class RssHandler(tornado.web.RequestHandler):
    async def get(self):
        self.set_header('Content-type', 'text/xml')
        await run_cgi(self, ['./rss.cgi'])


def main():
    debug = True if os.getenv('DEBUG') else False

    settings = {
        'autoreload': True,
        'compress_response': True,
        'debug': debug,
        'template_whitespace': 'all'
    }

    STATICDIR = os.path.join(os.path.dirname(__file__), 'viewer/static')

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/log/([0-9a-f]+)$', LogsHandler),
        (r'/rss', RssHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, dict(path=STATICDIR)),
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    addr = '0.0.0.0' if debug else '127.0.0.1'
    PORT = 8014
    print('Listening on %s:%d' % (addr, PORT))
    http_server.listen(PORT, address=addr)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
