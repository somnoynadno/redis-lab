import os
import tornado.ioloop
import tornado.web

PORT = 8888

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'})
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    print("Listening on", PORT)
    tornado.ioloop.IOLoop.current().start()