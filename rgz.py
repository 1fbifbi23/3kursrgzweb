from flask import Blueprint, redirect, url_for, render_template, Blueprint, request, session, current_app, flash
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

rgz = Blueprint('rgz', __name__)

def dbConnect():
    conn = psycopg2.connect(
        host = '127.0.0.1',
        database='rgz_larionov_base',
        user = 'admin_rgz_larionov_base',
        password = '123')    
    return conn

def dbClose(cursor, connection):
    cursor.close()
    connection.close()

@rgz.route('/')
@rgz.route('/index')
def start():
    return redirect('/rgz/', code=302)

@rgz.route('/rgz/')
def main():
    username = session.get('username')
    return render_template('rgz.html', username=username)

@rgz.route('/rgz/login', methods=["GET", "POST"])
def login():
    errors = []

    if request.method == "GET":
        return render_template("login.html", errors=errors)
    
    username = request.form.get("username")
    password = request.form.get("password")

    if not (username or password):
        errors.append("Пожалуйста заполните все поля")
        return render_template("login.html", errors=errors)
    if username == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('login.html', errors=errors)
    if password == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('login.html', errors=errors)
    
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT user_id, password FROM users WHERE username = %s;", (username,))

    result = cur.fetchone()

    if result is None:
        errors.append("Неправильный логин или пароль")
        dbClose(cur, conn)
        return render_template("login.html", errors=errors)
    
    userID, hashPassword = result

    if check_password_hash(hashPassword, password):
        session['id'] = userID
        session['username'] = username
        dbClose(cur, conn)
        return redirect("/rgz/")
    
    else:
        errors.append('Неправильный логин пароль')
        return render_template('login.html', errors=errors)

@rgz.route('/rgz/register', methods = ['GET', 'POST'])
def register():
    userID = session.get('id')
    
    errors = []

    if request.method == "GET":
        return render_template('register.html', errors=errors)
     
    username = request.form.get("username")
    password = request.form.get("password")


    if not (username or password):
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('register.html', errors=errors)
    if username == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('register.html', errors=errors)
    if password == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('register.html', errors=errors)
    
    hashPassword = generate_password_hash(password)

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = %s;", (username,))

    if cur.fetchone() is not None:
        errors.append("Пользователь с данным именем уже существует")

        conn.close()
        cur.close()
        return render_template('register.html', errors=errors)
    
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id", (username, hashPassword))
    user_id = cur.fetchone()[0]
    session['id'] = user_id
    
    conn.commit()
    conn.close()
    cur.close()
    return redirect("/rgz/register2")

@rgz.route('/rgz/register2/', methods=['GET', 'POST'])
def choose_gender_and_partner_preferences():
    user_id = session.get('id')
    errors = []
    if user_id is None:
        return redirect('/rgz/register')

    if request.method == "GET":
        return render_template('register2.html', errors=errors)
    name = request.form.get('name')
    gender = request.form.get("gender")
    partner_gender = request.form.get("partner_gender")
    age = request.form.get('age')
    if not gender or not partner_gender:
        errors.append("Пожалуйста, выберите ваш пол и предпочитаемый пол партнера")
        return render_template('register2.html', errors=errors)

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute("INSERT INTO Profiles (user_id, age, name, gender, searching_for) VALUES (%s, %s, %s, %s, %s)",
                (user_id, age, name, gender, partner_gender))
    conn.commit()
    conn.close()
    cur.close()

    return redirect('/rgz/register3')

@rgz.route('/rgz/register3', methods=['GET', 'POST'])
def register3():
    userID = session.get('id')
    if userID is None:
        return redirect('/rgz/register')
    errors = []

    if request.method == "GET":
        return render_template('register3.html', errors=errors)

    description = request.form.get("description")

    if not description:
        errors.append("Пожалуйста, введите описание о себе")
        return render_template('register3.html', errors=errors)

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute("UPDATE Profiles SET about_me = %s WHERE user_id = %s;",
                (description, userID))
    conn.commit()
    conn.close()
    cur.close()

    return redirect('/rgz/register4')

@rgz.route('/rgz/register4', methods=['GET', 'POST'])
def register4():
    user_id = session.get('id')
    if user_id is None:
        return redirect('/rgz/register')

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            

            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            conn = dbConnect()
            cur = conn.cursor()

            cur.execute("UPDATE Profiles SET photo = %s WHERE user_id = %s;",
                        (file_path, user_id))
            conn.commit()
            dbClose(cur, conn)

            return redirect('/rgz/')
    return render_template('register4.html')
    
@rgz.route('/rgz/profile/')
def profile():
    user_id = session.get('id')
    if user_id is None:
        return redirect('/rgz/login')
    
    conn = dbConnect()
    cur = conn.cursor()
    cur.execute("SELECT age, name, gender, searching_for, about_me, photo FROM Profiles WHERE Profiles.user_id = %s", [user_id])
    articleBody = cur.fetchone()
    
    age = articleBody[0]
    name = articleBody[1]
    gender = articleBody[2]
    gender_search = articleBody[3]
    about_me = articleBody[4]
    photo = articleBody[5]
    photo_url = url_for('static', filename=os.path.join('uploads', os.path.basename(photo)).replace('\\', '/'), _external=True)
    dbClose(cur, conn)
    

    return render_template('profile.html', age=age, name=name, gender=gender, gender_search=gender_search, about_me=about_me, photo=photo, photo_url=photo_url)

