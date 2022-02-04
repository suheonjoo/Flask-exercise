from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()#연결된 db를 가져온다
    posts = db.execute(#연결된 db에서 pid,title,body,created,authorid,username을 실행한다
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    #여기에서 받은 posts는 index.html에서 for post in posts에서 쓰이게 됨
    return render_template('blog/index.html', posts=posts)
    #blog파일에 index.html 페이지를 반환하는데 db에서 가져온 posts을 해당 페이지에 posts를 넣는다
    #posts를 해당 html에서 {% for post in posts %}의 posts에 넘겨줌



#index.html에서  <a class="action" href="{{ url_for('blog.create') }}">New</a>
#blog.py 에서 create()함수를 실행한다는 것임
@bp.route('/create', methods=('GET', 'POST'))
@login_required #auth권한.py에 로그인된 상태를 요구 하는 데코리이터 로그인이 안되있으면 들어갈수 더이상 접근 못하게 아니라 로그인 페이지로 wrap해줌
def create():
    if request.method == 'POST':#생성이 post임
        title = request.form['title']
#create.html의 value="{{ request.form['title'] }}에서 적은 요청이다
        body = request.form['body']
        error = None

        if not title:   #만약 가져온 title값이 적혀 있지 않으면
            error = 'Title is required.'   #eror 변수에 오류 메세지를 적어준다

        if error is not None:#에러 변수에 메시지가 적혀 있으면 
            flash(error)    #flash()로 메세지내용과 함께 pop하게 한다
        else:   #에러 변수에 메세지가 적혀 있지 않으면
            db = get_db()   #db 연결을 가져오고
            db.execute( #해당 db에 조건을 만족하는 post(title, body, author_id)를 삽입한다 
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',    #이런식으로 변수를 넣는다
                (title, body, g.user['id']) #여기서 tile하고 body는 html에서 가져온거고 g.user는 전역변수에 담은 해당 유저의 id가 들어 있다
            )
            db.commit() #db를 commit하고
            return redirect(url_for('blog.index'))
            #db에 내용을 다 삽입했으면 blog퐁더의 index.html페이지로 redirect한다

    return render_template('blog/create.html')
    # create.html로 간다. 여기까지 코드가 실행됬다는 것은 title이 입력 되니 않든 오류가 발생했다는 것임

def get_post(id, check_author=True):#
    post = get_db().execute(#db 연결도 하고 실행을 할것인데
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',#해당 id가 user 태이블에 있고, post에서 해당 사용자의 p.id, title, body,created,author_id,username을 반환한다
        (id,)
    ).fetchone()

    if post is None:#해당 아이디가 존재하지 않은 경우, 오류페이지를 보여준다
        abort(404, f"Post id {id} doesn't exist.")#오류번호는 404임

    if check_author and post['author_id'] != g.user['id']:
        abort(403)#작성자 id와 유저 id가 일치 하지 않은 경우 오류페이지를 보여준다

    return post


#<a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
#위에서 method가 post라고 전달되는 http 메소드를 정해주었다
@bp.route('/<int:id>/update', methods=('GET', 'POST'))#해당 아이디를 가지고 있는 내용을 업데이트하기
@login_required
def update(id):
    
    post = get_post(id)
    #해당 아이디를 가지고 있는 post를 반환한다

    if request.method == 'POST':#request가 post인 경우
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:#타이틀이 없으면 에러 변수에 오류 넣어줌
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:#오류가 없으면 
            db = get_db()   #db를 연결하고 
            db.execute(     #아래 쿼리문에서 해당 값들 업데이트 해줌
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit() #마지막 db에 commit 해줌
            return redirect(url_for('blog.index'))
            #blog 폴더에 index를 redirect한다

    return render_template('blog/update.html', post=post)
    #여기 까지 왔다는 것은 post가 제대로 되지않고 오류가 떳다는 것임


#<form> 태그의 method 속성은 폼 데이터(form data)가 서버로 제출될 때 사용되는 HTTP 메소드를 명시합니다.
#GET 방식은 URL에 폼 데이터를 추가하여 서버로 전달하는 방식입니다.
#POST 방식은 폼 데이터를 별도로 첨부하여 서버로 전달하는 방식입니다.

#update.html에서 <form method="post">여기에서 method 값을 알수 있음
@bp.route('/<int:id>/delete', methods=('POST',))
#<form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">
#위의 update.html부분 action에서 url_for 함수 안에 blog.delete를 호출해준다
#그리고 id=post['id']에서 post는 http의 메소드를 말하는 것이 아니고, index.html에서 for post in posts를 말하는 것임
#(update.html이 index.html의 연장선이라는 것을 잠깐 놓쳤음 위로 올라가 보니깐 post가 가리키는 것을 알았음)
@login_required
def delete(id):
    get_post(id)#해당 아이디 가지고 있는 post를 찾고
    db = get_db()#db 연결을 받아 온다
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
























