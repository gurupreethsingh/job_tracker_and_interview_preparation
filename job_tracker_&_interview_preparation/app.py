# import sqlite3
# import secrets
# from functools import wraps
# from flask import Flask, render_template, request, redirect, url_for, flash, session, g
# from werkzeug.security import generate_password_hash, check_password_hash
# import os

# print("TEMPLATE FOLDER:", os.path.abspath("templates"))

# app = Flask(__name__)
# app.secret_key = "super-secret-key-change-this-in-production"

# DATABASE = "job_tracker.db"


# # ----------------------------
# # Database helpers
# # ----------------------------
# def get_db():
#     if "db" not in g:
#         g.db = sqlite3.connect(DATABASE)
#         g.db.row_factory = sqlite3.Row
#     return g.db


# @app.teardown_appcontext
# def close_db(error=None):
#     db = g.pop("db", None)
#     if db is not None:
#         db.close()


# def add_column_if_missing(cursor, table_name, column_name, column_definition):
#     cursor.execute(f"PRAGMA table_info({table_name})")
#     columns = [col[1] for col in cursor.fetchall()]
#     if column_name not in columns:
#         cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


# def add_missing_columns():
#     db = sqlite3.connect(DATABASE)
#     db.row_factory = sqlite3.Row
#     cursor = db.cursor()

#     # ---------------- USERS TABLE ----------------
#     add_column_if_missing(cursor, "users", "is_deleted", "INTEGER DEFAULT 0")
#     add_column_if_missing(cursor, "users", "deleted_at", "TIMESTAMP NULL")
#     add_column_if_missing(cursor, "users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

#     # ---------------- PASSWORD_RESETS TABLE ----------------
#     add_column_if_missing(cursor, "password_resets", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

#     # ---------------- MASTER_PREP_TOPICS TABLE ----------------
#     add_column_if_missing(cursor, "master_prep_topics", "category", "TEXT")
#     add_column_if_missing(cursor, "master_prep_topics", "description", "TEXT")
#     add_column_if_missing(cursor, "master_prep_topics", "is_active", "INTEGER DEFAULT 1")
#     add_column_if_missing(cursor, "master_prep_topics", "created_by", "INTEGER")
#     add_column_if_missing(cursor, "master_prep_topics", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

#     # ---------------- MASTER_PREP_QUESTIONS TABLE ----------------
#     add_column_if_missing(cursor, "master_prep_questions", "answer", "TEXT")
#     add_column_if_missing(cursor, "master_prep_questions", "difficulty", "TEXT")
#     add_column_if_missing(cursor, "master_prep_questions", "is_active", "INTEGER DEFAULT 1")
#     add_column_if_missing(cursor, "master_prep_questions", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

#     # ---------------- USER_SELECTED_TOPICS TABLE ----------------
#     add_column_if_missing(cursor, "user_selected_topics", "progress_status", "TEXT DEFAULT 'Not Started'")
#     add_column_if_missing(cursor, "user_selected_topics", "notes", "TEXT")
#     add_column_if_missing(cursor, "user_selected_topics", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

#     # ---------------- USER_SELECTED_QUESTIONS TABLE ----------------
#     add_column_if_missing(cursor, "user_selected_questions", "is_important", "INTEGER DEFAULT 0")
#     add_column_if_missing(cursor, "user_selected_questions", "personal_notes", "TEXT")
#     add_column_if_missing(cursor, "user_selected_questions", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

#     db.commit()
#     db.close()


# def init_db():
#     db = sqlite3.connect(DATABASE)
#     cursor = db.cursor()

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             full_name TEXT NOT NULL,
#             email TEXT NOT NULL UNIQUE,
#             password TEXT NOT NULL,
#             role TEXT NOT NULL CHECK(role IN ('superadmin', 'user')),
#             is_deleted INTEGER DEFAULT 0,
#             deleted_at TIMESTAMP NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS password_resets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             email TEXT NOT NULL,
#             token TEXT NOT NULL UNIQUE,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS master_prep_topics (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             topic_name TEXT NOT NULL,
#             category TEXT,
#             description TEXT,
#             is_active INTEGER DEFAULT 1,
#             created_by INTEGER,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (created_by) REFERENCES users(id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS master_prep_questions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             topic_id INTEGER NOT NULL,
#             question TEXT NOT NULL,
#             answer TEXT,
#             difficulty TEXT,
#             is_active INTEGER DEFAULT 1,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (topic_id) REFERENCES master_prep_topics(id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS user_selected_topics (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             topic_id INTEGER NOT NULL,
#             progress_status TEXT DEFAULT 'Not Started',
#             notes TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             UNIQUE(user_id, topic_id),
#             FOREIGN KEY (user_id) REFERENCES users(id),
#             FOREIGN KEY (topic_id) REFERENCES master_prep_topics(id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS user_selected_questions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             question_id INTEGER NOT NULL,
#             is_important INTEGER DEFAULT 0,
#             personal_notes TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             UNIQUE(user_id, question_id),
#             FOREIGN KEY (user_id) REFERENCES users(id),
#             FOREIGN KEY (question_id) REFERENCES master_prep_questions(id)
#         )
#     """)

#         cursor.execute("""
# CREATE TABLE IF NOT EXISTS jobs (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     company TEXT,
#     location TEXT,
#     salary TEXT,
#     description TEXT,
#     is_active INTEGER DEFAULT 1,
#     created_by INTEGER,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (created_by) REFERENCES users(id)
# )
#     """)

#             cursor.execute("""
# CREATE TABLE IF NOT EXISTS job_applications (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     job_id INTEGER NOT NULL,
#     user_id INTEGER NOT NULL,
#     full_name TEXT,
#     email TEXT,
#     phone TEXT,
#     resume TEXT,
#     cover_letter TEXT,
#     status TEXT DEFAULT 'Pending',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (job_id) REFERENCES jobs(id),
#     FOREIGN KEY (user_id) REFERENCES users(id)
# )
#     """)

#                 cursor.execute("""
#    CREATE TABLE IF NOT EXISTS notifications (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER NOT NULL,
#     message TEXT,
#     is_read INTEGER DEFAULT 0,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (user_id) REFERENCES users(id)
# )
#     """)


 



#     cursor.execute("SELECT * FROM users WHERE email = ?", ("superadmin@jobtrackerai.com",))
#     superadmin = cursor.fetchone()

#     if not superadmin:
#         cursor.execute("""
#             INSERT INTO users (full_name, email, password, role, is_deleted)
#             VALUES (?, ?, ?, ?, 0)
#         """, (
#             "Super Admin",
#             "superadmin@jobtrackerai.com",
#             generate_password_hash("Admin@123"),
#             "superadmin"
#         ))

#     db.commit()
#     db.close()


# # ----------------------------
# # Auth decorators
# # ----------------------------
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if "user_id" not in session:
#             flash("Please login first.", "warning")
#             return redirect(url_for("login"))
#         return f(*args, **kwargs)
#     return decorated_function


# def role_required(required_role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if "user_id" not in session:
#                 flash("Please login first.", "warning")
#                 return redirect(url_for("login"))

#             if session.get("role") != required_role:
#                 flash("You are not authorized to access this page.", "danger")
#                 return redirect(url_for("login"))

#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator


# # ----------------------------
# # Context processor
# # ----------------------------
# @app.context_processor
# def inject_user():
#     return {
#         "current_user_name": session.get("full_name"),
#         "current_user_role": session.get("role"),
#         "current_user_id": session.get("user_id"),
#         "is_logged_in": "user_id" in session
#     }


# # ----------------------------
# # Public routes
# # ----------------------------
# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         full_name = request.form.get("full_name", "").strip()
#         email = request.form.get("email", "").strip().lower()
#         password = request.form.get("password", "").strip()
#         confirm_password = request.form.get("confirm_password", "").strip()
#         role = request.form.get("role", "user").strip()

#         if not full_name or not email or not password or not confirm_password:
#             flash("All fields are required.", "danger")
#             return redirect(url_for("register"))

#         if password != confirm_password:
#             flash("Passwords do not match.", "danger")
#             return redirect(url_for("register"))

#         if role not in ["superadmin", "user"]:
#             flash("Invalid role selected.", "danger")
#             return redirect(url_for("register"))

#         db = get_db()
#         cursor = db.cursor()

#         existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
#         if existing_user and existing_user["is_deleted"] == 0:
#             flash("Email already registered. Please login.", "warning")
#             return redirect(url_for("login"))

#         if existing_user and existing_user["is_deleted"] == 1:
#             flash("This email belongs to a deleted account. Please contact superadmin.", "warning")
#             return redirect(url_for("login"))

#         hashed_password = generate_password_hash(password)

#         cursor.execute("""
#             INSERT INTO users (full_name, email, password, role, is_deleted)
#             VALUES (?, ?, ?, ?, 0)
#         """, (full_name, email, hashed_password, role))
#         db.commit()

#         flash("Registration successful. Please login.", "success")
#         return redirect(url_for("login"))

#     return render_template("register.html")


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get("email", "").strip().lower()
#         password = request.form.get("password", "").strip()

#         if not email or not password:
#             flash("Email and password are required.", "danger")
#             return redirect(url_for("login"))

#         db = get_db()
#         user = db.execute(
#             "SELECT * FROM users WHERE email = ? AND is_deleted = 0",
#             (email,)
#         ).fetchone()

#         if user and check_password_hash(user["password"], password):
#             session.clear()
#             session["user_id"] = user["id"]
#             session["full_name"] = user["full_name"]
#             session["email"] = user["email"]
#             session["role"] = user["role"]

#             flash("Login successful.", "success")

#             if user["role"] == "superadmin":
#                 return redirect(url_for("super_admin_dashboard"))
#             return redirect(url_for("user_dashboard"))

#         flash("Invalid email or password.", "danger")
#         return redirect(url_for("login"))

#     return render_template("login.html")


# @app.route("/forgot-password", methods=["GET", "POST"])
# def forgot_password():
#     reset_link = None

#     if request.method == "POST":
#         email = request.form.get("email", "").strip().lower()

#         if not email:
#             flash("Please enter your email.", "danger")
#             return redirect(url_for("forgot_password"))

#         db = get_db()
#         user = db.execute(
#             "SELECT * FROM users WHERE email = ? AND is_deleted = 0",
#             (email,)
#         ).fetchone()

#         if not user:
#             flash("No active account found with that email.", "warning")
#             return redirect(url_for("forgot_password"))

#         token = secrets.token_urlsafe(32)

#         db.execute("INSERT INTO password_resets (email, token) VALUES (?, ?)", (email, token))
#         db.commit()

#         reset_link = url_for("reset_password", token=token, _external=True)
#         flash("Password reset link generated successfully.", "success")

#     return render_template("forgot_password.html", reset_link=reset_link)


# @app.route("/reset-password/<token>", methods=["GET", "POST"])
# def reset_password(token):
#     db = get_db()
#     reset_record = db.execute("SELECT * FROM password_resets WHERE token = ?", (token,)).fetchone()

#     if not reset_record:
#         flash("Invalid or expired reset link.", "danger")
#         return redirect(url_for("forgot_password"))

#     if request.method == "POST":
#         password = request.form.get("password", "").strip()
#         confirm_password = request.form.get("confirm_password", "").strip()

#         if not password or not confirm_password:
#             flash("Both password fields are required.", "danger")
#             return redirect(url_for("reset_password", token=token))

#         if password != confirm_password:
#             flash("Passwords do not match.", "danger")
#             return redirect(url_for("reset_password", token=token))

#         hashed_password = generate_password_hash(password)

#         db.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, reset_record["email"]))
#         db.execute("DELETE FROM password_resets WHERE email = ?", (reset_record["email"],))
#         db.commit()

#         flash("Password reset successful. Please login.", "success")
#         return redirect(url_for("login"))

#     return render_template("reset_password.html", token=token)


