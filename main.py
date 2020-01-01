#!/usr/bin/env python3

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
            n  = r.zrange("hospital:name", 0, -1)
            a  = r.zrange("hospital:address", 0, -1)
            p  = r.zrange("hospital:phone", 0, -1)
            bn = r.zrange("hospital:beds_number", 0, -1)
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            i = [i for i in range(1, len(n)+1)]
            items = zip(i, n, a, p, bn)

            self.render('templates/hospital.html', items=items)

    def post(self):
        name = self.get_argument('name')
        address = self.get_argument('address')
        beds_number = self.get_argument('beds_number')
        phone = self.get_argument('phone')

        if not name or not address:
            self.set_status(400)
            self.write("Hospital name and address required")
            return

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
            self.write('OK: ID ' + ID + " for " + name)


class DoctorHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            s = r.zrange("doctor:surname", 0, -1)
            p = r.zrange("doctor:profession", 0, -1)
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            i = [i for i in range(1, len(s)+1)]
            items = zip(i, s, p)

            self.render('templates/doctor.html', items=items)

    def post(self):
        surname = self.get_argument('surname')
        profession = self.get_argument('profession')

        if not surname or not profession:
            self.set_status(400)
            self.write("Surname and profession required")
            return

        logging.info(surname + ' ' + profession)

        try:
            ID = r.get("doctor:autoID").decode()

            r.zadd("doctor:surname", {surname: ID})
            r.zadd("doctor:profession", {profession: ID})

            r.incr("doctor:autoID")
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            self.write('OK: ID ' + ID + " for " + surname)


class PatientHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            s   = r.zrange("patient:surname", 0, -1)
            bd  = r.zrange("patient:born_date", 0, -1)
            sex = r.zrange("patient:sex", 0, -1)
            mpn = r.zrange("patient:mpn", 0, -1)
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            i = [i for i in range(1, len(s)+1)]
            items = zip(i, s, bd, sex, mpn)

            self.render('templates/patient.html', items=items)

    def post(self):
        surname = self.get_argument('surname')
        born_date = self.get_argument('born_date')
        sex = self.get_argument('sex')
        mpn = self.get_argument('mpn')

        if not surname or not born_date or not sex or not mpn:
            self.set_status(400)
            self.write("All fields required")
            return

        # wow what a check
        if sex not in ['M', 'F']:
            self.set_status(400)
            self.write("Sex must be 'M' or 'F'")
            return

        logging.info(surname + ' ' + born_date + ' ' + sex + ' ' + mpn)

        try:
            ID = r.get("patient:autoID").decode()

            r.zadd("patient:surname", {surname: ID})
            r.zadd("patient:born_date", {born_date: ID})
            r.zadd("patient:sex", {sex: ID})
            r.zadd("patient:mpn", {mpn: ID})

            r.incr("patient:autoID")
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            self.write('OK: ID ' + ID + " for " + surname)


class DiagnosisHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            pid = r.zrange("diagnosis:patient_ID", 0, -1)
            t   = r.zrange("diagnosis:type", 0, -1)
            inf = r.zrange("diagnosis:information", 0, -1)
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            i = [i for i in range(1, len(pid)+1)]
            items = zip(i, pid, t, inf)

            self.render('templates/diagnosis.html', items=items)

    def post(self):
        patient_ID = self.get_argument('patient_ID')
        diagnosis_type = self.get_argument('type')
        information = self.get_argument('information')

        if not patient_ID or not diagnosis_type:
            self.set_status(400)
            self.write("Patiend ID and diagnosis type required")
            return

        try:
            patient = r.zrange("patient:surname", patient_ID, patient_ID)
        except ValueError:
            self.set_status(400)
            self.write("Invalid ID")
            return

        if not patient:
            self.set_status(400)
            self.write("No patient with such ID")
            return

        logging.info(patient_ID + ' ' + diagnosis_type + ' ' + information)

        try:
            ID = r.get("diagnosis:autoID").decode()

            r.zadd("diagnosis:patient_ID", {patient_ID: ID})
            r.zadd("diagnosis:type", {diagnosis_type: ID})
            r.zadd("diagnosis:information", {information: ID})

            r.incr("diagnosis:autoID")
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        else:
            self.write('OK: ID ' + ID + " for patient " + patient[0].decode())


def init_db():
    db_initiated = r.get("db_initiated")
    if not db_initiated:
        r.set("hospital:autoID", 1)
        r.set("doctor:autoID", 1)
        r.set("patient:autoID", 1)
        r.set("diagnosis:autoID", 1)
        r.set("db_initiated", 1)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r"/hospital", HospitalHandler),
        (r"/doctor", DoctorHandler),
        (r"/patient", PatientHandler),
        (r"/diagnosis", DiagnosisHandler)
    ], autoreload=True, debug=True, compiled_template_cache=False, serve_traceback=True)


if __name__ == "__main__":
    init_db()
    app = make_app()
    app.listen(PORT)
    tornado.options.parse_command_line()
    logging.info("Listening on " + str(PORT))
    tornado.ioloop.IOLoop.current().start()