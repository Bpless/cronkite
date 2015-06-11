class BaseHandler(tornado.web.RequestHandler):

  def get_login_url(self):
    return u"/login"

  def get_current_user(self):
    user_json = self.get_secure_cookie("user")
    if user_json:
      return tornado.escape.json_decode(user_json)
    else:
      return None


class LoginHandler(BaseHandler):

  def get(self):
    self.render("login.html", next=self.get_argument("next","/"), message=self.get_argument("error","") )

  def post(self):
    email = self.get_argument("email", "")
    password = self.get_argument("password", "")

    user = self.application.syncdb['users'].find_one( { 'user': email } )

    if user and user['password'] and bcrypt.hashpw(password, user['password']) == user['password']:
      self.set_current_user(email)
      self.redirect("hello")
    else:
      error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect.")
      self.redirect(u"/login" + error_msg)

  def set_current_user(self, user):
    print "setting "+user
    if user:
      self.set_secure_cookie("user", tornado.escape.json_encode(user))
    else:
      self.clear_cookie("user")


class SignupHandler(LoginHandler):

  def get(self):
    self.render("register.html", next=self.get_argument("next","/"))

  def post(self):
    email = self.get_argument("email", "")

    already_taken = self.application.syncdb['users'].find_one({
      'user': email
    })

    if already_taken:
      error_msg = u"?error=" + tornado.escape.url_escape("Login name already taken")
      self.redirect(u"/login" + error_msg)


    password = self.get_argument("password", "")
    hashed_pass = bcrypt.hashpw(password, bcrypt.gensalt(8))

    user = {}
    user['user'] = email
    user['password'] = hashed_pass

    auth = self.application.syncdb['users'].save(user)
    self.set_current_user(email)

    self.redirect("hello")