# # ----------------------------
# # Dashboard routes
# # ----------------------------
# @app.route("/superadmin/dashboard")
# @login_required
# @role_required("superadmin")
# def super_admin_dashboard():
#     db = get_db()

#     total_users = db.execute("""
#         SELECT COUNT(*) AS count FROM users
#         WHERE role = 'user' AND is_deleted = 0
#     """).fetchone()["count"]

#     total_superadmins = db.execute("""
#         SELECT COUNT(*) AS count FROM users
#         WHERE role = 'superadmin' AND is_deleted = 0
#     """).fetchone()["count"]

#     deleted_users_count = db.execute("""
#         SELECT COUNT(*) AS count FROM users
#         WHERE is_deleted = 1
#     """).fetchone()["count"]

#     total_master_topics = db.execute("""
#         SELECT COUNT(*) AS count FROM master_prep_topics WHERE is_active = 1
#     """).fetchone()["count"]

#     total_master_questions = db.execute("""
#         SELECT COUNT(*) AS count FROM master_prep_questions WHERE is_active = 1
#     """).fetchone()["count"]

#     recent_users = db.execute("""
#         SELECT id, full_name, email, role, created_at
#         FROM users
#         WHERE is_deleted = 0
#         ORDER BY id DESC
#         LIMIT 5
#     """).fetchall()

#     return render_template(
#         "super_admin_dashboard.html",
#         total_users=total_users,
#         total_superadmins=total_superadmins,
#         deleted_users_count=deleted_users_count,
#         total_master_topics=total_master_topics,
#         total_master_questions=total_master_questions,
#         recent_users=recent_users
#     )


# @app.route("/user/dashboard")
# @login_required
# @role_required("user")
# def user_dashboard():
#     db = get_db()
#     user_id = session.get("user_id")

#     total_selected_topics = db.execute("""
#         SELECT COUNT(*) AS count
#         FROM user_selected_topics
#         WHERE user_id = ?
#     """, (user_id,)).fetchone()["count"]

#     completed_topics = db.execute("""
#         SELECT COUNT(*) AS count
#         FROM user_selected_topics
#         WHERE user_id = ? AND progress_status = 'Mastered'
#     """, (user_id,)).fetchone()["count"]

#     total_selected_questions = db.execute("""
#         SELECT COUNT(*) AS count
#         FROM user_selected_questions
#         WHERE user_id = ?
#     """, (user_id,)).fetchone()["count"]

#     important_questions = db.execute("""
#         SELECT COUNT(*) AS count
#         FROM user_selected_questions
#         WHERE user_id = ? AND is_important = 1
#     """, (user_id,)).fetchone()["count"]

#     recent_topics = db.execute("""
#         SELECT ust.id, ust.progress_status, ust.created_at, mpt.topic_name, mpt.category
#         FROM user_selected_topics ust
#         INNER JOIN master_prep_topics mpt ON ust.topic_id = mpt.id
#         WHERE ust.user_id = ?
#         ORDER BY ust.id DESC
#         LIMIT 5
#     """, (user_id,)).fetchall()

#     available_topic_count = db.execute("""
#         SELECT COUNT(*) AS count
#         FROM master_prep_topics
#         WHERE is_active = 1
#     """).fetchone()["count"]

#     return render_template(
#         "user_dashboard.html",
#         total_selected_topics=total_selected_topics,
#         completed_topics=completed_topics,
#         total_selected_questions=total_selected_questions,
#         important_questions=important_questions,
#         recent_topics=recent_topics,
#         available_topic_count=available_topic_count
#     )


# # ----------------------------
# # Superadmin master topic routes
# # ----------------------------
# @app.route("/superadmin/add-master-topic", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def add_master_topic():
#     if request.method == "POST":
#         topic_name = request.form.get("topic_name", "").strip()
#         category = request.form.get("category", "").strip()
#         description = request.form.get("description", "").strip()

#         if not topic_name:
#             flash("Topic name is required.", "danger")
#             return redirect(url_for("add_master_topic"))

#         db = get_db()

#         existing = db.execute("""
#             SELECT id FROM master_prep_topics
#             WHERE LOWER(topic_name) = LOWER(?) AND is_active = 1
#         """, (topic_name,)).fetchone()

#         if existing:
#             flash("This topic already exists.", "warning")
#             return redirect(url_for("all_master_topics"))

#         db.execute("""
#             INSERT INTO master_prep_topics (topic_name, category, description, created_by)
#             VALUES (?, ?, ?, ?)
#         """, (topic_name, category, description, session.get("user_id")))
#         db.commit()

#         flash("Master topic added successfully.", "success")
#         return redirect(url_for("all_master_topics"))

#     return render_template("add_master_topic.html")


# @app.route("/superadmin/all-master-topics")
# @login_required
# @role_required("superadmin")
# def all_master_topics():
#     db = get_db()
#     search = request.args.get("search", "").strip()
#     category = request.args.get("category", "").strip()

#     query = """
#         SELECT mpt.*,
#                (SELECT COUNT(*) FROM master_prep_questions mpq WHERE mpq.topic_id = mpt.id AND mpq.is_active = 1) AS questions_count
#         FROM master_prep_topics mpt
#         WHERE mpt.is_active = 1
#     """
#     params = []

#     if search:
#         query += " AND (mpt.topic_name LIKE ? OR mpt.category LIKE ?)"
#         params.extend([f"%{search}%", f"%{search}%"])

#     if category:
#         query += " AND mpt.category = ?"
#         params.append(category)

#     query += " ORDER BY mpt.topic_name ASC"

#     topics = db.execute(query, params).fetchall()
#     categories = db.execute("""
#         SELECT DISTINCT category FROM master_prep_topics
#         WHERE is_active = 1 AND category IS NOT NULL AND category != ''
#         ORDER BY category ASC
#     """).fetchall()

#     return render_template(
#         "all_master_topics.html",
#         topics=topics,
#         search=search,
#         category=category,
#         categories=categories
#     )


# @app.route("/superadmin/edit-master-topic/<int:topic_id>", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def edit_master_topic(topic_id):
#     db = get_db()
#     topic = db.execute("""
#         SELECT * FROM master_prep_topics
#         WHERE id = ? AND is_active = 1
#     """, (topic_id,)).fetchone()

#     if not topic:
#         flash("Master topic not found.", "danger")
#         return redirect(url_for("all_master_topics"))

#     if request.method == "POST":
#         topic_name = request.form.get("topic_name", "").strip()
#         category = request.form.get("category", "").strip()
#         description = request.form.get("description", "").strip()

#         if not topic_name:
#             flash("Topic name is required.", "danger")
#             return redirect(url_for("edit_master_topic", topic_id=topic_id))

#         db.execute("""
#             UPDATE master_prep_topics
#             SET topic_name = ?, category = ?, description = ?
#             WHERE id = ?
#         """, (topic_name, category, description, topic_id))
#         db.commit()

#         flash("Master topic updated successfully.", "success")
#         return redirect(url_for("all_master_topics"))

#     return render_template("edit_master_topic.html", topic=topic)


# @app.route("/superadmin/delete-master-topic/<int:topic_id>", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def delete_master_topic(topic_id):
#     db = get_db()

#     topic = db.execute("""
#         SELECT * FROM master_prep_topics
#         WHERE id = ? AND is_active = 1
#     """, (topic_id,)).fetchone()

#     if not topic:
#         flash("Master topic not found.", "danger")
#         return redirect(url_for("all_master_topics"))

#     db.execute("UPDATE master_prep_topics SET is_active = 0 WHERE id = ?", (topic_id,))
#     db.execute("UPDATE master_prep_questions SET is_active = 0 WHERE topic_id = ?", (topic_id,))
#     db.commit()

#     flash("Master topic and its linked questions were deactivated.", "success")
#     return redirect(url_for("all_master_topics"))


# # ----------------------------
# # Superadmin master question routes
# # ----------------------------
# @app.route("/superadmin/add-master-question", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def add_master_question():
#     db = get_db()

#     topics = db.execute("""
#         SELECT id, topic_name FROM master_prep_topics
#         WHERE is_active = 1
#         ORDER BY topic_name ASC
#     """).fetchall()

#     if request.method == "POST":
#         topic_id = request.form.get("topic_id", "").strip()
#         question = request.form.get("question", "").strip()
#         answer = request.form.get("answer", "").strip()
#         difficulty = request.form.get("difficulty", "").strip()

#         if not topic_id or not question:
#             flash("Topic and question are required.", "danger")
#             return redirect(url_for("add_master_question"))

#         if difficulty not in ["", "Easy", "Medium", "Hard"]:
#             flash("Invalid difficulty selected.", "danger")
#             return redirect(url_for("add_master_question"))

#         try:
#             topic_id = int(topic_id)
#         except ValueError:
#             flash("Invalid topic selected.", "danger")
#             return redirect(url_for("add_master_question"))

#         topic = db.execute("""
#             SELECT id FROM master_prep_topics
#             WHERE id = ? AND is_active = 1
#         """, (topic_id,)).fetchone()

#         if not topic:
#             flash("Selected topic is invalid.", "danger")
#             return redirect(url_for("add_master_question"))

#         db.execute("""
#             INSERT INTO master_prep_questions (topic_id, question, answer, difficulty)
#             VALUES (?, ?, ?, ?)
#         """, (topic_id, question, answer, difficulty))
#         db.commit()

#         flash("Master question added successfully.", "success")
#         return redirect(url_for("all_master_questions"))

#     return render_template("add_master_question.html", topics=topics)


# @app.route("/superadmin/all-master-questions")
# @login_required
# @role_required("superadmin")
# def all_master_questions():
#     db = get_db()
#     search = request.args.get("search", "").strip()
#     difficulty = request.args.get("difficulty", "").strip()
#     topic_filter = request.args.get("topic_id", "").strip()

#     query = """
#         SELECT mpq.*, mpt.topic_name, mpt.category
#         FROM master_prep_questions mpq
#         INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
#         WHERE mpq.is_active = 1 AND mpt.is_active = 1
#     """
#     params = []

#     if search:
#         query += " AND (mpq.question LIKE ? OR mpq.answer LIKE ?)"
#         params.extend([f"%{search}%", f"%{search}%"])

#     if difficulty:
#         query += " AND mpq.difficulty = ?"
#         params.append(difficulty)

#     if topic_filter:
#         try:
#             topic_filter_int = int(topic_filter)
#             query += " AND mpq.topic_id = ?"
#             params.append(topic_filter_int)
#         except ValueError:
#             pass

#     query += " ORDER BY mpq.id DESC"

#     questions = db.execute(query, params).fetchall()
#     topics = db.execute("""
#         SELECT id, topic_name FROM master_prep_topics
#         WHERE is_active = 1
#         ORDER BY topic_name ASC
#     """).fetchall()

#     return render_template(
#         "all_master_questions.html",
#         questions=questions,
#         topics=topics,
#         search=search,
#         difficulty=difficulty,
#         topic_filter=topic_filter
#     )


# @app.route("/superadmin/edit-master-question/<int:question_id>", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def edit_master_question(question_id):
#     db = get_db()

#     question_row = db.execute("""
#         SELECT * FROM master_prep_questions
#         WHERE id = ? AND is_active = 1
#     """, (question_id,)).fetchone()

#     if not question_row:
#         flash("Master question not found.", "danger")
#         return redirect(url_for("all_master_questions"))

#     topics = db.execute("""
#         SELECT id, topic_name FROM master_prep_topics
#         WHERE is_active = 1
#         ORDER BY topic_name ASC
#     """).fetchall()

#     if request.method == "POST":
#         topic_id = request.form.get("topic_id", "").strip()
#         question = request.form.get("question", "").strip()
#         answer = request.form.get("answer", "").strip()
#         difficulty = request.form.get("difficulty", "").strip()

#         if not topic_id or not question:
#             flash("Topic and question are required.", "danger")
#             return redirect(url_for("edit_master_question", question_id=question_id))

