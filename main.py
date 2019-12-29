import logging
import redis
import tornado.ioloop
import tornado.web

from tornado.options import parse_command_line

PORT = 8888
r = redis.StrictRedis(host='localhost', port=6379, db=0)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')


class HospitalHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            n = r.zrange("hospital:name", 0, -1)
            a = r.zrange("hospital:address", 0, -1)
            p = r.zrange("hospital:phone", 0, -1)
            bn = r.zrange("hospital:beds_number", 0, -1)
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")

        i = [i for i in range((len(n)))]
        items = zip(i, n, a, p, bn)

        self.render('templates/hospital.html', items=items)

    def post(self):
        name = self.get_argument('name')
        address = self.get_argument('address')
        beds_number = self.get_argument('beds_number')
        phone = self.get_argument('phone')

        logging.info(name + ' ' + address + ' ' + beds_number + ' ' + phone)

        try:
            ID = r.get("hospital:autoID").decode()

            r.zadd("hospital:name", {name: ID})
            r.zadd("hospital:address", {address: ID})
            r.zadd("hospital:phone", {phone: ID})
            r.zadd("hospital:beds_number", {beds_number: ID})

            r.incr("hospital:autoID")
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            self.write('OK ' + ID + " " + name)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r"/hospital", HospitalHandler)
    ], autoreload=True, debug=True, compiled_template_cache=False, serve_traceback=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    tornado.options.parse_command_line()
    logging.info("Listening on " + str(PORT))
    tornado.ioloop.IOLoop.current().start()