@rgz.route('/rgz/profile/change/', methods=['GET', 'POST'])
def profile_change():
    user_id = session.get('id')
    if user_id is None:
        return redirect('/rgz/login')
    errors = []
    if request.method == "GET":
        return render_template('change.html', errors=errors)
    


    if user_id is None:
        return redirect('/rgz/login')
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            conn = dbConnect()
            cur = conn.cursor()

            cur.execute("UPDATE Profiles SET photo = %s WHERE user_id = %s;", (file_path, user_id))
            conn.commit()
            dbClose(cur, conn)
            return redirect('/rgz/profile')
        
    
    description = request.form.get("description")
    name = request.form.get('name')
    gender = request.form.get("gender")
    partner_gender = request.form.get("partner_gender")
    age = request.form.get('age')
    hide_profile = request.form.get('hide_profile')
    
    conn = dbConnect()
    cur = conn.cursor()
    cur.execute("SELECT age, name, gender, searching_for, about_me, hide_profile FROM Profiles WHERE user_id = %s;", (user_id,))
    current_values = cur.fetchone()
    current_age, current_name, current_gender, current_searching_for, current_about_me, current_hide_profile = current_values
    
    age = current_age if age == '' else int(age)
    name = name if name else current_name
    gender = gender if gender else current_gender
    partner_gender = partner_gender if partner_gender else current_searching_for
    description = description if description else current_about_me
    hide_profile = hide_profile if hide_profile else current_hide_profile

    cur.execute("""
        UPDATE Profiles
        SET age = COALESCE(%s, age),
            name = COALESCE(%s, name),
            gender = COALESCE(%s, gender),
            searching_for = COALESCE(%s, searching_for),
            about_me = COALESCE(%s, about_me),
            hide_profile = %s
        WHERE user_id = %s;
        """, (age, name, gender, partner_gender, description, hide_profile, user_id))

    conn.commit()
    conn.close()
    cur.close()
    
    
    return redirect('/rgz/profile')

@rgz.route('/rgz/profile/delete/', methods=['GET', 'POST'])
def profile_delete():
    user_id = session.get('id')

    if user_id is None:
        return redirect('/rgz/login')

    conn = dbConnect()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM Profiles WHERE user_id = %s;", (user_id,))
        
    cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))

    conn.commit()

    dbClose(cur, conn)

    session.clear()

    flash("Ваш профиль был успешно удален")
    return redirect('/rgz/')

@rgz.route('/rgz/glav', methods=['GET', 'POST'])
def glav():
    user_id = session.get('id')
    if user_id is None:
        return redirect('/rgz/login')
    
    search_name = request.args.get('search_name')
    search_age = request.args.get('search_age')
    page = request.args.get('page', 1, type=int)

    conn = dbConnect()
    cur = conn.cursor()

    where_clauses = []
    query_params = []

    if search_name:
        where_clauses.append("lower(name) LIKE lower(%s)")
        query_params.append(f"%{search_name}%") 

    if search_age:
        where_clauses.append("age = %s")
        query_params.append(search_age)

    extra_where = (" AND " + " AND ".join(where_clauses)) if where_clauses else ""

    search_query = f"""
    SELECT user_id, age, name, gender, searching_for, about_me, photo
    FROM Profiles
    WHERE (hide_profile = false OR hide_profile IS NULL) {extra_where}
    LIMIT 3 OFFSET %s;
    """
    
    offset = (page - 1) * 3
    query_params.append(offset)

    cur.execute(search_query, query_params)

    conn = dbConnect()
    cur = conn.cursor()
    
    cur.execute("SELECT gender, searching_for FROM Profiles WHERE user_id = %s;", (user_id,))
    user_profile = cur.fetchone()
    if user_profile is None:
        dbClose(cur, conn)
        flash("Профиль не найден.")
        return redirect('/rgz/profile')

    user_gender, user_searching_for = user_profile
    print(user_profile)

    search_query = """
    SELECT user_id, age, name, gender, searching_for, about_me, photo
    FROM Profiles
    WHERE searching_for = %s AND gender = %s AND (hide_profile = false OR hide_profile IS NULL)
    """

    search_params = [user_gender, user_searching_for]

    if search_name:
        search_query += " AND lower(name) LIKE lower(%s)"
        search_params.append(f'%{search_name}%')

    if search_age:
        search_query += " AND age = %s"
        search_params.append(search_age)

    offset = (page - 1) * 3
    search_query += " LIMIT 3 OFFSET %s"
    search_params.append(offset)

    cur.execute(search_query, tuple(search_params))

    search_results = cur.fetchall()
    results_with_photos = []
    for result in search_results:
        photo_filename = result[6]
        print(photo_filename)
        if photo_filename:
            photo_url = url_for('static', filename=os.path.join('uploads', os.path.basename(photo_filename)).replace('\\', '/'), _external=True)
        else:
            photo_url = None
        results_with_photos.append(result + (photo_url,))
    dbClose(cur, conn)
    print(search_results)
    print(results_with_photos)

    next_url = url_for('rgz.glav', page=page+1, search_name=search_name, search_age=search_age) \
        if len(search_results) == 3 else None
    prev_url = url_for('rgz.glav', page=page-1, search_name=search_name, search_age=search_age) \
        if page > 1 else None
    
    return render_template('glav.html', search_results=results_with_photos, next_url=next_url, prev_url=prev_url)
    
@rgz.route('/rgz/logout')
def logout():
    session.clear()
    return render_template('rgz.html')