#         try:
#             topic_id = int(topic_id)
#         except ValueError:
#             flash("Invalid topic selected.", "danger")
#             return redirect(url_for("edit_master_question", question_id=question_id))

#         db.execute("""
#             UPDATE master_prep_questions
#             SET topic_id = ?, question = ?, answer = ?, difficulty = ?
#             WHERE id = ?
#         """, (topic_id, question, answer, difficulty, question_id))
#         db.commit()

#         flash("Master question updated successfully.", "success")
#         return redirect(url_for("all_master_questions"))

#     return render_template("edit_master_question.html", question_row=question_row, topics=topics)


# @app.route("/superadmin/delete-master-question/<int:question_id>", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def delete_master_question(question_id):
#     db = get_db()
#     db.execute("""
#         UPDATE master_prep_questions
#         SET is_active = 0
#         WHERE id = ?
#     """, (question_id,))
#     db.commit()

#     flash("Master question deactivated successfully.", "success")
#     return redirect(url_for("all_master_questions"))


# # super admin job routes/ functions. 
# # create new job
# @app.route("/superadmin/add-job", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def add_job():
#     if request.method == "POST":
#         title = request.form.get("title")
#         company = request.form.get("company")
#         location = request.form.get("location")
#         salary = request.form.get("salary")
#         description = request.form.get("description")

#         db = get_db()
#         db.execute("""
#             INSERT INTO jobs (title, company, location, salary, description, created_by)
#             VALUES (?, ?, ?, ?, ?, ?)
#         """, (title, company, location, salary, description, session["user_id"]))
#         db.commit()

#         flash("Job added successfully", "success")
#         return redirect(url_for("all_jobs"))

#     return render_template("add_job.html")

# # view all jobs
# @app.route("/superadmin/all-jobs")
# @login_required
# @role_required("superadmin")
# def all_jobs():
#     search = request.args.get("search", "")

#     db = get_db()
#     jobs = db.execute("""
#         SELECT * FROM jobs
#         WHERE is_active = 1 AND (title LIKE ? OR company LIKE ?)
#         ORDER BY id DESC
#     """, (f"%{search}%", f"%{search}%")).fetchall()

#     return render_template("all_jobs.html", jobs=jobs)


# # view single job details
# @app.route("/superadmin/job/<int:job_id>")
# @login_required
# @role_required("superadmin")
# def single_job(job_id):
#     db = get_db()
#     job = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
#     return render_template("single_job.html", job=job)


# # update job details
# @app.route("/superadmin/edit-job/<int:job_id>", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def edit_job(job_id):
#     db = get_db()
#     job = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()

#     if request.method == "POST":
#         db.execute("""
#             UPDATE jobs SET title=?, company=?, location=?, salary=?, description=?
#             WHERE id=?
#         """, (
#             request.form["title"],
#             request.form["company"],
#             request.form["location"],
#             request.form["salary"],
#             request.form["description"],
#             job_id
#         ))
#         db.commit()
#         return redirect(url_for("all_jobs"))

#     return render_template("edit_job.html", job=job)


# # soft delete jobs
# @app.route("/superadmin/delete-job/<int:job_id>", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def delete_job(job_id):
#     db = get_db()
#     db.execute("UPDATE jobs SET is_active=0 WHERE id=?", (job_id,))
#     db.commit()
#     return redirect(url_for("all_jobs"))


# # hard delete job
# @app.route("/superadmin/hard-delete-job/<int:job_id>", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def hard_delete_job(job_id):
#     db = get_db()
#     db.execute("DELETE FROM jobs WHERE id=?", (job_id,))
#     db.commit()
#     return redirect(url_for("all_jobs"))


# # user applying for job 

# @app.route("/apply-job/<int:job_id>", methods=["GET", "POST"])
# @login_required
# def apply_job(job_id):
#     if request.method == "POST":
#         file = request.files["resume"]
#         filename = file.filename
#         file.save(os.path.join("uploads", filename))

#         db = get_db()
#         db.execute("""
#             INSERT INTO job_applications
#             (job_id, user_id, full_name, email, phone, resume, cover_letter)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         """, (
#             job_id,
#             session["user_id"],
#             request.form["full_name"],
#             request.form["email"],
#             request.form["phone"],
#             filename,
#             request.form["cover_letter"]
#         ))
#         db.commit()

#         flash("Applied successfully!", "success")
#         return redirect(url_for("user_jobs"))

#     return render_template("apply_job.html")


# # user can see his job applications 
# @app.route("/my-applications")
# @login_required
# def my_applications():
#     db = get_db()
#     apps = db.execute("""
#         SELECT ja.*, j.title
#         FROM job_applications ja
#         JOIN jobs j ON ja.job_id = j.id
#         WHERE ja.user_id=?
#     """, (session["user_id"],)).fetchall()

#     return render_template("my_applications.html", apps=apps)



# # superadmin can see all the job applications
# @app.route("/superadmin/applications")
# @login_required
# @role_required("superadmin")
# def all_applications():
#     db = get_db()
#     apps = db.execute("""
#         SELECT ja.*, j.title, u.full_name
#         FROM job_applications ja
#         JOIN jobs j ON ja.job_id = j.id
#         JOIN users u ON ja.user_id = u.id
#     """).fetchall()

#     return render_template("all_applications.html", apps=apps)


# # accept or reject the job applications. 
# @app.route("/superadmin/update-application/<int:app_id>/<status>")
# @login_required
# @role_required("superadmin")
# def update_application(app_id, status):
#     db = get_db()

#     db.execute("UPDATE job_applications SET status=? WHERE id=?", (status, app_id))

#     user = db.execute("SELECT user_id FROM job_applications WHERE id=?", (app_id,)).fetchone()

#     db.execute("""
#         INSERT INTO notifications (user_id, message)
#         VALUES (?, ?)
#     """, (user["user_id"], f"Your job application has been {status}"))

#     db.commit()
#     return redirect(url_for("all_applications"))


# # notifications about the job applications 
# @app.route("/notifications")
# @login_required
# def notifications():
#     db = get_db()
#     notes = db.execute("""
#         SELECT * FROM notifications
#         WHERE user_id=?
#         ORDER BY id DESC
#     """, (session["user_id"],)).fetchall()

#     return render_template("notifications.html", notes=notes)

# # ----------------------------
# # User topic selection routes
# # ----------------------------
# @app.route("/user/available-topics")
# @login_required
# @role_required("user")
# def available_topics():
#     db = get_db()
#     user_id = session.get("user_id")
#     search = request.args.get("search", "").strip()
#     category = request.args.get("category", "").strip()

#     query = """
#         SELECT mpt.*,
#                CASE WHEN ust.id IS NOT NULL THEN 1 ELSE 0 END AS already_selected
#         FROM master_prep_topics mpt
#         LEFT JOIN user_selected_topics ust
#           ON ust.topic_id = mpt.id AND ust.user_id = ?
#         WHERE mpt.is_active = 1
#     """
#     params = [user_id]

#     if search:
#         query += " AND (mpt.topic_name LIKE ? OR mpt.category LIKE ?)"
#         params.extend([f"%{search}%", f"%{search}%"])

#     if category:
#         query += " AND mpt.category = ?"
#         params.append(category)

#     query += " ORDER BY mpt.topic_name ASC"

#     topics = db.execute(query, params).fetchall()
#     categories = db.execute("""
#         SELECT DISTINCT category FROM master_prep_topics
#         WHERE is_active = 1 AND category IS NOT NULL AND category != ''
#         ORDER BY category ASC
#     """).fetchall()

#     return render_template(
#         "available_topics.html",
#         topics=topics,
#         search=search,
#         category=category,
#         categories=categories
#     )


# @app.route("/user/select-topic/<int:topic_id>", methods=["POST"])
# @login_required
# @role_required("user")
# def select_topic(topic_id):
#     db = get_db()
#     user_id = session.get("user_id")

#     topic = db.execute("""
#         SELECT id FROM master_prep_topics
#         WHERE id = ? AND is_active = 1
#     """, (topic_id,)).fetchone()

#     if not topic:
#         flash("Topic not found.", "danger")
#         return redirect(url_for("available_topics"))

#     existing = db.execute("""
#         SELECT id FROM user_selected_topics
#         WHERE user_id = ? AND topic_id = ?
#     """, (user_id, topic_id)).fetchone()

#     if existing:
#         flash("You already selected this topic.", "warning")
#         return redirect(url_for("available_topics"))

#     db.execute("""
#         INSERT INTO user_selected_topics (user_id, topic_id, progress_status, notes)
#         VALUES (?, ?, 'Not Started', '')
#     """, (user_id, topic_id))
#     db.commit()

#     flash("Topic added to your preparation list.", "success")
#     return redirect(url_for("my_topics"))


# @app.route("/user/my-topics")
# @login_required
# @role_required("user")
# def my_topics():
#     db = get_db()
#     user_id = session.get("user_id")

#     topics = db.execute("""
#         SELECT ust.*, mpt.topic_name, mpt.category, mpt.description
#         FROM user_selected_topics ust
#         INNER JOIN master_prep_topics mpt ON ust.topic_id = mpt.id
#         WHERE ust.user_id = ? AND mpt.is_active = 1
#         ORDER BY ust.id DESC
#     """, (user_id,)).fetchall()

#     return render_template("my_topics.html", topics=topics)


# @app.route("/user/update-my-topic/<int:selected_topic_id>", methods=["GET", "POST"])
# @login_required
# @role_required("user")
# def update_my_topic(selected_topic_id):
#     db = get_db()
#     user_id = session.get("user_id")

#     selected_topic = db.execute("""
#         SELECT ust.*, mpt.topic_name, mpt.category, mpt.description
#         FROM user_selected_topics ust
#         INNER JOIN master_prep_topics mpt ON ust.topic_id = mpt.id
#         WHERE ust.id = ? AND ust.user_id = ? AND mpt.is_active = 1
#     """, (selected_topic_id, user_id)).fetchone()

#     if not selected_topic:
#         flash("Selected topic not found.", "danger")
#         return redirect(url_for("my_topics"))

#     if request.method == "POST":
#         progress_status = request.form.get("progress_status", "").strip()
#         notes = request.form.get("notes", "").strip()

#         if progress_status not in ["Not Started", "In Progress", "Revised", "Mastered"]:
#             flash("Invalid progress status.", "danger")
#             return redirect(url_for("update_my_topic", selected_topic_id=selected_topic_id))

#         db.execute("""
#             UPDATE user_selected_topics
#             SET progress_status = ?, notes = ?
#             WHERE id = ? AND user_id = ?
#         """, (progress_status, notes, selected_topic_id, user_id))
#         db.commit()

#         flash("Your topic progress was updated successfully.", "success")
#         return redirect(url_for("my_topics"))

#     return render_template("update_my_topic.html", selected_topic=selected_topic)


# @app.route("/user/remove-my-topic/<int:selected_topic_id>", methods=["POST"])
# @login_required
# @role_required("user")
# def remove_my_topic(selected_topic_id):
#     db = get_db()
#     user_id = session.get("user_id")

#     topic_row = db.execute("""
#         SELECT topic_id FROM user_selected_topics
#         WHERE id = ? AND user_id = ?
#     """, (selected_topic_id, user_id)).fetchone()

#     if not topic_row:
#         flash("Selected topic not found.", "danger")
#         return redirect(url_for("my_topics"))

#     db.execute("""
#         DELETE FROM user_selected_topics
#         WHERE id = ? AND user_id = ?
#     """, (selected_topic_id, user_id))
#     db.execute("""
#         DELETE FROM user_selected_questions
#         WHERE user_id = ? AND question_id IN (
#             SELECT id FROM master_prep_questions WHERE topic_id = ?
#         )
#     """, (user_id, topic_row["topic_id"]))
#     db.commit()

