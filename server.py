# __author: Lambert
# __date: 2017/10/30 11:14
import tornado.ioloop
import tornado.web
import ui_methods as mt
import ui_modules as md
import time

settings = {
    "template_path": 'tpl',
    "static_path": 'statics',
    "static_url_prefix": '/sss/',
    "cookie_secret": "123456",  # 设置签名密钥
    "ui_methods": mt,
    "ui_modules": md,
    "xsrf_cookies": True
}
nameList = []
container = {}


class Session:
    def __init__(self, handler):
        self.handler = handler
        self.random_str = None

    def __genarate_random_str(self):
        import hashlib
        import time
        obj = hashlib.md5()
        obj.update(bytes(str(time.time()), encoding="utf8"))
        random_str = obj.hexdigest()
        return random_str

    def __setitem__(self, key, value):
        if not self.random_str:
            random_str = self.handler.get_cookie("session", None)
            if not random_str:
                random_str = self.__genarate_random_str()
                container[random_str] = {}
            else:
                if random_str in container.keys():
                    pass
                else:
                    random_str = self.__genarate_random_str()
                    container[random_str] = {}
            self.random_str = random_str
        container[self.random_str][key] = value
        self.handler.set_cookie("session", self.random_str)

    def __getitem__(self, key):
        random_str = self.handler.get_cookie("session", None)
        if not random_str:
            return None
        user_info_str = container.get(random_str, None)
        if not user_info_str:
            return None
        value = user_info_str.get(key, None)
        return value


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session(self)
        print(container)


class MainHandler(BaseHandler):
    def get(self):
        user = self.get_secure_cookie("user", None)
        if user:
            self.session["is_login"] = True
            self.session["username"] = user
            self.render("index.html", nameList=nameList, npm="NPM", user=user)
        else:
            self.redirect("/login")

    # 对象被回收时调用
    def __del__(self):
        print('del')

    def post(self):
        name = self.get_argument("name")
        nameList.append(name)
        self.render("index.html", nameList=nameList, npm="NPM")


class ManagerHandler(BaseHandler):
    def get(self):
        print(container)
        if self.session["is_login"]:
            self.write("欢迎%s" % self.session["username"])
        else:
            self.redirect("/login")


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("login.html")

    def post(self, *args, **kwargs):
        user = self.get_argument('user')
        pwd = self.get_argument('password')
        check = self.get_argument("auto", None)
        code = self.get_argument("code", None)
        print(self.session["check_code"])
        if user == "admin" and pwd == "admin" and code.upper() == self.session["check_code"].upper():
            if check:
                self.set_secure_cookie("user", user, expires_days=7)  # 设置7天过期时间
            else:
                r = time.time() + 10
                self.set_secure_cookie("user", user, expires=r)  # 设置默认过期时间
            self.redirect("/index")
        else:
            self.render("login.html")


class LogoutHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_secure_cookie("user", self.get_secure_cookie("user"), expires=time.time())
        self.redirect("/login")


class CheckCodeHandler(BaseHandler):
    def get(self, *args, **kwargs):
        import check_code
        import io
        mstream = io.BytesIO()
        img, code = check_code.create_validate_code()
        self.session["check_code"] = code
        img.save(mstream, "GIF")
        self.write(mstream.getvalue())


def make_app():
    return tornado.web.Application([
        (r"/index", MainHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/admin", ManagerHandler),
        (r"/check_code", CheckCodeHandler),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
