# __author: Lambert
# __date: 2017/10/30 14:33
from tornado.web import UIModule


class Customer(UIModule):
    def render(self, *args, **kwargs):
        return "ui_modules"
