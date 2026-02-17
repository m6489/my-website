import os
from flask import Flask, request, redirect, render_template_string, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# کاربران (در حافظه)
users = {}

# ===== صفحات HTML با گرافیک =====

login_html = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ورود</title>
<style>
body {margin:0;font-family:tahoma;background:linear-gradient(135deg,#141e30,#243b55);display:flex;justify-content:center;align-items:center;height:100vh;}
.card{background:rgba(255,255,255,0.1);backdrop-filter:blur(15px);padding:30px;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.5);width:300px;transition:0.4s;}
.card:hover{transform:rotateY(6deg) rotateX(6deg);}
h2{color:white;text-align:center;}
input{width:100%;margin-top:10px;padding:10px;border:none;border-radius:10px;}
button{width:100%;margin-top:15px;padding:10px;border:none;border-radius:10px;background:linear-gradient(45deg,#00c6ff,#0072ff);color:white;font-weight:bold;cursor:pointer;}
p{color:red;text-align:center;}
a{color:white;text-decoration:none;display:block;margin-top:10px;text-align:center;}
</style>
</head>
<body>
<div class="card">
<h2>ورود به حساب</h2>
<form method="post">
<input type="text" name="username" placeholder="نام کاربری">
<input type="password" name="password" placeholder="رمز عبور">
<button type="submit">ورود</button>
</form>
<p>{{msg}}</p>
<a href="/register">ساخت حساب جدید</a>
</div>
</body>
</html>
'''

register_html = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ثبت نام</title>
<style>
body {margin:0;font-family:tahoma;background:linear-gradient(135deg,#141e30,#243b55);display:flex;justify-content:center;align-items:center;height:100vh;}
.card{background:rgba(255,255,255,0.1);backdrop-filter:blur(15px);padding:30px;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.5);width:300px;transition:0.4s;}
.card:hover{transform:rotateY(6deg) rotateX(6deg);}
h2{color:white;text-align:center;}
input{width:100%;margin-top:10px;padding:10px;border:none;border-radius:10px;}
button{width:100%;margin-top:15px;padding:10px;border:none;border-radius:10px;background:linear-gradient(45deg,#00c6ff,#0072ff);color:white;font-weight:bold;cursor:pointer;}
p{color:red;text-align:center;}
a{color:white;text-decoration:none;display:block;margin-top:10px;text-align:center;}
</style>
</head>
<body>
<div class="card">
<h2>ساخت حساب</h2>
<form method="post">
<input type="text" name="username" placeholder="نام کاربری">
<input type="password" name="password" placeholder="رمز عبور">
<button type="submit">ثبت نام</button>
</form>
<p>{{msg}}</p>
<a href="/login">بازگشت به ورود</a>
</div>
</body>
</html>
'''

panel_html = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>پنل کاربر</title>
<style>
body {margin:0;font-family:tahoma;background:linear-gradient(135deg,#1d2b64,#f8cdda);display:flex;justify-content:center;align-items:center;height:100vh;}
.card{width:350px;padding:25px;border-radius:20px;background:rgba(255,255,255,0.15);backdrop-filter:blur(15px);box-shadow:0 15px 35px rgba(0,0,0,0.4);transition:0.4s;}
.card:hover{transform:rotateY(8deg) rotateX(8deg) scale(1.05);}
h2{text-align:center;color:white;}
.custom-file{background:white;padding:8px;border-radius:10px;margin-top:10px;cursor:pointer;text-align:center;}
input[type="file"]{display:none;}
button{width:100%;margin-top:15px;padding:10px;border:none;border-radius:10px;background:linear-gradient(45deg,#00c6ff,#0072ff);color:white;font-weight:bold;cursor:pointer;}
ul{margin-top:20px;padding:0;list-style:none;max-height:120px;overflow-y:auto;}
li{margin:5px 0;}
a{color:white;text-decoration:none;}
.logout{margin-top:10px;display:block;text-align:center;color:white;}
</style>
<script>
function انتخاب_فایل(){document.getElementById("file").click();}
function نمایش_نام(){document.getElementById("نامفایل").innerText=document.getElementById("file").files[0].name;}
</script>
</head>
<body>
<div class="card">
<h2>خوش آمدی {{username}}</h2>
<form method="post" enctype="multipart/form-data">
<div class="custom-file" onclick="انتخاب_فایل()">انتخاب فایل</div>
<div id="نامفایل" style="color:white;text-align:center;margin-top:5px;"></div>
<input type="file" id="file" name="file" onchange="نمایش_نام()">
<button type="submit">آپلود فایل</button>
</form>
<ul>
{% for file in files %}
<li><a href="/uploads/{{file}}" target="_blank">{{file}}</a></li>
{% endfor %}
</ul>
<a class="logout" href="/logout">خروج از حساب</a>
</div>
</body>
</html>
'''

# ===== مسیرها =====

@app.route("/")
def home():
    if "username" in session:
        files = os.listdir(UPLOAD_FOLDER)
        return render_template_string(panel_html, username=session["username"], files=files)
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            msg = "این نام کاربری قبلاً ثبت شده"
        else:
            users[username] = password
            return redirect("/login")
    return render_template_string(register_html, msg=msg)

@app.route("/login", methods=["GET","POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["username"] = username
            return redirect("/")
        else:
            msg = "نام کاربری یا رمز اشتباه است"
    return render_template_string(login_html, msg=msg)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/", methods=["POST"])
def upload():
    if "username" in session and "file" in request.files:
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
    return redirect("/")

# ===== اجرای Render =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
