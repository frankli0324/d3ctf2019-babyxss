from flask import Flask, render_template_string, session, request, make_response
import hashlib
import os
import json
from rq import Queue
from redis import Redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'somesecret'
config = json.load(open('config.json', 'r'))


def verify_url(url):
    base = 'https://'+request.host
    if len(url) == 0:
        return False
    if len(url) < len(base) or url[:len(base)] != base:
        return False
    return True


def verify_captcha(captcha):
    return 'captcha' in session.keys() \
        and len(session.get('captcha')) == 5 \
        and hashlib.md5(captcha.encode()).hexdigest()[:5] == session.get('captcha')


def add_queue(url):
    q = Queue(connection=Redis(
        host=config['redis']['host'],
        password=config['redis']['auth']
    ))
    q.enqueue('bot.add', url)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.php', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        try:
            if 'captcha' in request.form.keys() and 'url' in request.form.keys():
                captcha = request.form['captcha']
                url = request.form['url']
                if not verify_captcha(captcha):
                    message = "Wrong Captcha :("
                elif not verify_url(url):
                    message = "Wrong URL :("
                else:
                    session.pop('captcha')
                    message = "Done! Please wait for the admin to check it out. XD"
                    add_queue(url)
        except:
            message = "Error! Please contact admin"
    if 'captcha' not in request.form.keys() or 'captcha' not in session.keys():
        session['captcha'] = hashlib.md5(os.urandom(16)).hexdigest()[:5]
    return render_template_string(
        index,
        message=message,
        host='https://'+request.host,
        captcha=session['captcha']
    )


@app.route('/fd.php')
def mirror():
    response = make_response(request.args.get('q'))
    response.headers['Content-Security-Policy'] = "img-src 'none'; script-src 'none'; frame-src 'none'; connect-src 'none'"
    return response


@app.route('/admin.php')
def admin():
    if request.headers.get('x-forwarded-for') != config['redis']['host']:
        return 'only admin can see it'
    token = request.host.split('.')[0]
    return f'''{{
    "token": "{token}",
    "flag": "d3ctf{{{hashlib.sha256((
        token+config["challenge"]["flag"]
    ).encode()).hexdigest()}}}"
}}
'''


index = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <link rel="stylesheet" type="text/css" href="/static/bootstrap.min.css">
    <style type="text/css">.form-control-borderless {border: none;}.form-control-borderless:hover, .form-control-borderless:active, .form-control-borderless:focus {outline: none;box-shadow: none;}
    </style>
</head>
<body>
<div class='container-fluid'><br><br><div class='row justify-content-center'>
<h1><font style="font-size: 6vw">
    Report <a href='/fd.php?q=bugs'>bugs</a> to admin?
</font></h1>
</div><br><br>
<div class='row justify-content-center'>
    <h3><font color='red'>{{ message }}</font></h3>
</div>
<div class="row justify-content-center"><div class="col col-sm-8">
    <form method="POST" action="">
        <div class="card card-body">
            <input class="form-control form-control-lg form-control-borderless" 
                   type="text" name="url" placeholder="{{ host }}">
        </div>
        <br>
        <div class="card card-body">
            <input class="form-control form-control-lg form-control-borderless" 
                   type="text" name="captcha" placeholder="md5($captcha)[:5]=={{ captcha }}">
        </div>
        <br><br>
        <div class="row justify-content-center">
            <button class="btn btn-lg btn-success"
                    type="submit">Report</button>
        </div>
    </form>
    
    <footer class="float-right">
        note for admins: flag is right <a href="/admin.php">here</a>.
    </footer>
</div>
</div></div>
</body>
</html>
'''


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
