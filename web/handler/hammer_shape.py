# -*- coding: UTF-8 -*-
import datetime
import tornado.web
from ...model.quantc import HammerShape

class HammerShapeHandler(tornado.web.RequestHandler):
    def get(self):
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        stocks = HammerShape.select().where(HammerShape.date == today)
        self.render('hammer_shape.html', title='HammerShape', content='', stocks=stocks)