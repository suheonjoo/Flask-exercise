import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request#로그인 권한을 요청하기 전에
def load_logged_in_user():  #사용자가 적은 값이 db에 있는지 확인해야 한다
    user_id = session.get('user_id')
    #session으로 html에서 받은 정보 가져옴
    if user_id is None:#여기는 사용자가 아이디 칸에 아이디를 적지 않은 경우
        g.user = None
    else:   #여기가 db에 있는지 확인하는 쿼리 작업이다
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def login_required(view): #로그인 권한이 필요할경우의 함수
    @functools.wraps(view)
    def wrapped_view(**kwargs): #일단은 기존 뷰를 덮어씌운다라고 생각하면 된다
        if g.user is None:
            return redirect(url_for('auth.login'))
            #접근 권한이 없는 경우 로그인 페이지로 redirect 해준다
        return view(**kwargs)
        #접근 권한이 있으면 지금 기존뷰view(**kwargs)를 반환한다
    return wrapped_view #덮어진 view, 즉 wrapped_view의 반환값을 반환한다


#base.html에서 <li><a href="{{ url_for('auth.logout') }}">Log Out</a>이 부분이 있는데
#하이퍼 링크로 만들어서 클릭하면 auth.py의 logout 함수를 실행하게 하는 것임
@bp.route('/logout')
def logout():
    session.clear() #logout하면 지금 있는 해당 세션을 나간다
    return redirect(url_for('index'))#그리고 홈화면index 화면으로 redirect한다





#base.html에서 <li><a href="{{ url_for('auth.register') }}">Register</a>이 부분이 있어서
#하이퍼 링크를 만들어서 auth.py의 register함수를 실행하게 한다
#함수를 호출하게 되면 해당 아직 입력되는 값이 없으니깐 register 함수에서 render_template('auth/register.html')을 반환해주는 것임
#<form method="post">
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')#현대 화면 그대로로 되게 반환, 반환값이 현재 화면



