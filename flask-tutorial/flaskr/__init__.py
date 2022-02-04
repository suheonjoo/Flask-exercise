import os

from flask import Flask



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello1():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    #'/' url에서 들어오는 모든 요청을 하는 endpoint가 index()함수를 실행한다는 것임
    #말그대로 endpoint가 index'이다라는 의미는 ~~~/index 앞에 뭐든간에 끝에 index가 오는 것을 말한다
    #여기서는 '/'라는 엔드 포인트에 index()를 실행하라는 것임
    #index()는 route('/')에 있다 실험해 본게 route('/s')로 수정하니깐 안됨


    return app