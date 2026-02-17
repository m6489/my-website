from flask import Flask, render_template_string, request, redirect, session, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret-key-123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

users = {}

# صفحه اصلی
@app.route("/")
def home():
    if "username" in session:
        return render_template_string("""
        <h2>خوش آمدی {{username}}</h2>
        <a href="/upload">آپلود فایل</a><br><br>
        <a href="/logout">خروج</a>
        """, username=session["username"])
    return redirect("/login")

# ثبت نام
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return "این نام کاربری قبلاً ثبت شده"
        users[username] = password
        return redirect("/login")

    return """
    <h2>ساخت حساب</h2>
    <form method="post">
    نام کاربری:<br>
    <input type="text" name="username"><br>
    رمز عبور:<br>
    <input type="password" name="password"><br><br>
    <button type="submit">ثبت نام</button>
    </form>
    <a href="/login">ورود</a>
    """

# ورود
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["username"] = username
            return redirect("/")
        return "اطلاعات اشتباه است"

    return """
    <h2>ورود</h2>
    <form method="post">
    نام کاربری:<br>
    <input type="text" name="username"><br>
    رمز عبور:<br>
    <input type="password" name="password"><br><br>
    <button type="submit">ورود</button>
    </form>
    <a href="/register">ساخت حساب جدید</a>
    """

# خروج
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

# آپلود
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return "فایل با موفقیت آپلود شد"

    return """
    <h2>آپلود فایل</h2>
    <form method="post" enctype="multipart/form-data">
    <input type="file" name="file"><br><br>
    <button type="submit">آپلود</button>
    </form>
    <br>
    <a href="/">بازگشت</a>
    """

# اجرای مخصوص Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)