#     flash("Topic removed from your preparation list.", "success")
#     return redirect(url_for("my_topics"))


# # ----------------------------
# # User question selection routes
# # ----------------------------
# @app.route("/user/available-questions")
# @login_required
# @role_required("user")
# def available_questions():
#     db = get_db()
#     user_id = session.get("user_id")

#     search = request.args.get("search", "").strip()
#     difficulty = request.args.get("difficulty", "").strip()
#     topic_filter = request.args.get("topic_id", "").strip()
#     my_topics_only = request.args.get("my_topics_only", "").strip()

#     query = """
#         SELECT mpq.*, mpt.topic_name, mpt.category,
#                CASE WHEN usq.id IS NOT NULL THEN 1 ELSE 0 END AS already_selected
#         FROM master_prep_questions mpq
#         INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
#         LEFT JOIN user_selected_questions usq
#           ON usq.question_id = mpq.id AND usq.user_id = ?
#         WHERE mpq.is_active = 1 AND mpt.is_active = 1
#     """
#     params = [user_id]

#     if search:
#         query += " AND (mpq.question LIKE ? OR mpq.answer LIKE ?)"
#         params.extend([f"%{search}%", f"%{search}%"])

#     if difficulty:
#         query += " AND mpq.difficulty = ?"
#         params.append(difficulty)

#     if topic_filter:
#         try:
#             topic_filter_int = int(topic_filter)
#             query += " AND mpq.topic_id = ?"
#             params.append(topic_filter_int)
#         except ValueError:
#             pass

#     if my_topics_only == "1":
#         query += """
#             AND mpq.topic_id IN (
#                 SELECT topic_id FROM user_selected_topics WHERE user_id = ?
#             )
#         """
#         params.append(user_id)

#     query += " ORDER BY mpq.id DESC"

#     questions = db.execute(query, params).fetchall()

#     topics = db.execute("""
#         SELECT id, topic_name FROM master_prep_topics
#         WHERE is_active = 1
#         ORDER BY topic_name ASC
#     """).fetchall()

#     return render_template(
#         "available_questions.html",
#         questions=questions,
#         topics=topics,
#         search=search,
#         difficulty=difficulty,
#         topic_filter=request.args.get("topic_id", ""),
#         my_topics_only=my_topics_only
#     )


# @app.route("/user/select-question/<int:question_id>", methods=["POST"])
# @login_required
# @role_required("user")
# def select_question(question_id):
#     db = get_db()
#     user_id = session.get("user_id")

#     question_row = db.execute("""
#         SELECT id FROM master_prep_questions
#         WHERE id = ? AND is_active = 1
#     """, (question_id,)).fetchone()

#     if not question_row:
#         flash("Question not found.", "danger")
#         return redirect(url_for("available_questions"))

#     existing = db.execute("""
#         SELECT id FROM user_selected_questions
#         WHERE user_id = ? AND question_id = ?
#     """, (user_id, question_id)).fetchone()

#     if existing:
#         flash("You already selected this question.", "warning")
#         return redirect(url_for("available_questions"))

#     db.execute("""
#         INSERT INTO user_selected_questions (user_id, question_id, is_important, personal_notes)
#         VALUES (?, ?, 0, '')
#     """, (user_id, question_id))
#     db.commit()

#     flash("Question added to your personal question bank.", "success")
#     return redirect(url_for("my_questions"))


# @app.route("/user/my-questions")
# @login_required
# @role_required("user")
# def my_questions():
#     db = get_db()
#     user_id = session.get("user_id")

#     search = request.args.get("search", "").strip()
#     important = request.args.get("important", "").strip()

#     query = """
#         SELECT usq.*, mpq.question, mpq.answer, mpq.difficulty, mpt.topic_name
#         FROM user_selected_questions usq
#         INNER JOIN master_prep_questions mpq ON usq.question_id = mpq.id
#         INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
#         WHERE usq.user_id = ? AND mpq.is_active = 1 AND mpt.is_active = 1
#     """
#     params = [user_id]

#     if search:
#         query += " AND (mpq.question LIKE ? OR mpq.answer LIKE ? OR mpt.topic_name LIKE ?)"
#         params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

#     if important == "1":
#         query += " AND usq.is_important = 1"

#     query += " ORDER BY usq.id DESC"

#     questions = db.execute(query, params).fetchall()
#     return render_template("my_questions.html", questions=questions, search=search, important=important)


# @app.route("/user/update-my-question/<int:selected_question_id>", methods=["GET", "POST"])
# @login_required
# @role_required("user")
# def update_my_question(selected_question_id):
#     db = get_db()
#     user_id = session.get("user_id")

#     selected_question = db.execute("""
#         SELECT usq.*, mpq.question, mpq.answer, mpq.difficulty, mpt.topic_name
#         FROM user_selected_questions usq
#         INNER JOIN master_prep_questions mpq ON usq.question_id = mpq.id
#         INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
#         WHERE usq.id = ? AND usq.user_id = ? AND mpq.is_active = 1 AND mpt.is_active = 1
#     """, (selected_question_id, user_id)).fetchone()

#     if not selected_question:
#         flash("Selected question not found.", "danger")
#         return redirect(url_for("my_questions"))

#     if request.method == "POST":
#         is_important = 1 if request.form.get("is_important") == "on" else 0
#         personal_notes = request.form.get("personal_notes", "").strip()

#         db.execute("""
#             UPDATE user_selected_questions
#             SET is_important = ?, personal_notes = ?
#             WHERE id = ? AND user_id = ?
#         """, (is_important, personal_notes, selected_question_id, user_id))
#         db.commit()

#         flash("Your question preferences were updated successfully.", "success")
#         return redirect(url_for("my_questions"))

#     return render_template("update_my_question.html", selected_question=selected_question)


# @app.route("/user/remove-my-question/<int:selected_question_id>", methods=["POST"])
# @login_required
# @role_required("user")
# def remove_my_question(selected_question_id):
#     db = get_db()
#     user_id = session.get("user_id")

#     db.execute("""
#         DELETE FROM user_selected_questions
#         WHERE id = ? AND user_id = ?
#     """, (selected_question_id, user_id))
#     db.commit()

#     flash("Question removed from your personal bank.", "success")
#     return redirect(url_for("my_questions"))


# # ----------------------------
# # Superadmin user management
# # ----------------------------
# @app.route("/superadmin/all-users")
# @login_required
# @role_required("superadmin")
# def all_users():
#     db = get_db()

#     active_users = db.execute("""
#         SELECT id, full_name, email, role, created_at
#         FROM users
#         WHERE is_deleted = 0
#         ORDER BY id DESC
#     """).fetchall()

#     deleted_users = db.execute("""
#         SELECT id, full_name, email, role, created_at, deleted_at
#         FROM users
#         WHERE is_deleted = 1
#         ORDER BY id DESC
#     """).fetchall()

#     return render_template(
#         "all_users.html",
#         active_users=active_users,
#         deleted_users=deleted_users
#     )


# @app.route("/superadmin/update-role/<int:user_id>", methods=["GET", "POST"])
# @login_required
# @role_required("superadmin")
# def update_role(user_id):
#     db = get_db()
#     user = db.execute("""
#         SELECT id, full_name, email, role, created_at, is_deleted
#         FROM users
#         WHERE id = ?
#     """, (user_id,)).fetchone()

#     if not user:
#         flash("User not found.", "danger")
#         return redirect(url_for("all_users"))

#     if request.method == "POST":
#         if user["id"] == session.get("user_id"):
#             flash("You cannot change your own role from this page.", "warning")
#             return redirect(url_for("update_role", user_id=user_id))

#         new_role = request.form.get("role", "").strip()

#         if new_role not in ["superadmin", "user"]:
#             flash("Invalid role selected.", "danger")
#             return redirect(url_for("update_role", user_id=user_id))

#         db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
#         db.commit()

#         flash("User role updated successfully.", "success")
#         return redirect(url_for("all_users"))

#     return render_template("update_role.html", user=user)


# @app.route("/superadmin/soft-delete-users", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def soft_delete_users():
#     selected_user_ids = request.form.getlist("selected_users")

#     if not selected_user_ids:
#         flash("Please select at least one user to soft delete.", "warning")
#         return redirect(url_for("all_users"))

#     db = get_db()

#     safe_ids = []
#     for uid in selected_user_ids:
#         try:
#             parsed_id = int(uid)
#             if parsed_id != session.get("user_id"):
#                 safe_ids.append(parsed_id)
#         except ValueError:
#             continue

#     if not safe_ids:
#         flash("No valid users selected for soft delete.", "warning")
#         return redirect(url_for("all_users"))

#     placeholders = ",".join(["?"] * len(safe_ids))
#     query = f"""
#         UPDATE users
#         SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
#         WHERE id IN ({placeholders})
#     """
#     db.execute(query, safe_ids)
#     db.commit()

#     flash("Selected users soft deleted successfully.", "success")
#     return redirect(url_for("all_users"))


# @app.route("/superadmin/hard-delete-users", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def hard_delete_users():
#     selected_user_ids = request.form.getlist("selected_users")

#     if not selected_user_ids:
#         flash("Please select at least one user to hard delete.", "warning")
#         return redirect(url_for("all_users"))

#     db = get_db()

#     safe_ids = []
#     for uid in selected_user_ids:
#         try:
#             parsed_id = int(uid)
#             if parsed_id != session.get("user_id"):
#                 safe_ids.append(parsed_id)
#         except ValueError:
#             continue

#     if not safe_ids:
#         flash("No valid users selected for hard delete.", "warning")
#         return redirect(url_for("all_users"))

#     placeholders = ",".join(["?"] * len(safe_ids))
#     query = f"DELETE FROM users WHERE id IN ({placeholders})"
#     db.execute(query, safe_ids)
#     db.commit()

#     flash("Selected users hard deleted permanently.", "success")
#     return redirect(url_for("all_users"))


# @app.route("/superadmin/restore-users", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def restore_users():
#     selected_user_ids = request.form.getlist("selected_deleted_users")

#     if not selected_user_ids:
#         flash("Please select at least one deleted user to restore.", "warning")
#         return redirect(url_for("all_users"))

#     db = get_db()

#     safe_ids = []
#     for uid in selected_user_ids:
#         try:
#             safe_ids.append(int(uid))
#         except ValueError:
#             continue

#     if not safe_ids:
#         flash("No valid deleted users selected.", "warning")
#         return redirect(url_for("all_users"))

#     placeholders = ",".join(["?"] * len(safe_ids))
#     query = f"""
#         UPDATE users
#         SET is_deleted = 0, deleted_at = NULL
#         WHERE id IN ({placeholders})
#     """
#     db.execute(query, safe_ids)
#     db.commit()

#     flash("Selected users restored successfully.", "success")
#     return redirect(url_for("all_users"))


# @app.route("/superadmin/delete-all-users-soft", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def delete_all_users_soft():
#     db = get_db()

#     db.execute("""
#         UPDATE users
#         SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
#         WHERE role = 'user' AND is_deleted = 0
#     """)
#     db.commit()

#     flash("All normal users soft deleted successfully.", "success")
#     return redirect(url_for("all_users"))


# @app.route("/superadmin/delete-all-users-hard", methods=["POST"])
# @login_required
# @role_required("superadmin")
# def delete_all_users_hard():
#     db = get_db()

#     db.execute("""
#         DELETE FROM users
#         WHERE role = 'user'
#     """)
#     db.commit()

#     flash("All normal users hard deleted permanently.", "success")
#     return redirect(url_for("all_users"))


# # ----------------------------
# # Logout
# # ----------------------------
# @app.route("/logout")
# @login_required
# def logout():
#     session.clear()
#     flash("You have been logged out successfully.", "info")
#     return redirect(url_for("login"))


# # ----------------------------
# # Run app
# # ----------------------------
# if __name__ == "__main__":
#     init_db()
#     add_missing_columns()
#     app.run(debug=True)

