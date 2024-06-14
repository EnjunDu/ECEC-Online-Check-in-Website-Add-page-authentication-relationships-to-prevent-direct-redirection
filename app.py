from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zheshiyigeanquanmiyaoo~'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signin.db'
db = SQLAlchemy(app)

# 用户模块
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    sign_ins = db.relationship('SignIn', backref='user', lazy=True)

# 签到记录模块
class SignIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sign_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 创建数据库表格
@app.before_request
def create_tables():
    db.create_all()

# 登录检查装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 管理员权限检查装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin') != True:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# 主页
@app.route('/')
def index():
    return render_template('index.html')

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return '用户名和密码不能为空'

        if not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return '用户名和密码不能为空'

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['admin'] = False
            return redirect(url_for('signin'))
        else:
            return '登录失败'

    return render_template('login.html')

# 签到
@app.route('/signin', methods=['GET', 'POST'])
@login_required
def signin():
    if request.method == 'POST':
        new_sign_in = SignIn(user_id=session['user_id'])
        db.session.add(new_sign_in)
        db.session.commit()
        return '签到成功！'
    else:
        return render_template('signin.html')

# 管理员登录
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 设置一个专门的管理员账号密码
        admin_username = 'ISCC_2024_sky_Jack_Du'
        admin_password = 'sky_1s_S0_h@NdsOme~_1234678910'

        # 验证管理员账号密码
        if username == admin_username and password == admin_password:
            session['admin'] = True
            session['user_id'] = 1  # 设置一个固定的管理员ID
            return redirect(url_for('admin_dashboard'))
        else:
            return '登录失败'

    return render_template('admin_login.html')

# 后台面板
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    sign_ins = SignIn.query.all()
    return render_template('admin_dashboard.html', sign_ins=sign_ins)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8848)