import os
import sqlite3
import secrets
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g,
    send_from_directory,
    abort,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

print("TEMPLATE FOLDER:", os.path.abspath("templates"))

app = Flask(__name__)
app.secret_key = "super-secret-key-change-this-in-production"

DATABASE = "job_tracker.db"
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# Database helpers
# ----------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def add_column_if_missing(cursor, table_name, column_name, column_definition):
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if column_name not in columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            )
    except sqlite3.OperationalError:
        pass


def table_exists(cursor, table_name):
    row = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def add_missing_columns():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # ---------------- USERS TABLE ----------------
    if table_exists(cursor, "users"):
        add_column_if_missing(cursor, "users", "is_deleted", "INTEGER DEFAULT 0")
        add_column_if_missing(cursor, "users", "deleted_at", "TIMESTAMP NULL")
        add_column_if_missing(
            cursor, "users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )

    # ---------------- PASSWORD_RESETS TABLE ----------------
    if table_exists(cursor, "password_resets"):
        add_column_if_missing(
            cursor, "password_resets", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )

    # ---------------- MASTER_PREP_TOPICS TABLE ----------------
    if table_exists(cursor, "master_prep_topics"):
        add_column_if_missing(cursor, "master_prep_topics", "category", "TEXT")
        add_column_if_missing(cursor, "master_prep_topics", "description", "TEXT")
        add_column_if_missing(cursor, "master_prep_topics", "is_active", "INTEGER DEFAULT 1")
        add_column_if_missing(cursor, "master_prep_topics", "created_by", "INTEGER")
        add_column_if_missing(
            cursor,
            "master_prep_topics",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

    # ---------------- MASTER_PREP_QUESTIONS TABLE ----------------
    if table_exists(cursor, "master_prep_questions"):
        add_column_if_missing(cursor, "master_prep_questions", "answer", "TEXT")
        add_column_if_missing(cursor, "master_prep_questions", "difficulty", "TEXT")
        add_column_if_missing(
            cursor, "master_prep_questions", "is_active", "INTEGER DEFAULT 1"
        )
        add_column_if_missing(
            cursor,
            "master_prep_questions",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

    # ---------------- USER_SELECTED_TOPICS TABLE ----------------
    if table_exists(cursor, "user_selected_topics"):
        add_column_if_missing(
            cursor,
            "user_selected_topics",
            "progress_status",
            "TEXT DEFAULT 'Not Started'",
        )
        add_column_if_missing(cursor, "user_selected_topics", "notes", "TEXT")
        add_column_if_missing(
            cursor,
            "user_selected_topics",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

    # ---------------- USER_SELECTED_QUESTIONS TABLE ----------------
    if table_exists(cursor, "user_selected_questions"):
        add_column_if_missing(
            cursor, "user_selected_questions", "is_important", "INTEGER DEFAULT 0"
        )
        add_column_if_missing(cursor, "user_selected_questions", "personal_notes", "TEXT")
        add_column_if_missing(
            cursor,
            "user_selected_questions",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

    # ---------------- JOBS TABLE ----------------
    if table_exists(cursor, "jobs"):
        add_column_if_missing(cursor, "jobs", "company", "TEXT")
        add_column_if_missing(cursor, "jobs", "location", "TEXT")
        add_column_if_missing(cursor, "jobs", "salary", "TEXT")
        add_column_if_missing(cursor, "jobs", "description", "TEXT")
        add_column_if_missing(cursor, "jobs", "is_active", "INTEGER DEFAULT 1")
        add_column_if_missing(cursor, "jobs", "created_by", "INTEGER")
        add_column_if_missing(cursor, "jobs", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # ---------------- JOB_APPLICATIONS TABLE ----------------
    if table_exists(cursor, "job_applications"):
        add_column_if_missing(cursor, "job_applications", "full_name", "TEXT")
        add_column_if_missing(cursor, "job_applications", "email", "TEXT")
        add_column_if_missing(cursor, "job_applications", "phone", "TEXT")
        add_column_if_missing(cursor, "job_applications", "resume", "TEXT")
        add_column_if_missing(cursor, "job_applications", "cover_letter", "TEXT")
        add_column_if_missing(cursor, "job_applications", "status", "TEXT DEFAULT 'Pending'")
        add_column_if_missing(
            cursor,
            "job_applications",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

    # ---------------- NOTIFICATIONS TABLE ----------------
    if table_exists(cursor, "notifications"):
        add_column_if_missing(cursor, "notifications", "message", "TEXT")
        add_column_if_missing(cursor, "notifications", "is_read", "INTEGER DEFAULT 0")
        add_column_if_missing(
            cursor,
            "notifications",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

    db.commit()
    db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('superadmin', 'user')),
            is_deleted INTEGER DEFAULT 0,
            deleted_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_prep_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_prep_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            difficulty TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (topic_id) REFERENCES master_prep_topics(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_selected_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            progress_status TEXT DEFAULT 'Not Started',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, topic_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (topic_id) REFERENCES master_prep_topics(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_selected_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            is_important INTEGER DEFAULT 0,
            personal_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, question_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES master_prep_questions(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            salary TEXT,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            resume TEXT,
            cover_letter TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute("SELECT * FROM users WHERE email = ?", ("superadmin@jobtrackerai.com",))
    superadmin = cursor.fetchone()

    if not superadmin:
        cursor.execute(
            """
            INSERT INTO users (full_name, email, password, role, is_deleted)
            VALUES (?, ?, ?, ?, 0)
            """,
            (
                "Super Admin",
                "superadmin@jobtrackerai.com",
                generate_password_hash("Admin@123"),
                "superadmin",
            ),
        )

    db.commit()
    db.close()


# ----------------------------
# Utility helpers
# ----------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_resume_file(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    safe_name = secure_filename(file_storage.filename)
    unique_name = f"{secrets.token_hex(8)}_{safe_name}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file_storage.save(file_path)
    return unique_name


# ----------------------------
# Auth decorators
# ----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))

            if session.get("role") != required_role:
                flash("You are not authorized to access this page.", "danger")
                return redirect(url_for("login"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ----------------------------
# Context processor
# ----------------------------
@app.context_processor
def inject_user():
    unread_notifications = 0

    if "user_id" in session:
        try:
            db = get_db()
            unread_notifications = db.execute(
                """
                SELECT COUNT(*) AS count
                FROM notifications
                WHERE user_id = ? AND is_read = 0
                """,
                (session.get("user_id"),),
            ).fetchone()["count"]
        except Exception:
            unread_notifications = 0

    return {
        "current_user_name": session.get("full_name"),
        "current_user_role": session.get("role"),
        "current_user_id": session.get("user_id"),
        "is_logged_in": "user_id" in session,
        "unread_notifications_count": unread_notifications,
    }


# ----------------------------
# Public routes
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "user").strip()

        if not full_name or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if role not in ["superadmin", "user"]:
            flash("Invalid role selected.", "danger")
            return redirect(url_for("register"))

        db = get_db()
        cursor = db.cursor()

        existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if existing_user and existing_user["is_deleted"] == 0:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        if existing_user and existing_user["is_deleted"] == 1:
            flash("This email belongs to a deleted account. Please contact superadmin.", "warning")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password, role, is_deleted)
            VALUES (?, ?, ?, ?, 0)
            """,
            (full_name, email, hashed_password, role),
        )
        db.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("login"))

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ? AND is_deleted = 0",
            (email,),
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash("Login successful.", "success")

            if user["role"] == "superadmin":
                return redirect(url_for("super_admin_dashboard"))
            return redirect(url_for("user_dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email.", "danger")
            return redirect(url_for("forgot_password"))

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ? AND is_deleted = 0",
            (email,),
        ).fetchone()

        if not user:
            flash("No active account found with that email.", "warning")
            return redirect(url_for("forgot_password"))

        token = secrets.token_urlsafe(32)

        db.execute("INSERT INTO password_resets (email, token) VALUES (?, ?)", (email, token))
        db.commit()

        reset_link = url_for("reset_password", token=token, _external=True)
        flash("Password reset link generated successfully.", "success")

    return render_template("forgot_password.html", reset_link=reset_link)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    db = get_db()
    reset_record = db.execute("SELECT * FROM password_resets WHERE token = ?", (token,)).fetchone()

    if not reset_record:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not password or not confirm_password:
            flash("Both password fields are required.", "danger")
            return redirect(url_for("reset_password", token=token))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password", token=token))

        hashed_password = generate_password_hash(password)

        db.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, reset_record["email"]))
        db.execute("DELETE FROM password_resets WHERE email = ?", (reset_record["email"],))
        db.commit()

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


# ----------------------------
# Dashboard routes
# ----------------------------
@app.route("/superadmin/dashboard")
@login_required
@role_required("superadmin")
def super_admin_dashboard():
    db = get_db()

    total_users = db.execute(
        """
        SELECT COUNT(*) AS count FROM users
        WHERE role = 'user' AND is_deleted = 0
        """
    ).fetchone()["count"]

    total_superadmins = db.execute(
        """
        SELECT COUNT(*) AS count FROM users
        WHERE role = 'superadmin' AND is_deleted = 0
        """
    ).fetchone()["count"]

    deleted_users_count = db.execute(
        """
        SELECT COUNT(*) AS count FROM users
        WHERE is_deleted = 1
        """
    ).fetchone()["count"]

    total_master_topics = db.execute(
        """
        SELECT COUNT(*) AS count FROM master_prep_topics WHERE is_active = 1
        """
    ).fetchone()["count"]

    total_master_questions = db.execute(
        """
        SELECT COUNT(*) AS count FROM master_prep_questions WHERE is_active = 1
        """
    ).fetchone()["count"]

    total_jobs = db.execute(
        """
        SELECT COUNT(*) AS count FROM jobs WHERE is_active = 1
        """
    ).fetchone()["count"]

    total_job_applications = db.execute(
        """
        SELECT COUNT(*) AS count FROM job_applications
        """
    ).fetchone()["count"]

    recent_users = db.execute(
        """
        SELECT id, full_name, email, role, created_at
        FROM users
        WHERE is_deleted = 0
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    return render_template(
        "super_admin_dashboard.html",
        total_users=total_users,
        total_superadmins=total_superadmins,
        deleted_users_count=deleted_users_count,
        total_master_topics=total_master_topics,
        total_master_questions=total_master_questions,
        total_jobs=total_jobs,
        total_job_applications=total_job_applications,
        recent_users=recent_users,
    )


@app.route("/user/dashboard")
@login_required
@role_required("user")
def user_dashboard():
    db = get_db()
    user_id = session.get("user_id")

    total_selected_topics = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM user_selected_topics
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()["count"]

    completed_topics = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM user_selected_topics
        WHERE user_id = ? AND progress_status = 'Mastered'
        """,
        (user_id,),
    ).fetchone()["count"]

    total_selected_questions = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM user_selected_questions
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()["count"]

    important_questions = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM user_selected_questions
        WHERE user_id = ? AND is_important = 1
        """,
        (user_id,),
    ).fetchone()["count"]

    recent_topics = db.execute(
        """
        SELECT ust.id, ust.progress_status, ust.created_at, mpt.topic_name, mpt.category
        FROM user_selected_topics ust
        INNER JOIN master_prep_topics mpt ON ust.topic_id = mpt.id
        WHERE ust.user_id = ?
        ORDER BY ust.id DESC
        LIMIT 5
        """,
        (user_id,),
    ).fetchall()

    available_topic_count = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM master_prep_topics
        WHERE is_active = 1
        """
    ).fetchone()["count"]

    my_applications_count = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM job_applications
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()["count"]

    return render_template(
        "user_dashboard.html",
        total_selected_topics=total_selected_topics,
        completed_topics=completed_topics,
        total_selected_questions=total_selected_questions,
        important_questions=important_questions,
        recent_topics=recent_topics,
        available_topic_count=available_topic_count,
        my_applications_count=my_applications_count,
    )


# ----------------------------
# Superadmin master topic routes
# ----------------------------
@app.route("/superadmin/add-master-topic", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def add_master_topic():
    if request.method == "POST":
        topic_name = request.form.get("topic_name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        if not topic_name:
            flash("Topic name is required.", "danger")
            return redirect(url_for("add_master_topic"))

        db = get_db()

        existing = db.execute(
            """
            SELECT id FROM master_prep_topics
            WHERE LOWER(topic_name) = LOWER(?) AND is_active = 1
            """,
            (topic_name,),
        ).fetchone()

        if existing:
            flash("This topic already exists.", "warning")
            return redirect(url_for("all_master_topics"))

        db.execute(
            """
            INSERT INTO master_prep_topics (topic_name, category, description, created_by)
            VALUES (?, ?, ?, ?)
            """,
            (topic_name, category, description, session.get("user_id")),
        )
        db.commit()

        flash("Master topic added successfully.", "success")
        return redirect(url_for("all_master_topics"))

    return render_template("add_master_topic.html")


@app.route("/superadmin/all-master-topics")
@login_required
@role_required("superadmin")
def all_master_topics():
    db = get_db()
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = """
        SELECT mpt.*,
               (SELECT COUNT(*) FROM master_prep_questions mpq WHERE mpq.topic_id = mpt.id AND mpq.is_active = 1) AS questions_count
        FROM master_prep_topics mpt
        WHERE mpt.is_active = 1
    """
    params = []

    if search:
        query += " AND (mpt.topic_name LIKE ? OR mpt.category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND mpt.category = ?"
        params.append(category)

    query += " ORDER BY mpt.topic_name ASC"

    topics = db.execute(query, params).fetchall()
    categories = db.execute(
        """
        SELECT DISTINCT category FROM master_prep_topics
        WHERE is_active = 1 AND category IS NOT NULL AND category != ''
        ORDER BY category ASC
        """
    ).fetchall()

    return render_template(
        "all_master_topics.html",
        topics=topics,
        search=search,
        category=category,
        categories=categories,
    )


@app.route("/superadmin/edit-master-topic/<int:topic_id>", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def edit_master_topic(topic_id):
    db = get_db()
    topic = db.execute(
        """
        SELECT * FROM master_prep_topics
        WHERE id = ? AND is_active = 1
        """,
        (topic_id,),
    ).fetchone()

    if not topic:
        flash("Master topic not found.", "danger")
        return redirect(url_for("all_master_topics"))

    if request.method == "POST":
        topic_name = request.form.get("topic_name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        if not topic_name:
            flash("Topic name is required.", "danger")
            return redirect(url_for("edit_master_topic", topic_id=topic_id))

        db.execute(
            """
            UPDATE master_prep_topics
            SET topic_name = ?, category = ?, description = ?
            WHERE id = ?
            """,
            (topic_name, category, description, topic_id),
        )
        db.commit()

        flash("Master topic updated successfully.", "success")
        return redirect(url_for("all_master_topics"))

    return render_template("edit_master_topic.html", topic=topic)


@app.route("/superadmin/delete-master-topic/<int:topic_id>", methods=["POST"])
@login_required
@role_required("superadmin")
def delete_master_topic(topic_id):
    db = get_db()

    topic = db.execute(
        """
        SELECT * FROM master_prep_topics
        WHERE id = ? AND is_active = 1
        """,
        (topic_id,),
    ).fetchone()

    if not topic:
        flash("Master topic not found.", "danger")
        return redirect(url_for("all_master_topics"))

    db.execute("UPDATE master_prep_topics SET is_active = 0 WHERE id = ?", (topic_id,))
    db.execute("UPDATE master_prep_questions SET is_active = 0 WHERE topic_id = ?", (topic_id,))
    db.commit()

    flash("Master topic and its linked questions were deactivated.", "success")
    return redirect(url_for("all_master_topics"))


# ----------------------------
# Superadmin master question routes
# ----------------------------
@app.route("/superadmin/add-master-question", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def add_master_question():
    db = get_db()

    topics = db.execute(
        """
        SELECT id, topic_name FROM master_prep_topics
        WHERE is_active = 1
        ORDER BY topic_name ASC
        """
    ).fetchall()

    if request.method == "POST":
        topic_id = request.form.get("topic_id", "").strip()
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer", "").strip()
        difficulty = request.form.get("difficulty", "").strip()

        if not topic_id or not question:
            flash("Topic and question are required.", "danger")
            return redirect(url_for("add_master_question"))

        if difficulty not in ["", "Easy", "Medium", "Hard"]:
            flash("Invalid difficulty selected.", "danger")
            return redirect(url_for("add_master_question"))

        try:
            topic_id = int(topic_id)
        except ValueError:
            flash("Invalid topic selected.", "danger")
            return redirect(url_for("add_master_question"))

        topic = db.execute(
            """
            SELECT id FROM master_prep_topics
            WHERE id = ? AND is_active = 1
            """,
            (topic_id,),
        ).fetchone()

        if not topic:
            flash("Selected topic is invalid.", "danger")
            return redirect(url_for("add_master_question"))

        db.execute(
            """
            INSERT INTO master_prep_questions (topic_id, question, answer, difficulty)
            VALUES (?, ?, ?, ?)
            """,
            (topic_id, question, answer, difficulty),
        )
        db.commit()

        flash("Master question added successfully.", "success")
        return redirect(url_for("all_master_questions"))

    return render_template("add_master_question.html", topics=topics)


@app.route("/superadmin/all-master-questions")
@login_required
@role_required("superadmin")
def all_master_questions():
    db = get_db()
    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    topic_filter = request.args.get("topic_id", "").strip()

    query = """
        SELECT mpq.*, mpt.topic_name, mpt.category
        FROM master_prep_questions mpq
        INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
        WHERE mpq.is_active = 1 AND mpt.is_active = 1
    """
    params = []

    if search:
        query += " AND (mpq.question LIKE ? OR mpq.answer LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if difficulty:
        query += " AND mpq.difficulty = ?"
        params.append(difficulty)

    if topic_filter:
        try:
            topic_filter_int = int(topic_filter)
            query += " AND mpq.topic_id = ?"
            params.append(topic_filter_int)
        except ValueError:
            pass

    query += " ORDER BY mpq.id DESC"

    questions = db.execute(query, params).fetchall()
    topics = db.execute(
        """
        SELECT id, topic_name FROM master_prep_topics
        WHERE is_active = 1
        ORDER BY topic_name ASC
        """
    ).fetchall()

    return render_template(
        "all_master_questions.html",
        questions=questions,
        topics=topics,
        search=search,
        difficulty=difficulty,
        topic_filter=topic_filter,
    )


@app.route("/superadmin/edit-master-question/<int:question_id>", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def edit_master_question(question_id):
    db = get_db()

    question_row = db.execute(
        """
        SELECT * FROM master_prep_questions
        WHERE id = ? AND is_active = 1
        """,
        (question_id,),
    ).fetchone()

    if not question_row:
        flash("Master question not found.", "danger")
        return redirect(url_for("all_master_questions"))

    topics = db.execute(
        """
        SELECT id, topic_name FROM master_prep_topics
        WHERE is_active = 1
        ORDER BY topic_name ASC
        """
    ).fetchall()

    if request.method == "POST":
        topic_id = request.form.get("topic_id", "").strip()
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer", "").strip()
        difficulty = request.form.get("difficulty", "").strip()

        if not topic_id or not question:
            flash("Topic and question are required.", "danger")
            return redirect(url_for("edit_master_question", question_id=question_id))

        try:
            topic_id = int(topic_id)
        except ValueError:
            flash("Invalid topic selected.", "danger")
            return redirect(url_for("edit_master_question", question_id=question_id))

        db.execute(
            """
            UPDATE master_prep_questions
            SET topic_id = ?, question = ?, answer = ?, difficulty = ?
            WHERE id = ?
            """,
            (topic_id, question, answer, difficulty, question_id),
        )
        db.commit()

        flash("Master question updated successfully.", "success")
        return redirect(url_for("all_master_questions"))

    return render_template("edit_master_question.html", question_row=question_row, topics=topics)


@app.route("/superadmin/delete-master-question/<int:question_id>", methods=["POST"])
@login_required
@role_required("superadmin")
def delete_master_question(question_id):
    db = get_db()
    db.execute(
        """
        UPDATE master_prep_questions
        SET is_active = 0
        WHERE id = ?
        """,
        (question_id,),
    )
    db.commit()

    flash("Master question deactivated successfully.", "success")
    return redirect(url_for("all_master_questions"))


# ----------------------------
# Job tracker - Superadmin job routes
# ----------------------------
@app.route("/superadmin/add-job", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def add_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Job title is required.", "danger")
            return redirect(url_for("add_job"))

        db = get_db()
        db.execute(
            """
            INSERT INTO jobs (title, company, location, salary, description, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, company, location, salary, description, session["user_id"]),
        )
        db.commit()

        flash("Job added successfully.", "success")
        return redirect(url_for("all_jobs"))

    return render_template("add_job.html")


@app.route("/superadmin/all-jobs")
@login_required
@role_required("superadmin")
def all_jobs():
    search = request.args.get("search", "").strip()

    db = get_db()
    jobs = db.execute(
        """
        SELECT *
        FROM jobs
        WHERE is_active = 1
          AND (title LIKE ? OR company LIKE ? OR location LIKE ?)
        ORDER BY id DESC
        """,
        (f"%{search}%", f"%{search}%", f"%{search}%"),
    ).fetchall()

    return render_template("all_jobs.html", jobs=jobs, search=search)


@app.route("/superadmin/job/<int:job_id>")
@login_required
@role_required("superadmin")
def single_job(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("all_jobs"))

    return render_template("single_job.html", job=job)


@app.route("/superadmin/edit-job/<int:job_id>", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def edit_job(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("all_jobs"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Job title is required.", "danger")
            return redirect(url_for("edit_job", job_id=job_id))

        db.execute(
            """
            UPDATE jobs
            SET title = ?, company = ?, location = ?, salary = ?, description = ?
            WHERE id = ?
            """,
            (title, company, location, salary, description, job_id),
        )
        db.commit()

        flash("Job updated successfully.", "success")
        return redirect(url_for("all_jobs"))

    return render_template("edit_job.html", job=job)


@app.route("/superadmin/delete-job/<int:job_id>", methods=["POST"])
@login_required
@role_required("superadmin")
def delete_job(job_id):
    db = get_db()

    job = db.execute(
        "SELECT id FROM jobs WHERE id = ? AND is_active = 1",
        (job_id,),
    ).fetchone()

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("all_jobs"))

    db.execute("UPDATE jobs SET is_active = 0 WHERE id = ?", (job_id,))
    db.commit()

    flash("Job soft deleted successfully.", "success")
    return redirect(url_for("all_jobs"))


@app.route("/superadmin/hard-delete-job/<int:job_id>", methods=["POST"])
@login_required
@role_required("superadmin")
def hard_delete_job(job_id):
    db = get_db()

    job = db.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("all_jobs"))

    db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    db.commit()

    flash("Job hard deleted successfully.", "success")
    return redirect(url_for("all_jobs"))


# ----------------------------
# Job tracker - Public/User job browsing
# ----------------------------
@app.route("/jobs")
def user_jobs():
    db = get_db()
    search = request.args.get("search", "").strip()

    jobs = db.execute(
        """
        SELECT *
        FROM jobs
        WHERE is_active = 1
          AND (title LIKE ? OR company LIKE ? OR location LIKE ?)
        ORDER BY id DESC
        """,
        (f"%{search}%", f"%{search}%", f"%{search}%"),
    ).fetchall()

    return render_template("user_jobs.html", jobs=jobs, search=search)


@app.route("/jobs/<int:job_id>")
def user_single_job(job_id):
    db = get_db()
    job = db.execute(
        "SELECT * FROM jobs WHERE id = ? AND is_active = 1",
        (job_id,),
    ).fetchone()

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("user_jobs"))

    return render_template("user_single_job.html", job=job)


@app.route("/apply-job/<int:job_id>", methods=["GET", "POST"])
@login_required
@role_required("user")
def apply_job(job_id):
    db = get_db()

    job = db.execute(
        "SELECT * FROM jobs WHERE id = ? AND is_active = 1",
        (job_id,),
    ).fetchone()

    if not job:
        flash("Job not found or inactive.", "danger")
        return redirect(url_for("user_jobs"))

    existing_application = db.execute(
        """
        SELECT id
        FROM job_applications
        WHERE job_id = ? AND user_id = ?
        """,
        (job_id, session["user_id"]),
    ).fetchone()

    if existing_application:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("my_applications"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        cover_letter = request.form.get("cover_letter", "").strip()
        resume_file = request.files.get("resume")

        if not full_name or not email or not phone or not cover_letter:
            flash("All fields are required.", "danger")
            return redirect(url_for("apply_job", job_id=job_id))

        if not resume_file or not resume_file.filename:
            flash("Please upload your resume.", "danger")
            return redirect(url_for("apply_job", job_id=job_id))

        saved_resume_name = save_resume_file(resume_file)
        if not saved_resume_name:
            flash("Only PDF, DOC, and DOCX files are allowed.", "danger")
            return redirect(url_for("apply_job", job_id=job_id))

        db.execute(
            """
            INSERT INTO job_applications
            (job_id, user_id, full_name, email, phone, resume, cover_letter, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')
            """,
            (
                job_id,
                session["user_id"],
                full_name,
                email,
                phone,
                saved_resume_name,
                cover_letter,
            ),
        )
        db.commit()

        flash("Applied successfully!", "success")
        return redirect(url_for("my_applications"))

    return render_template("apply_job.html", job=job)


@app.route("/my-applications")
@login_required
@role_required("user")
def my_applications():
    db = get_db()
    apps = db.execute(
        """
        SELECT ja.*, j.title, j.company, j.location
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        WHERE ja.user_id = ?
        ORDER BY ja.id DESC
        """,
        (session["user_id"],),
    ).fetchall()

    return render_template("my_applications.html", apps=apps)


@app.route("/edit-my-application/<int:application_id>", methods=["GET", "POST"])
@login_required
@role_required("user")
def edit_my_application(application_id):
    db = get_db()

    application = db.execute(
        """
        SELECT ja.*, j.title
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        WHERE ja.id = ? AND ja.user_id = ?
        """,
        (application_id, session["user_id"]),
    ).fetchone()

    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("my_applications"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        cover_letter = request.form.get("cover_letter", "").strip()
        resume_file = request.files.get("resume")

        if not full_name or not email or not phone or not cover_letter:
            flash("All fields are required.", "danger")
            return redirect(url_for("edit_my_application", application_id=application_id))

        updated_resume_name = application["resume"]

        if resume_file and resume_file.filename:
            saved_resume_name = save_resume_file(resume_file)
            if not saved_resume_name:
                flash("Only PDF, DOC, and DOCX files are allowed.", "danger")
                return redirect(url_for("edit_my_application", application_id=application_id))
            updated_resume_name = saved_resume_name

        db.execute(
            """
            UPDATE job_applications
            SET full_name = ?, email = ?, phone = ?, resume = ?, cover_letter = ?, status = 'Pending'
            WHERE id = ? AND user_id = ?
            """,
            (
                full_name,
                email,
                phone,
                updated_resume_name,
                cover_letter,
                application_id,
                session["user_id"],
            ),
        )
        db.commit()

        flash("Application updated successfully.", "success")
        return redirect(url_for("my_applications"))

    return render_template("edit_my_application.html", application=application)


# ----------------------------
# Job tracker - Superadmin application management
# ----------------------------
@app.route("/superadmin/applications")
@login_required
@role_required("superadmin")
def all_applications():
    db = get_db()
    apps = db.execute(
        """
        SELECT ja.*, j.title, j.company, u.full_name AS user_full_name
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        JOIN users u ON ja.user_id = u.id
        ORDER BY ja.id DESC
        """
    ).fetchall()

    return render_template("all_applications.html", apps=apps)


@app.route("/superadmin/application/<int:application_id>")
@login_required
@role_required("superadmin")
def single_application(application_id):
    db = get_db()

    application = db.execute(
        """
        SELECT ja.*, j.title, j.company, j.location, u.full_name AS user_full_name
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        JOIN users u ON ja.user_id = u.id
        WHERE ja.id = ?
        """,
        (application_id,),
    ).fetchone()

    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("all_applications"))

    return render_template("single_application.html", application=application)


@app.route("/superadmin/update-application/<int:app_id>/<status>")
@login_required
@role_required("superadmin")
def update_application(app_id, status):
    if status not in ["Accepted", "Rejected", "Pending"]:
        flash("Invalid application status.", "danger")
        return redirect(url_for("all_applications"))

    db = get_db()

    application = db.execute(
        "SELECT id, user_id FROM job_applications WHERE id = ?",
        (app_id,),
    ).fetchone()

    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("all_applications"))

    db.execute(
        "UPDATE job_applications SET status = ? WHERE id = ?",
        (status, app_id),
    )

    message = f"Your job application has been {status}."

    db.execute(
        """
        INSERT INTO notifications (user_id, message, is_read)
        VALUES (?, ?, 0)
        """,
        (application["user_id"], message),
    )

    db.commit()
    flash(f"Application marked as {status}.", "success")
    return redirect(url_for("all_applications"))


@app.route("/superadmin/delete-application/<int:application_id>", methods=["POST"])
@login_required
@role_required("superadmin")
def delete_application(application_id):
    db = get_db()

    application = db.execute(
        "SELECT id FROM job_applications WHERE id = ?",
        (application_id,),
    ).fetchone()

    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("all_applications"))

    db.execute("DELETE FROM job_applications WHERE id = ?", (application_id,))
    db.commit()

    flash("Application deleted successfully.", "success")
    return redirect(url_for("all_applications"))


# ----------------------------
# Resume download
# ----------------------------
@app.route("/download-resume/<path:filename>")
@login_required
def download_resume(filename):
    db = get_db()

    application = db.execute(
        """
        SELECT *
        FROM job_applications
        WHERE resume = ?
        """,
        (filename,),
    ).fetchone()

    if not application:
        abort(404)

    if session.get("role") == "superadmin":
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

    if session.get("role") == "user" and application["user_id"] == session.get("user_id"):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

    abort(403)


# ----------------------------
# Notifications
# ----------------------------
@app.route("/notifications")
@login_required
@role_required("user")
def notifications():
    db = get_db()
    notes = db.execute(
        """
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],),
    ).fetchall()

    return render_template("notifications.html", notes=notes)


@app.route("/notification/<int:notification_id>")
@login_required
@role_required("user")
def single_notification(notification_id):
    db = get_db()

    notification = db.execute(
        """
        SELECT *
        FROM notifications
        WHERE id = ? AND user_id = ?
        """,
        (notification_id, session["user_id"]),
    ).fetchone()

    if not notification:
        flash("Notification not found.", "danger")
        return redirect(url_for("notifications"))

    db.execute(
        """
        UPDATE notifications
        SET is_read = 1
        WHERE id = ? AND user_id = ?
        """,
        (notification_id, session["user_id"]),
    )
    db.commit()

    updated_notification = db.execute(
        """
        SELECT *
        FROM notifications
        WHERE id = ? AND user_id = ?
        """,
        (notification_id, session["user_id"]),
    ).fetchone()

    return render_template("single_notification.html", notification=updated_notification)


# ----------------------------
# User topic selection routes
# ----------------------------
@app.route("/user/available-topics")
@login_required
@role_required("user")
def available_topics():
    db = get_db()
    user_id = session.get("user_id")
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = """
        SELECT mpt.*,
               CASE WHEN ust.id IS NOT NULL THEN 1 ELSE 0 END AS already_selected
        FROM master_prep_topics mpt
        LEFT JOIN user_selected_topics ust
          ON ust.topic_id = mpt.id AND ust.user_id = ?
        WHERE mpt.is_active = 1
    """
    params = [user_id]

    if search:
        query += " AND (mpt.topic_name LIKE ? OR mpt.category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND mpt.category = ?"
        params.append(category)

    query += " ORDER BY mpt.topic_name ASC"

    topics = db.execute(query, params).fetchall()
    categories = db.execute(
        """
        SELECT DISTINCT category FROM master_prep_topics
        WHERE is_active = 1 AND category IS NOT NULL AND category != ''
        ORDER BY category ASC
        """
    ).fetchall()

    return render_template(
        "available_topics.html",
        topics=topics,
        search=search,
        category=category,
        categories=categories,
    )


@app.route("/user/select-topic/<int:topic_id>", methods=["POST"])
@login_required
@role_required("user")
def select_topic(topic_id):
    db = get_db()
    user_id = session.get("user_id")

    topic = db.execute(
        """
        SELECT id FROM master_prep_topics
        WHERE id = ? AND is_active = 1
        """,
        (topic_id,),
    ).fetchone()

    if not topic:
        flash("Topic not found.", "danger")
        return redirect(url_for("available_topics"))

    existing = db.execute(
        """
        SELECT id FROM user_selected_topics
        WHERE user_id = ? AND topic_id = ?
        """,
        (user_id, topic_id),
    ).fetchone()

    if existing:
        flash("You already selected this topic.", "warning")
        return redirect(url_for("available_topics"))

    db.execute(
        """
        INSERT INTO user_selected_topics (user_id, topic_id, progress_status, notes)
        VALUES (?, ?, 'Not Started', '')
        """,
        (user_id, topic_id),
    )
    db.commit()

    flash("Topic added to your preparation list.", "success")
    return redirect(url_for("my_topics"))


@app.route("/user/my-topics")
@login_required
@role_required("user")
def my_topics():
    db = get_db()
    user_id = session.get("user_id")

    topics = db.execute(
        """
        SELECT ust.*, mpt.topic_name, mpt.category, mpt.description
        FROM user_selected_topics ust
        INNER JOIN master_prep_topics mpt ON ust.topic_id = mpt.id
        WHERE ust.user_id = ? AND mpt.is_active = 1
        ORDER BY ust.id DESC
        """,
        (user_id,),
    ).fetchall()

    return render_template("my_topics.html", topics=topics)


@app.route("/user/update-my-topic/<int:selected_topic_id>", methods=["GET", "POST"])
@login_required
@role_required("user")
def update_my_topic(selected_topic_id):
    db = get_db()
    user_id = session.get("user_id")

    selected_topic = db.execute(
        """
        SELECT ust.*, mpt.topic_name, mpt.category, mpt.description
        FROM user_selected_topics ust
        INNER JOIN master_prep_topics mpt ON ust.topic_id = mpt.id
        WHERE ust.id = ? AND ust.user_id = ? AND mpt.is_active = 1
        """,
        (selected_topic_id, user_id),
    ).fetchone()

    if not selected_topic:
        flash("Selected topic not found.", "danger")
        return redirect(url_for("my_topics"))

    if request.method == "POST":
        progress_status = request.form.get("progress_status", "").strip()
        notes = request.form.get("notes", "").strip()

        if progress_status not in ["Not Started", "In Progress", "Revised", "Mastered"]:
            flash("Invalid progress status.", "danger")
            return redirect(url_for("update_my_topic", selected_topic_id=selected_topic_id))

        db.execute(
            """
            UPDATE user_selected_topics
            SET progress_status = ?, notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (progress_status, notes, selected_topic_id, user_id),
        )
        db.commit()

        flash("Your topic progress was updated successfully.", "success")
        return redirect(url_for("my_topics"))

    return render_template("update_my_topic.html", selected_topic=selected_topic)


@app.route("/user/remove-my-topic/<int:selected_topic_id>", methods=["POST"])
@login_required
@role_required("user")
def remove_my_topic(selected_topic_id):
    db = get_db()
    user_id = session.get("user_id")

    topic_row = db.execute(
        """
        SELECT topic_id FROM user_selected_topics
        WHERE id = ? AND user_id = ?
        """,
        (selected_topic_id, user_id),
    ).fetchone()

    if not topic_row:
        flash("Selected topic not found.", "danger")
        return redirect(url_for("my_topics"))

    db.execute(
        """
        DELETE FROM user_selected_topics
        WHERE id = ? AND user_id = ?
        """,
        (selected_topic_id, user_id),
    )
    db.execute(
        """
        DELETE FROM user_selected_questions
        WHERE user_id = ? AND question_id IN (
            SELECT id FROM master_prep_questions WHERE topic_id = ?
        )
        """,
        (user_id, topic_row["topic_id"]),
    )
    db.commit()

    flash("Topic removed from your preparation list.", "success")
    return redirect(url_for("my_topics"))


# ----------------------------
# User question selection routes
# ----------------------------
@app.route("/user/available-questions")
@login_required
@role_required("user")
def available_questions():
    db = get_db()
    user_id = session.get("user_id")

    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    topic_filter = request.args.get("topic_id", "").strip()
    my_topics_only = request.args.get("my_topics_only", "").strip()

    query = """
        SELECT mpq.*, mpt.topic_name, mpt.category,
               CASE WHEN usq.id IS NOT NULL THEN 1 ELSE 0 END AS already_selected
        FROM master_prep_questions mpq
        INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
        LEFT JOIN user_selected_questions usq
          ON usq.question_id = mpq.id AND usq.user_id = ?
        WHERE mpq.is_active = 1 AND mpt.is_active = 1
    """
    params = [user_id]

    if search:
        query += " AND (mpq.question LIKE ? OR mpq.answer LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if difficulty:
        query += " AND mpq.difficulty = ?"
        params.append(difficulty)

    if topic_filter:
        try:
            topic_filter_int = int(topic_filter)
            query += " AND mpq.topic_id = ?"
            params.append(topic_filter_int)
        except ValueError:
            pass

    if my_topics_only == "1":
        query += """
            AND mpq.topic_id IN (
                SELECT topic_id FROM user_selected_topics WHERE user_id = ?
            )
        """
        params.append(user_id)

    query += " ORDER BY mpq.id DESC"

    questions = db.execute(query, params).fetchall()

    topics = db.execute(
        """
        SELECT id, topic_name FROM master_prep_topics
        WHERE is_active = 1
        ORDER BY topic_name ASC
        """
    ).fetchall()

    return render_template(
        "available_questions.html",
        questions=questions,
        topics=topics,
        search=search,
        difficulty=difficulty,
        topic_filter=request.args.get("topic_id", ""),
        my_topics_only=my_topics_only,
    )


@app.route("/user/select-question/<int:question_id>", methods=["POST"])
@login_required
@role_required("user")
def select_question(question_id):
    db = get_db()
    user_id = session.get("user_id")

    question_row = db.execute(
        """
        SELECT id FROM master_prep_questions
        WHERE id = ? AND is_active = 1
        """,
        (question_id,),
    ).fetchone()

    if not question_row:
        flash("Question not found.", "danger")
        return redirect(url_for("available_questions"))

    existing = db.execute(
        """
        SELECT id FROM user_selected_questions
        WHERE user_id = ? AND question_id = ?
        """,
        (user_id, question_id),
    ).fetchone()

    if existing:
        flash("You already selected this question.", "warning")
        return redirect(url_for("available_questions"))

    db.execute(
        """
        INSERT INTO user_selected_questions (user_id, question_id, is_important, personal_notes)
        VALUES (?, ?, 0, '')
        """,
        (user_id, question_id),
    )
    db.commit()

    flash("Question added to your personal question bank.", "success")
    return redirect(url_for("my_questions"))


@app.route("/user/my-questions")
@login_required
@role_required("user")
def my_questions():
    db = get_db()
    user_id = session.get("user_id")

    search = request.args.get("search", "").strip()
    important = request.args.get("important", "").strip()

    query = """
        SELECT usq.*, mpq.question, mpq.answer, mpq.difficulty, mpt.topic_name
        FROM user_selected_questions usq
        INNER JOIN master_prep_questions mpq ON usq.question_id = mpq.id
        INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
        WHERE usq.user_id = ? AND mpq.is_active = 1 AND mpt.is_active = 1
    """
    params = [user_id]

    if search:
        query += " AND (mpq.question LIKE ? OR mpq.answer LIKE ? OR mpt.topic_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if important == "1":
        query += " AND usq.is_important = 1"

    query += " ORDER BY usq.id DESC"

    questions = db.execute(query, params).fetchall()
    return render_template("my_questions.html", questions=questions, search=search, important=important)


@app.route("/user/update-my-question/<int:selected_question_id>", methods=["GET", "POST"])
@login_required
@role_required("user")
def update_my_question(selected_question_id):
    db = get_db()
    user_id = session.get("user_id")

    selected_question = db.execute(
        """
        SELECT usq.*, mpq.question, mpq.answer, mpq.difficulty, mpt.topic_name
        FROM user_selected_questions usq
        INNER JOIN master_prep_questions mpq ON usq.question_id = mpq.id
        INNER JOIN master_prep_topics mpt ON mpq.topic_id = mpt.id
        WHERE usq.id = ? AND usq.user_id = ? AND mpq.is_active = 1 AND mpt.is_active = 1
        """,
        (selected_question_id, user_id),
    ).fetchone()

    if not selected_question:
        flash("Selected question not found.", "danger")
        return redirect(url_for("my_questions"))

    if request.method == "POST":
        is_important = 1 if request.form.get("is_important") == "on" else 0
        personal_notes = request.form.get("personal_notes", "").strip()

        db.execute(
            """
            UPDATE user_selected_questions
            SET is_important = ?, personal_notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (is_important, personal_notes, selected_question_id, user_id),
        )
        db.commit()

        flash("Your question preferences were updated successfully.", "success")
        return redirect(url_for("my_questions"))

    return render_template("update_my_question.html", selected_question=selected_question)


@app.route("/user/remove-my-question/<int:selected_question_id>", methods=["POST"])
@login_required
@role_required("user")
def remove_my_question(selected_question_id):
    db = get_db()
    user_id = session.get("user_id")

    db.execute(
        """
        DELETE FROM user_selected_questions
        WHERE id = ? AND user_id = ?
        """,
        (selected_question_id, user_id),
    )
    db.commit()

    flash("Question removed from your personal bank.", "success")
    return redirect(url_for("my_questions"))


# ----------------------------
# Superadmin user management
# ----------------------------
@app.route("/superadmin/all-users")
@login_required
@role_required("superadmin")
def all_users():
    db = get_db()

    active_users = db.execute(
        """
        SELECT id, full_name, email, role, created_at
        FROM users
        WHERE is_deleted = 0
        ORDER BY id DESC
        """
    ).fetchall()

    deleted_users = db.execute(
        """
        SELECT id, full_name, email, role, created_at, deleted_at
        FROM users
        WHERE is_deleted = 1
        ORDER BY id DESC
        """
    ).fetchall()

    return render_template(
        "all_users.html",
        active_users=active_users,
        deleted_users=deleted_users,
    )


@app.route("/superadmin/update-role/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def update_role(user_id):
    db = get_db()
    user = db.execute(
        """
        SELECT id, full_name, email, role, created_at, is_deleted
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("all_users"))

    if request.method == "POST":
        if user["id"] == session.get("user_id"):
            flash("You cannot change your own role from this page.", "warning")
            return redirect(url_for("update_role", user_id=user_id))

        new_role = request.form.get("role", "").strip()

        if new_role not in ["superadmin", "user"]:
            flash("Invalid role selected.", "danger")
            return redirect(url_for("update_role", user_id=user_id))

        db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        db.commit()

        flash("User role updated successfully.", "success")
        return redirect(url_for("all_users"))

    return render_template("update_role.html", user=user)


@app.route("/superadmin/soft-delete-users", methods=["POST"])
@login_required
@role_required("superadmin")
def soft_delete_users():
    selected_user_ids = request.form.getlist("selected_users")

    if not selected_user_ids:
        flash("Please select at least one user to soft delete.", "warning")
        return redirect(url_for("all_users"))

    db = get_db()

    safe_ids = []
    for uid in selected_user_ids:
        try:
            parsed_id = int(uid)
            if parsed_id != session.get("user_id"):
                safe_ids.append(parsed_id)
        except ValueError:
            continue

    if not safe_ids:
        flash("No valid users selected for soft delete.", "warning")
        return redirect(url_for("all_users"))

    placeholders = ",".join(["?"] * len(safe_ids))
    query = f"""
        UPDATE users
        SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
        WHERE id IN ({placeholders})
    """
    db.execute(query, safe_ids)
    db.commit()

    flash("Selected users soft deleted successfully.", "success")
    return redirect(url_for("all_users"))


@app.route("/superadmin/hard-delete-users", methods=["POST"])
@login_required
@role_required("superadmin")
def hard_delete_users():
    selected_user_ids = request.form.getlist("selected_users")

    if not selected_user_ids:
        flash("Please select at least one user to hard delete.", "warning")
        return redirect(url_for("all_users"))

    db = get_db()

    safe_ids = []
    for uid in selected_user_ids:
        try:
            parsed_id = int(uid)
            if parsed_id != session.get("user_id"):
                safe_ids.append(parsed_id)
        except ValueError:
            continue

    if not safe_ids:
        flash("No valid users selected for hard delete.", "warning")
        return redirect(url_for("all_users"))

    placeholders = ",".join(["?"] * len(safe_ids))
    query = f"DELETE FROM users WHERE id IN ({placeholders})"
    db.execute(query, safe_ids)
    db.commit()

    flash("Selected users hard deleted permanently.", "success")
    return redirect(url_for("all_users"))


@app.route("/superadmin/restore-users", methods=["POST"])
@login_required
@role_required("superadmin")
def restore_users():
    selected_user_ids = request.form.getlist("selected_deleted_users")

    if not selected_user_ids:
        flash("Please select at least one deleted user to restore.", "warning")
        return redirect(url_for("all_users"))

    db = get_db()

    safe_ids = []
    for uid in selected_user_ids:
        try:
            safe_ids.append(int(uid))
        except ValueError:
            continue

    if not safe_ids:
        flash("No valid deleted users selected.", "warning")
        return redirect(url_for("all_users"))

    placeholders = ",".join(["?"] * len(safe_ids))
    query = f"""
        UPDATE users
        SET is_deleted = 0, deleted_at = NULL
        WHERE id IN ({placeholders})
    """
    db.execute(query, safe_ids)
    db.commit()

    flash("Selected users restored successfully.", "success")
    return redirect(url_for("all_users"))


@app.route("/superadmin/delete-all-users-soft", methods=["POST"])
@login_required
@role_required("superadmin")
def delete_all_users_soft():
    db = get_db()

    db.execute(
        """
        UPDATE users
        SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
        WHERE role = 'user' AND is_deleted = 0
        """
    )
    db.commit()

    flash("All normal users soft deleted successfully.", "success")
    return redirect(url_for("all_users"))


@app.route("/superadmin/delete-all-users-hard", methods=["POST"])
@login_required
@role_required("superadmin")
def delete_all_users_hard():
    db = get_db()

    db.execute(
        """
        DELETE FROM users
        WHERE role = 'user'
        """
    )
    db.commit()

    flash("All normal users hard deleted permanently.", "success")
    return redirect(url_for("all_users"))


# ----------------------------
# Logout
# ----------------------------
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    init_db()
    add_missing_columns()
    app.run(debug=True)