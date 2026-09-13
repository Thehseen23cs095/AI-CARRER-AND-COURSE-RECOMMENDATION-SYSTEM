from flask import Flask, render_template, render_template_string, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime, os
import webbrowser
from reportlab.pdfgen import canvas
from io import BytesIO
from flask_migrate import Migrate
import sqlite3

# -------------------- MOCK QUESTIONS --------------------
MOCK_QUESTIONS = [
    {
        "question": "Tell me about yourself.",
        "type": "Behavioral",
        "difficulty": "Easy",
        "sample_answer": "Give a concise overview of your education, experience, skills, and career interests. Example: 'I am a BSc Computer Science graduate, passionate about AI and web development. I have done internships in web projects and enjoy problem-solving and learning new technologies.'"
    },
    {
        "question": "What are your strengths?",
        "type": "Behavioral",
        "difficulty": "Easy",
        "sample_answer": "Mention 2–3 strengths with examples, e.g., 'I am proactive, a fast learner, and good at teamwork. For example, I led a college project that improved our web application performance.'"
    },
    {
        "question": "What are your weaknesses?",
        "type": "Behavioral",
        "difficulty": "Medium",
        "sample_answer": "Be honest but show improvement. Example: 'I tend to overanalyze, but I have learned to prioritize tasks and meet deadlines efficiently.'"
    },
    {
        "question": "Why do you want to work for our company?",
        "type": "HR",
        "difficulty": "Medium",
        "sample_answer": "Show knowledge of company & alignment with career goals. Example: 'I admire your company’s innovation in AI solutions and want to contribute to projects that solve real-world problems while growing my skills.'"
    },
    {
        "question": "Explain the difference between list and tuple in Python.",
        "type": "Technical",
        "difficulty": "Medium",
        "sample_answer": "List is mutable and defined with [], while tuple is immutable and defined with (). Lists are good for dynamic data, tuples for fixed collections."
    },
    {
        "question": "What is polymorphism in OOP?",
        "type": "Technical",
        "difficulty": "Medium",
        "sample_answer": "Polymorphism allows objects to take many forms. Example: a function can use objects of different classes as long as they share a common interface or method."
    },
    {
        "question": "Describe a challenging project you worked on and how you overcame difficulties.",
        "type": "Behavioral",
        "difficulty": "Hard",
        "sample_answer": "Describe the situation, action, result. Example: 'I worked on an online shopping cart project with complex JS logic. I divided tasks, debugged systematically, and successfully implemented it on time.'"
    },
    {
        "question": "How do you handle tight deadlines?",
        "type": "Behavioral",
        "difficulty": "Medium",
        "sample_answer": "Explain time management. Example: 'I prioritize tasks, break them into smaller goals, and communicate with my team to ensure timely delivery.'"
    },
    {
        "question": "What is a REST API?",
        "type": "Technical",
        "difficulty": "Medium",
        "sample_answer": "REST API allows communication between client and server using HTTP methods (GET, POST, PUT, DELETE) with stateless requests."
    },
    {
        "question": "What is SQL JOIN and explain different types.",
        "type": "Technical",
        "difficulty": "Medium",
        "sample_answer": "JOIN combines rows from multiple tables. Types: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN. Each returns different sets of matched rows."
    },
    {
        "question": "Where do you see yourself in 5 years?",
        "type": "HR",
        "difficulty": "Medium",
        "sample_answer": "Show growth mindset. Example: 'I see myself as a skilled AI developer contributing to innovative projects and taking on leadership responsibilities.'"
    },
    {
        "question": "Explain how you debug a code issue.",
        "type": "Technical",
        "difficulty": "Medium",
        "sample_answer": "I reproduce the error, check logs, break down code step by step, use print/debug statements, and consult documentation or peers if needed."
    },
    {
        "question": "Have you worked in a team? How do you handle conflicts?",
        "type": "Behavioral",
        "difficulty": "Medium",
        "sample_answer": "Show teamwork & conflict resolution. Example: 'I communicate openly, listen to others, find common ground, and focus on project goals.'"
    },
    {
        "question": "Explain the concept of inheritance in OOP.",
        "type": "Technical",
        "difficulty": "Medium",
        "sample_answer": "Inheritance allows a class (child) to acquire properties and methods of another class (parent). It promotes code reuse and hierarchical relationships."
    },
    {
        "question": "Do you have any questions for us?",
        "type": "HR",
        "difficulty": "Easy",
        "sample_answer": "Ask insightful questions like team structure, technologies used, or opportunities for growth to show interest and preparation."
    }
]
def evaluate_answer(answer, question=""):
    """
    Simple evaluation logic:
    - If answer has < 5 words -> Needs Improvement
    - If answer has 5-15 words -> Good answer
    - If answer has > 15 words or matches keywords -> Excellent
    """
    words = answer.strip().split()
    if len(words) < 5:
        return "⚠️ Needs Improvement"
    elif len(words) <= 15:
        return "👍 Good answer"
    else:
        return "🌟 Excellent"

# ======================================================
# APP CONFIG
# ======================================================
app = Flask(__name__)
app.secret_key = "enterprise_ai_career_system_2026"

# Absolute path for SQLite DB to avoid OperationalError
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "career_system.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# ======================================================
# DATABASE MODELS
# ======================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10), default="user")

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    interest = db.Column(db.String(100))
    
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    parent_mobile = db.Column(db.String(20))
    level = db.Column(db.String(50))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    school_name = db.Column(db.String(100))
    stream_12th = db.Column(db.String(50))
    hobbies_or_skills = db.Column(db.String(200))
    career = db.Column(db.String(100))
    score = db.Column(db.Integer)
    readiness = db.Column(db.Integer)

    # ✅ Added fields for predict route
    education = db.Column(db.String(50))
    skill_level = db.Column(db.String(50))
    percentage_10th = db.Column(db.Float, default=0.0)
    percentage_12th = db.Column(db.Float, default=0.0)
    school_name_10th = db.Column(db.String(100))
    school_name_12th = db.Column(db.String(100))
    future_goal = db.Column(db.String(50))
    linkedin = db.Column(db.String(200))
    summary = db.Column(db.Text)
    certifications = db.Column(db.Text)


    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)



class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    event_name = db.Column(db.String(100))
    date = db.Column(db.DateTime)

# Create tables and default admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        db.session.add(User(
            username="admin",
            password=bcrypt.generate_password_hash("admin123").decode(),
            role="admin"
        ))
        db.session.commit()

# ======================================================
# CAREERS DATA
# ======================================================
# ======================================================
# CAREERS DATA (FIXED)
# ======================================================
CAREERS = {
    "AI Engineer": {
        "skills": ["python", "machine learning", "data science", "deep learning"],
        "interests": ["technology", "ai", "data"],
        "strengths": ["analytical thinking", "problem solving"]
    },
    "Data Scientist": {
        "skills": ["python", "statistics", "data analysis", "machine learning"],
        "interests": ["technology", "ai", "data"],
        "strengths": ["analytical thinking", "problem solving"]
    },
    "Web Developer": {
        "skills": ["html", "css", "javascript", "react"],
        "interests": ["technology", "web development"],
        "strengths": ["creativity", "problem solving"]
    },
    "Cybersecurity Analyst": {
        "skills": ["network security", "ethical hacking", "python"],
        "interests": ["technology", "security"],
        "strengths": ["analytical thinking", "attention to detail"]
    },
    "UI/UX Designer": {
        "skills": ["figma", "adobe xd", "user research"],
        "interests": ["design", "creativity"],
        "strengths": ["creativity", "empathy"]
    },
    "Digital Marketer": {
        "skills": ["seo", "smm", "content creation"],
        "interests": ["marketing", "creativity"],
        "strengths": ["communication", "creativity"]
    },
    "Cloud Engineer": {
        "skills": ["aws", "azure", "devops"],
        "interests": ["technology", "cloud computing"],
        "strengths": ["problem solving", "analytical thinking"]
    },
    "Network Engineer": {
        "skills": ["networking", "linux", "cisco"],
        "interests": ["technology", "networking"],
        "strengths": ["problem solving", "attention to detail"]
    },
    "Product Manager": {
        "skills": ["planning", "communication", "analytics"],
        "interests": ["management", "strategy"],
        "strengths": ["leadership", "organization"]
    },
    "Game Developer": {
        "skills": ["c++", "unity", "3d modeling"],
        "interests": ["gaming", "technology"],
        "strengths": ["creativity", "problem solving"]
    },
    "Blockchain Developer": {
        "skills": ["solidity", "ethereum", "smart contracts"],
        "interests": ["technology", "finance"],
        "strengths": ["analytical thinking", "problem solving"]
    },
    "Business Analyst": {
        "skills": ["excel", "sql", "business modeling"],
        "interests": ["business", "analytics"],
        "strengths": ["analytical thinking", "communication"]
    },
    "Robotics Engineer": {
        "skills": ["robotics", "mechanical", "python"],
        "interests": ["technology", "engineering"],
        "strengths": ["problem solving", "creativity"]
    }
}

# ===== At the top of app.py, before any @app.route =====
internships = [
    {"id":1,"title":"Web Developer Intern","company":"Infosys","location":"Bangalore","mode":"Hybrid","stipend":"₹10,000 / month","skills":"HTML, CSS, JavaScript"},
    {"id":2,"title":"Data Analyst Intern","company":"TCS","location":"Chennai","mode":"Onsite","stipend":"₹12,000 / month","skills":"Python, Excel, SQL"},
    {"id":3,"title":"AI/ML Intern","company":"IBM","location":"Remote","mode":"Remote","stipend":"₹15,000 / month","skills":"Python, Machine Learning, AI Basics"},
    {"id":4,"title":"Cybersecurity Intern","company":"Wipro","location":"Hyderabad","mode":"Onsite","stipend":"₹11,000 / month","skills":"Networking, Security Basics"},
    {"id":5,"title":"Cloud Engineer Intern","company":"Accenture","location":"Pune","mode":"Hybrid","stipend":"₹13,000 / month","skills":"AWS, Azure, DevOps"},
    {"id":6,"title":"Mobile App Developer Intern","company":"Capgemini","location":"Bangalore","mode":"Remote","stipend":"₹12,500 / month","skills":"Flutter, Kotlin, Swift"},
    {"id":7,"title":"UI/UX Design Intern","company":"Zoho","location":"Chennai","mode":"Onsite","stipend":"₹10,500 / month","skills":"Figma, Adobe XD, Design Thinking"},
    {"id":8,"title":"Digital Marketing Intern","company":"HCL","location":"Delhi","mode":"Remote","stipend":"₹9,000 / month","skills":"SEO, Google Ads, Social Media Marketing"},
    {"id":9,"title":"Blockchain Developer Intern","company":"Mindtree","location":"Bangalore","mode":"Hybrid","stipend":"₹15,000 / month","skills":"Solidity, Ethereum, Smart Contracts"},
    {"id":10,"title":"Robotics Intern","company":"Siemens","location":"Pune","mode":"Onsite","stipend":"₹14,000 / month","skills":"Arduino, Raspberry Pi, C++"},
    {"id":11,"title":"Business Analyst Intern","company":"Cognizant","location":"Chennai","mode":"Hybrid","stipend":"₹11,500 / month","skills":"Excel, SQL, Data Interpretation"},
    {"id":12,"title":"Content Writing Intern","company":"Infosys","location":"Remote","mode":"Remote","stipend":"₹8,000 / month","skills":"Writing, SEO, Editing"},
    {"id":13,"title":"Graphic Design Intern","company":"Adobe","location":"Bangalore","mode":"Onsite","stipend":"₹12,000 / month","skills":"Photoshop, Illustrator, Creativity"},
    {"id":14,"title":"Product Management Intern","company":"Amazon","location":"Hyderabad","mode":"Hybrid","stipend":"₹16,000 / month","skills":"Agile, Communication, Research"},
    {"id":15,"title":"HR Intern","company":"Tata Consultancy","location":"Mumbai","mode":"Onsite","stipend":"₹9,500 / month","skills":"Recruitment, Communication, Documentation"},
    {"id":16,"title":"SEO Analyst Intern","company":"HCL","location":"Delhi","mode":"Remote","stipend":"₹9,000 / month","skills":"SEO, Google Analytics, Keywords"},
    {"id":17,"title":"IoT Intern","company":"Tech Mahindra","location":"Bangalore","mode":"Hybrid","stipend":"₹14,000 / month","skills":"IoT, Sensors, C++"},
    {"id":18,"title":"Game Development Intern","company":"Ubisoft","location":"Pune","mode":"Onsite","stipend":"₹15,000 / month","skills":"Unity, C#, Game Design"},
    {"id":19,"title":"Animation Intern","company":"Pixar","location":"Chennai","mode":"Onsite","stipend":"₹13,500 / month","skills":"Maya, Blender, Animation"},
    {"id":20,"title":"Finance Intern","company":"Goldman Sachs","location":"Mumbai","mode":"Hybrid","stipend":"₹17,000 / month","skills":"Excel, Financial Modeling, Analysis"}
]

# ======================================================
# CAREER SCORE ENGINE (FIXED)
# ======================================================
def career_score_engine(interest):
    """
    Returns top 3 career recommendations with scores.
    Score = 80 if matches interest, else 60.
    """
    results = []
    for career_name, details in CAREERS.items():
        score = 80 if career_name == interest else 60
        results.append((career_name, score))  # ✅ use career_name as key
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:3]


# ======================================================
# AI LOGIC
# ======================================================


def readiness_index(skills_count):
    if skills_count>=4: return 85
    if skills_count>=3: return 70
    if skills_count>=2: return 55
    return 40

def learning_path(career):
    return [
        "Month 1–2: Fundamentals & Basics",
        "Month 3–5: Core Skills & Mini Projects",
        "Month 6–8: Advanced Concepts",
        "Month 9–12: Internship & Certification"
    ]

# ======================================================
# HOME PAGE (UNCHANGED)
# ======================================================
# ======================================================
# HOME PAGE (UPDATED – PROFESSIONAL)
# ======================================================
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Career and Course Recommendation System</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body{
    background: linear-gradient(120deg,#1e1e60,#3a0ca3);
    color:white;
    font-family:'Segoe UI',sans-serif;
}
.hero{
    min-height:85vh;
    display:flex;
    align-items:center;
}
.hero-text h1{
    font-size:48px;
    font-weight:800;
}
.hero-text p{
    font-size:18px;
    opacity:0.9;
}
.hero img{
    width:420px;
}
.card-feature{
    background:#ffffff12;
    border-radius:15px;
    padding:25px;
}
</style>
</head>

<body>

<nav class="navbar navbar-expand-lg navbar-dark bg-transparent px-5">
    <a class="navbar-brand fw-bold" href="/">Career AI</a>
    <div class="ms-auto">
        {% if session.get('user') %}
            <a href="/dashboard" class="btn btn-outline-light me-2">Dashboard</a>
            <a href="/logout" class="btn btn-danger">Logout</a>
        {% else %}
            <a href="/login" class="btn btn-outline-light me-2">Login</a>
            <a href="/register" class="btn btn-warning">Register</a>
        {% endif %}
    </div>
</nav>

<div class="container hero">
    <div class="row align-items-center w-100">
        <div class="col-md-6 hero-text">
            <h1>AI Career and Course Recommendation System</h1>
            <p class="mt-3">
                A smart AI-driven platform that analyzes your interests,
                skills, and academic details to recommend the best career
                paths and learning courses for your future.
            </p>
            <div class="mt-4">
                <a href="/select-education" class="btn btn-success btn-lg me-3">Predict Career</a>
                <a href="/register" class="btn btn-light btn-lg">Get Started</a>
            </div>
        </div>

        <div class="col-md-6 text-center">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" alt="AI Robot">
        </div>
    </div>
</div>

<div class="container mb-5">
    <div class="row text-center g-4">
        <div class="col-md-4">
            <div class="card-feature">
                <h4>🎯 Smart Career Prediction</h4>
                <p>AI suggests careers based on interest & skill analysis.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-feature">
                <h4>📘 Course Recommendation</h4>
                <p>Personalized learning paths for each student.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-feature">
                <h4>🤖 AI Assistance</h4>
                <p>Chatbot support & intelligent guidance system.</p>
            </div>
        </div>
    </div>
</div>

</body>
</html>
""")


# ======================================================
# LOGIN & REGISTER
# ======================================================
@app.route("/login", methods=["GET","POST"])
def login():
    msg=""
    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]
        user=User.query.filter_by(username=u).first()

        if user and bcrypt.check_password_hash(user.password,p):
            session["user"]=u
            session["role"]=user.role
            return redirect("/dashboard")
        else:
            msg="Invalid credentials"

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Robot Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body{
    height:100vh;
    background: linear-gradient(135deg,#141e30,#243b55);
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:'Segoe UI',sans-serif;
    overflow:hidden;
    color:white;
}

/* Floating animation */
@keyframes float{
    0%{transform:translateY(0);}
    50%{transform:translateY(-15px);}
    100%{transform:translateY(0);}
}

.robot-container{
    text-align:center;
    animation:float 4s ease-in-out infinite;
}

/* Robot */
.robot{
    width:120px;
    margin:auto;
}

.head{
    width:120px;
    height:90px;
    background:white;
    border-radius:20px;
    position:relative;
}

.eye{
    width:18px;
    height:18px;
    background:#243b55;
    border-radius:50%;
    position:absolute;
    top:30px;
    animation:blink 4s infinite;
}

.eye.left{ left:30px; }
.eye.right{ right:30px; }

@keyframes blink{
    0%,95%,100%{height:18px;}
    97%{height:3px;}
}

.body{
    width:100px;
    height:110px;
    background:white;
    margin:10px auto;
    border-radius:20px;
}

.arm{
    width:20px;
    height:80px;
    background:white;
    position:absolute;
    top:100px;
    border-radius:20px;
    animation:wave 2s infinite;
}

.arm.left{ left:-25px; }
.arm.right{ right:-25px; animation-delay:1s; }

@keyframes wave{
    0%{transform:rotate(0deg);}
    50%{transform:rotate(20deg);}
    100%{transform:rotate(0deg);}
}

/* Card */
.login-card{
    backdrop-filter:blur(15px);
    background:rgba(255,255,255,0.15);
    padding:30px;
    border-radius:20px;
    width:350px;
    margin-top:20px;
}

.form-control{
    background:transparent;
    border:none;
    border-bottom:2px solid white;
    border-radius:0;
    color:white;
}

.form-control:focus{
    background:transparent;
    box-shadow:none;
    border-bottom:2px solid #00f2fe;
    color:white;
}

.btn-custom{
    background:linear-gradient(45deg,#00f2fe,#4facfe);
    border:none;
    border-radius:30px;
    transition:0.3s;
}

.btn-custom:hover{
    transform:scale(1.05);
}
a{color:#00f2fe;}
</style>
</head>

<body>

<div class="robot-container">

    <div class="robot position-relative">
        <div class="head">
            <div class="eye left"></div>
            <div class="eye right"></div>
        </div>
        <div class="body"></div>
        <div class="arm left"></div>
        <div class="arm right"></div>
    </div>

    <div class="login-card">
        <h3 class="text-center mb-3">🤖 AI Secure Login</h3>
        <form method="post">
            <input name="username" placeholder="Username" class="form-control mb-3" required>
            <input type="password" name="password" placeholder="Password" class="form-control mb-3" required>
            <button class="btn btn-custom w-100">Login</button>
        </form>
        <p class="text-warning mt-2">{{msg}}</p>
        <p class="text-center mt-2">
            Don't have an account?
            <a href="/register">Register</a>
        </p>
    </div>

</div>

</body>
</html>
""", msg=msg)


@app.route("/register", methods=["GET","POST"])
def register():
    msg=""
    if request.method=="POST":
        if User.query.filter_by(username=request.form["username"]).first():
            msg="Username already exists"
        else:
            hashed=bcrypt.generate_password_hash(request.form["password"]).decode()
            db.session.add(User(username=request.form["username"], password=hashed))
            db.session.commit()
            return redirect("/login")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Robot Register</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body{
    height:100vh;
    background: linear-gradient(135deg,#42275a,#734b6d);
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:'Segoe UI',sans-serif;
    overflow:hidden;
    color:white;
}

@keyframes float{
    0%{transform:translateY(0);}
    50%{transform:translateY(-15px);}
    100%{transform:translateY(0);}
}

.robot-container{
    text-align:center;
    animation:float 4s ease-in-out infinite;
}

/* Same Robot Style */
.robot{width:120px;margin:auto;}
.head{width:120px;height:90px;background:white;border-radius:20px;position:relative;}
.eye{width:18px;height:18px;background:#734b6d;border-radius:50%;position:absolute;top:30px;animation:blink 4s infinite;}
.eye.left{left:30px;}
.eye.right{right:30px;}
@keyframes blink{0%,95%,100%{height:18px;}97%{height:3px;}}
.body{width:100px;height:110px;background:white;margin:10px auto;border-radius:20px;}
.arm{width:20px;height:80px;background:white;position:absolute;top:100px;border-radius:20px;animation:wave 2s infinite;}
.arm.left{left:-25px;}
.arm.right{right:-25px;animation-delay:1s;}
@keyframes wave{0%{transform:rotate(0deg);}50%{transform:rotate(20deg);}100%{transform:rotate(0deg);}}

.login-card{
    backdrop-filter:blur(15px);
    background:rgba(255,255,255,0.15);
    padding:30px;
    border-radius:20px;
    width:350px;
    margin-top:20px;
}

.form-control{
    background:transparent;
    border:none;
    border-bottom:2px solid white;
    border-radius:0;
    color:white;
}

.form-control:focus{
    background:transparent;
    box-shadow:none;
    border-bottom:2px solid #ff758c;
}

.btn-custom{
    background:linear-gradient(45deg,#ff512f,#dd2476);
    border:none;
    border-radius:30px;
    transition:0.3s;
}

.btn-custom:hover{
    transform:scale(1.05);
}
a{color:#ff758c;}
</style>
</head>

<body>

<div class="robot-container">

    <div class="robot position-relative">
        <div class="head">
            <div class="eye left"></div>
            <div class="eye right"></div>
        </div>
        <div class="body"></div>
        <div class="arm left"></div>
        <div class="arm right"></div>
    </div>

    <div class="login-card">
        <h3 class="text-center mb-3">🤖 Create AI Account</h3>
        <form method="post">
            <input name="username" placeholder="Username" class="form-control mb-3" required>
            <input type="password" name="password" placeholder="Password" class="form-control mb-3" required>
            <button class="btn btn-custom w-100">Register</button>
        </form>
        <p class="text-warning mt-2">{{msg}}</p>
        <p class="text-center mt-2">
            Already have an account?
            <a href="/login">Login</a>
        </p>
    </div>

</div>

</body>
</html>
""", msg=msg)

# ======================================================
# DASHBOARD
# ======================================================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Career Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

<style>
*{font-family:'Inter',sans-serif;}

body{
    background:#0f172a;
    color:white;
    overflow-x:hidden;
}

/* Animated gradient background */
body::before{
    content:"";
    position:fixed;
    width:900px;
    height:900px;
    background:radial-gradient(circle,#3b82f6,transparent 70%);
    top:-300px;
    right:-300px;
    opacity:0.15;
    animation:moveBg 18s infinite alternate ease-in-out;
    z-index:-1;
}

@keyframes moveBg{
    from{transform:translate(0,0);}
    to{transform:translate(-150px,150px);}
}

/* Header */
.header-card{
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(25px);
    border-radius:18px;
    padding:25px 30px;
    margin-bottom:40px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    animation:fadeDown 0.8s ease;
}

@keyframes fadeDown{
    from{opacity:0;transform:translateY(-25px);}
    to{opacity:1;transform:translateY(0);}
}

.role-badge{
    background:linear-gradient(45deg,#2563eb,#1d4ed8);
    padding:8px 18px;
    border-radius:12px;
    font-weight:600;
}

/* Module cards */
.module-card{
    position:relative;
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:20px;
    padding:30px;
    transition:all 0.4s cubic-bezier(.4,0,.2,1);
    backdrop-filter:blur(20px);
    overflow:hidden;
}

/* Animated border glow */
.module-card::before{
    content:"";
    position:absolute;
    inset:0;
    border-radius:20px;
    padding:1px;
    background:linear-gradient(120deg,#2563eb,#06b6d4,#2563eb);
    background-size:200% 200%;
    animation:gradientMove 4s linear infinite;
    opacity:0;
    transition:opacity 0.4s ease;
    z-index:0;
}

@keyframes gradientMove{
    0%{background-position:0% 50%;}
    100%{background-position:200% 50%;}
}

.module-card:hover::before{
    opacity:1;
}

/* Inner content stays above glow */
.module-card > *{
    position:relative;
    z-index:1;
}

/* Lift + shadow */
.module-card:hover{
    transform:translateY(-12px) scale(1.02);
    box-shadow:0 30px 70px rgba(37,99,235,0.35);
}

/* Title animation */
.module-card h5{
    transition:0.3s ease;
}

.module-card:hover h5{
    color:#3b82f6;
}

/* Button glow */
.module-card .btn{
    transition:all 0.3s ease;
}

.module-card:hover .btn{
    box-shadow:0 0 20px rgba(59,130,246,0.6);
    transform:translateY(-3px);
}


.module-card h5{
    font-weight:600;
    margin-bottom:8px;
}

.module-card p{
    color:#9ca3af;
    font-size:14px;
    margin-bottom:18px;
}

.module-card .btn{
    border-radius:12px;
    padding:8px 16px;
    font-weight:500;
}

/* Entrance animation */
@keyframes fadeUp{
    from{opacity:0;transform:translateY(40px);}
    to{opacity:1;transform:translateY(0);}
}

/* Stagger animation for 9 cards */
.module-card:nth-child(1){animation-delay:0.2s;}
.module-card:nth-child(2){animation-delay:0.3s;}
.module-card:nth-child(3){animation-delay:0.4s;}
.module-card:nth-child(4){animation-delay:0.5s;}
.module-card:nth-child(5){animation-delay:0.6s;}
.module-card:nth-child(6){animation-delay:0.7s;}
.module-card:nth-child(7){animation-delay:0.8s;}
.module-card:nth-child(8){animation-delay:0.9s;}
.module-card:nth-child(9){animation-delay:1s;}

</style>
</head>

<body>

<div class="container py-5">

    <!-- Header -->
    <div class="header-card">
        <div>
            <h4 class="mb-1">Welcome, {{session['user']}}</h4>
            <small class="text-secondary">AI Career & Course Recommendation System</small>
        </div>
        <div class="role-badge">
            Role: {{session['role']}}
        </div>
    </div>

    <!-- Modules Grid -->
    <div class="row g-4">

        <div class="col-md-4"><div class="module-card">
            <h5>🎯 Career Prediction</h5>
            <p>Analyze interests & skills</p>
            <a href="/select-education" class="btn btn-success">Career Prediction</a>
        </div></div>

        <div class="col-md-4"><div class="module-card">
            <h5>👤 My Profile</h5>
            <p>View career readiness</p>
            <a href="/profile" class="btn btn-success">View</a>
        </div></div>

        <div class="col-md-4"><div class="module-card">
            <h5>📘 Learning Resources</h5>
            <p>Courses & certifications</p>
            <a href="/learning" class="btn btn-warning">Explore</a>
        </div></div>

        <div class="col-md-4"><div class="module-card">
            <h5>🤖 AI Career Chatbot</h5>
            <p>Ask doubts anytime</p>
            <a href="/chatbot" class="btn btn-dark">Open Chatbot</a>
        </div></div>

        <div class="col-md-4"><div class="module-card">
            <h5>🧠 Skill Gap Analyzer</h5>
            <p>Analyze skills vs career requirements</p>
            <a href="/skill-gap" class="btn btn-primary">Analyze</a>
        </div></div>

        <div class="col-md-4"><div class="module-card">
            <h5>📝 Mock Interviews</h5>
            <p>Test skills with AI-generated assessments</p>
            <a href="/mock-interview-live" class="btn btn-success">Start Mock Interview</a>
        </div></div>

        <!-- Internship Opportunities Card -->
<div class="col d-flex">
    <div class="module-card">
        <h5>💼 Internship Opportunities</h5>
        <p>Explore real-world internships</p>
        <a href="/internship" class="btn btn-warning module-btn">View Internships</a>
    </div>
</div>


        <div class="col-md-4"><div class="module-card">
            <h5>🎤 Events & Webinars</h5>
            <p>Attend career workshops & webinars</p>
            <a href="/events" class="btn btn-dark">View Events</a>
        </div></div>

        <div class="col-md-4"><div class="module-card">
            <h5>📄 ATS Resume Builder</h5>
            <p>Create recruiter-friendly resume</p>
            <a href="/resume-builder" class="btn btn-primary">Build Resume</a>
        </div></div>

    </div>

</div>

</body>
</html>
""")

# ======================================================
# AI CAREER INTELLIGENCE – EDUCATION SELECTION
# ======================================================
# ==============================
# SELECT EDUCATION ROUTE
# ==============================
# ==============================
# HELPER FUNCTIONS
# ==============================
def get_student_detail(student, key, default=None):
    """Read a key from student's details dict safely."""
    if not student.details:
        student.details = {}
    return student.details.get(key, default)

def set_student_detail(student, key, value):
    """Update a key in student's details dict and commit."""
    if not student.details:
        student.details = {}
    student.details[key] = value
    db.session.commit()


# ==============================
# SELECT EDUCATION ROUTE
# ==============================

# ----------------------------
# Select Education & Skill Level
# ----------------------------
@app.route("/select-education", methods=["GET", "POST"])
def select_education():
    if "user" not in session:
        return redirect("/login")

    # 1️⃣ Get logged-in user
    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.clear()
        return redirect("/login")

    # 2️⃣ Get or create student profile
    student = Student.query.filter_by(user_id=user.id).first()
    if not student:
        student = Student(user_id=user.id, name=user.username)
        db.session.add(student)
        db.session.commit()

    # 3️⃣ Options for the form
    education_options = ["School", "Higher Secondary", "College", "Graduate", "Postgraduate"]
    skill_options = ["Beginner", "Intermediate", "Advanced", "Expert"]

    # 4️⃣ Handle form submission
    if request.method == "POST":
        education = request.form.get("education_level")
        skill_level = request.form.get("skill_level")

        if education and skill_level:
            student.education = education
            student.skill_level = skill_level
            db.session.commit()
            return redirect("/predict")

    # 5️⃣ Render form
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Career Intelligence | Education & Skills</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f8f0fc; color: #333; }
            .container { max-width: 600px; margin: 50px auto; background: #fff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);}
            h2 { color: #9b59b6; text-align: center; }
            label { display: block; margin-top: 15px; font-weight: bold; }
            select { width: 100%; padding: 10px; margin-top: 5px; border-radius: 8px; border: 1px solid #ccc; }
            button { background: #9b59b6; color: white; padding: 12px 20px; border: none; border-radius: 8px; margin-top: 20px; width: 100%; cursor: pointer; font-size: 16px; }
            button:hover { background: #8e44ad; }
            .info { margin-bottom: 20px; font-style: italic; color: #555; text-align: center; }
            .tooltip { font-size: 12px; color: #888; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome, {{ student.name }}</h2>
            <p class="info">Select your Education & Skill Level to get personalized career predictions.</p>

            <form method="POST">
                <label>Education Level:</label>
                <select name="education_level" required>
                    {% for edu in education_options %}
                        <option value="{{ edu }}" {% if student and student.education==edu %}selected{% endif %}>{{ edu }}</option>
                    {% endfor %}
                </select>
                <div class="tooltip">Choose your highest completed education level.</div>

                <label>Skill Level:</label>
                <select name="skill_level" required>
                    {% for skill in skill_options %}
                        <option value="{{ skill }}" {% if student and student.skill_level==skill %}selected{% endif %}>{{ skill }}</option>
                    {% endfor %}
                </select>
                <div class="tooltip">Select your proficiency level in your main skills.</div>

                <button type="submit">Save & Predict Careers</button>
            </form>
        </div>
    </body>
    </html>
    """, student=student, education_options=education_options, skill_options=skill_options)

# ----------------------------
# Career Prediction Logic
# ----------------------------
@app.route("/predict", methods=["GET","POST"])
def predict():
    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.clear()
        return redirect("/login")

    student = Student.query.filter_by(user_id=user.id).first()
    if not student:
        return redirect("/select-education")

    # ---------------- POST ----------------
    if request.method == "POST":

        student.name = request.form.get("name")
        student.father_name = request.form.get("father_name")
        student.mother_name = request.form.get("mother_name")
        student.parent_mobile = request.form.get("parent_mobile")
        student.future_goal = request.form.get("future_goal")
        student.interest = request.form.get("interest")

        # Education Based Saving
        if student.education == "School":
            student.school_name = request.form.get("school_name")
            student.percentage_10th = float(request.form.get("percentage") or 0)

        elif student.education == "Higher Secondary":
            student.school_name_10th = request.form.get("school_name_10th")
            student.percentage_10th = float(request.form.get("percentage_10th") or 0)
            student.school_name_12th = request.form.get("school_name_12th")
            student.percentage_12th = float(request.form.get("percentage_12th") or 0)
            student.stream_12th = request.form.get("stream_12th")

        elif student.education == "College":
            student.school_name = request.form.get("college_name")
            student.level = request.form.get("degree")
            student.percentage_12th = float(request.form.get("cgpa") or 0)

        elif student.education == "Graduate":
            student.level = request.form.get("degree_completed")
            student.school_name = request.form.get("university_name")
            student.percentage_12th = float(request.form.get("final_cgpa") or 0)

        elif student.education == "Postgraduate":
            student.level = request.form.get("pg_degree")
            student.percentage_12th = float(request.form.get("pg_cgpa") or 0)

        # Career Prediction
        if student.interest not in CAREERS:
            student.career = "Not Defined"
            student.score = 0
            student.readiness = 0
        else:
            results = career_score_engine(student.interest)
            student.career = results[0][0]
            student.score = results[0][1]
            student.readiness = readiness_index(
                len(CAREERS[student.interest]["skills"])
            )

        db.session.commit()
        return redirect("/profile")

    # ---------------- GET ----------------

    career_options = list(CAREERS.keys())

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Career Prediction</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">
<div class="container mt-5 mb-5">
<div class="card shadow p-4">

<h2 class="text-center mb-4">Career Prediction</h2>

<form method="post">

<div class="mb-3">
<input name="name" class="form-control" 
value="{{student.name}}" placeholder="Student Name" required>
</div>

<div class="row mb-3">
<div class="col">
<input name="father_name" class="form-control" 
value="{{student.father_name}}" placeholder="Father Name" required>
</div>
<div class="col">
<input name="mother_name" class="form-control" 
value="{{student.mother_name}}" placeholder="Mother Name" required>
</div>
</div>

<div class="mb-3">
<input name="parent_mobile" class="form-control" 
value="{{student.parent_mobile}}" placeholder="Parent Mobile">
</div>

<!-- ================= EDUCATION BASED FORM ================= -->

{% if student.education == "School" %}

<h5>School Details</h5>
<input name="school_name" class="form-control mb-3" placeholder="School Name" required>
<input type="number" name="percentage" class="form-control mb-3" placeholder="Current Percentage" required>

{% elif student.education == "Higher Secondary" %}

<h5>Higher Secondary Details</h5>
<input name="school_name_10th" class="form-control mb-3" placeholder="10th School Name" required>
<input type="number" name="percentage_10th" class="form-control mb-3" placeholder="10th Percentage" required>
<input name="school_name_12th" class="form-control mb-3" placeholder="12th School Name" required>
<input type="number" name="percentage_12th" class="form-control mb-3" placeholder="12th Percentage" required>
<input name="stream_12th" class="form-control mb-3" placeholder="12th Stream (Science/Commerce/etc)" required>

{% elif student.education == "College" %}

<h5>College Details</h5>
<input name="college_name" class="form-control mb-3" placeholder="College Name" required>
<input name="degree" class="form-control mb-3" placeholder="Degree (BSc/BTech/etc)" required>
<input type="number" step="0.01" name="cgpa" class="form-control mb-3" placeholder="Current CGPA" required>

{% elif student.education == "Graduate" %}

<h5>Graduate Details</h5>
<input name="degree_completed" class="form-control mb-3" placeholder="Degree Completed" required>
<input name="university_name" class="form-control mb-3" placeholder="University Name" required>
<input type="number" step="0.01" name="final_cgpa" class="form-control mb-3" placeholder="Final CGPA" required>

{% elif student.education == "Postgraduate" %}

<h5>Postgraduate Details</h5>
<input name="pg_degree" class="form-control mb-3" placeholder="PG Degree" required>
<input type="number" step="0.01" name="pg_cgpa" class="form-control mb-3" placeholder="PG CGPA" required>

{% endif %}

<hr>

<label>Career Interest:</label>
<select name="interest" class="form-select mb-3" required>
{% for c in career_options %}
<option value="{{c}}" {% if student.interest==c %}selected{% endif %}>{{c}}</option>
{% endfor %}
</select>

<label>Future Goal:</label>
<select name="future_goal" class="form-select mb-3" required>
<option value="">Select</option>
<option value="Higher Studies">Higher Studies</option>
<option value="Private Job">Private Job</option>
<option value="Government Job">Government Job</option>
<option value="Business">Business</option>
</select>

<button class="btn btn-primary w-100">
Predict Career
</button>

</form>
</div>
</div>
</body>
</html>
""", student=student, career_options=career_options)

# ==============================
# PROFILE ROUTE
# ==============================
# -------------------- PROFILE ROUTE --------------------
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    # Get user
    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        return redirect("/login")

    # Get or create student record
    s = Student.query.filter_by(user_id=user.id).first()
    if not s:
        s = Student(
            user_id=user.id,
            name=user.username,
            career="",
            score=0,
            readiness="Pending",
            hobbies_or_skills="",
            interest=""
        )
        db.session.add(s)
        db.session.commit()

    # Safe fields
    s.name = getattr(s, "name", "Unnamed")
    s.email = getattr(s, "email", "N/A")
    s.phone = getattr(s, "phone", "N/A")
    s.location = getattr(s, "location", "Unknown")
    s.role = getattr(s, "role", "Student")
    s.hobbies_or_skills = getattr(s, "hobbies_or_skills", "")
    s.interest = getattr(s, "interest", "")

    # Handle multiple careers
    careers = [c.strip() for c in s.career.split(",") if c.strip()]
    has_predicted = len(careers) > 0

    # Build a full career database from CAREERS dict
    full_career_db = {}
    for name, data in CAREERS.items():
        full_career_db[name] = ", ".join(data.get("skills", []))

    career_info = []
    for cname in careers:
        courses = full_career_db.get(cname, "")
        try:
            path = learning_path(cname)
        except:
            path = []
        career_info.append({
            "name": cname,
            "courses": [c.strip() for c in courses.split(",")] if courses else [],
            "path": path
        })

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ s.name }} - Profile</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
<style>
body { background: #f0f2f5; font-family:'Segoe UI',sans-serif; }
.header { background: linear-gradient(135deg,#667eea,#764ba2); color:white; padding:30px; text-align:center; border-radius:10px; }
.header img { border:4px solid rgba(255,255,255,0.5); }
.section-title { margin-top:25px; border-bottom:2px solid #dee2e6; padding-bottom:6px; }
.badge-skill { margin:3px; font-size:13px; }
.timeline-step { border-left:3px solid #0d6efd; padding-left:12px; margin-bottom:10px; font-size:14px; background:#fafafa; border-radius:5px;}
</style>
</head>
<body>

<div class="container mt-4">

<!-- Header -->
<div class="header">
    <img src="{{ s.profile_image if s.profile_image else 'https://via.placeholder.com/100' }}" class="rounded-circle mb-2" width="100">
    <h2>{{ s.name }}</h2>
    {% if has_predicted %}
        <p><span class="badge bg-warning">{{ ", ".join(careers) }}</span></p>
    {% else %}
        <p><span class="badge bg-secondary">Career Not Predicted</span></p>
    {% endif %}
    <p><i class="bi bi-envelope"></i> {{ s.email }} | <i class="bi bi-telephone"></i> {{ s.phone }}</p>
    <p><i class="bi bi-geo-alt"></i> {{ s.location }} | <i class="bi bi-person"></i> {{ s.role }}</p>
</div>

{% if has_predicted %}
    {% for ci in career_info %}
    <div class="mt-4">
        <h4 class="section-title"><i class="bi bi-briefcase-fill"></i> {{ ci.name }}</h4>

        <!-- Recommended Courses -->
        <h6>📘 Recommended Courses</h6>
        {% if ci.courses %}
            {% for course in ci.courses %}
                <span class="badge bg-info badge-skill">{{ course }}</span>
            {% endfor %}
        {% else %}
            <p>No course data available</p>
        {% endif %}

        <!-- Learning Path -->
        <h6 class="mt-3">🚀 Learning Path</h6>
        {% if ci.path %}
            {% for step in ci.path %}
                <div class="timeline-step">{{ loop.index }}. {{ step }}</div>
            {% endfor %}
        {% else %}
            <p>No path available</p>
        {% endif %}
    </div>
    {% endfor %}
{% endif %}

<!-- Skills -->
<div class="mt-4">
    <h5 class="section-title"><i class="bi bi-stars"></i> Skills / Hobbies</h5>
    {% if s.hobbies_or_skills %}
        {% for sk in s.hobbies_or_skills.split(",") if sk.strip() %}
            <span class="badge bg-secondary badge-skill">{{ sk.strip() }}</span>
        {% endfor %}
    {% else %}
        <p>No skills added yet.</p>
    {% endif %}
</div>

<!-- Interests -->
<div class="mt-3">
    <h5 class="section-title"><i class="bi bi-lightbulb-fill"></i> Interests</h5>
    {% if s.interest %}
        {% for it in s.interest.split(",") if it.strip() %}
            <span class="badge bg-primary badge-skill">{{ it.strip() }}</span>
        {% endfor %}
    {% else %}
        <p>No interests added yet.</p>
    {% endif %}
</div>

<a href="/dashboard" class="btn btn-secondary mt-4">⟵ Back to Dashboard</a>
</div>

</body>
</html>
""", s=s, careers=careers, career_info=career_info, has_predicted=has_predicted)

# -------------------- SUBMIT PREDICTION ROUTE --------------------
@app.route("/submit-prediction", methods=["POST"])
def submit_prediction():
    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        return redirect("/login")

    s = Student.query.filter_by(user_id=user.id).first()
    if not s:
        s = Student(user_id=user.id, name=user.username)
        db.session.add(s)

    # Get form data
    predicted_career = request.form.get("career", "").strip()
    predicted_score = int(request.form.get("score", 0))
    predicted_readiness = request.form.get("readiness", "Pending")
    predicted_readiness_percent = int(request.form.get("readiness_percent", 0))
    predicted_hobbies = request.form.get("hobbies", "")
    predicted_interest = request.form.get("interest", "")

    # Save to DB
    s.career = predicted_career
    s.score = predicted_score
    s.readiness = predicted_readiness
    s.hobbies_or_skills = predicted_hobbies
    s.interest = predicted_interest

    db.session.add(s)
    db.session.commit()

    # Save progress bar value in session (optional if not in DB)
    session["readiness_percent"] = predicted_readiness_percent

    return redirect("/profile")

# ======================================================
# LEARNING RESOURCES
# ======================================================
@app.route("/learning")
def learning():
    if "user" not in session:
        return redirect("/login")
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Learning Resources</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .card-icon { font-size: 24px; color: white; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
            .card:hover { transform: translateY(-10px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); transition: all 0.3s ease; }
            .card { transition: all 0.3s ease; cursor: pointer; }
            .bg-purple { background-color: #6f42c1; }
            .bg-orange { background-color: #fd7e14; }
            .bg-teal { background-color: #20c997; }
            .bg-red { background-color: #dc3545; }
            .bg-pink { background-color: #e83e8c; }
            .bg-lightblue { background-color: #0dcaf0; }
            .bg-lime { background-color: #198754; }
            .bg-gray { background-color: #6c757d; }
            .bg-yellow { background-color: #ffc107; }
            .bg-darkblue { background-color: #0d6efd; }
        </style>
    </head>
    <body>

        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/dashboard">Career Portal</a>
            </div>
        </nav>

        <div class="container mt-5">
            <h2 class="mb-4">Learning Resources</h2>
            <div class="row g-4">

                <!-- Python -->
                <div class="col-md-4">
                    <a href="https://www.python.org/about/gettingstarted/" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-success me-3"><i class="fab fa-python"></i></div>
                                <div>
                                    <h5 class="card-title">Python Tutorials</h5>
                                    <p class="card-text text-muted mb-0">Official Python beginner resources for AI, Web, and Data Science.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Machine Learning -->
                <div class="col-md-4">
                    <a href="https://developers.google.com/machine-learning/crash-course" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-danger me-3"><i class="fas fa-robot"></i></div>
                                <div>
                                    <h5 class="card-title">ML & Deep Learning</h5>
                                    <p class="card-text text-muted mb-0">Google’s official ML Crash Course for AI & neural networks.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Web Development -->
                <div class="col-md-4">
                    <a href="https://www.freecodecamp.org/" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-info me-3"><i class="fas fa-code"></i></div>
                                <div>
                                    <h5 class="card-title">Web Development</h5>
                                    <p class="card-text text-muted mb-0">Official FreeCodeCamp tutorials on HTML, CSS, JS, and frameworks.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Cyber Security -->
                <div class="col-md-4">
                    <a href="https://www.cisa.gov/cybersecurity-training" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-warning me-3"><i class="fas fa-shield-alt"></i></div>
                                <div>
                                    <h5 class="card-title">Cyber Security</h5>
                                    <p class="card-text text-muted mb-0">Official CISA cybersecurity training for labs and exercises.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Statistics & SQL -->
                <div class="col-md-4">
                    <a href="https://www.khanacademy.org/math/statistics-probability" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-primary me-3"><i class="fas fa-database"></i></div>
                                <div>
                                    <h5 class="card-title">Statistics & SQL</h5>
                                    <p class="card-text text-muted mb-0">Official Khan Academy lessons on stats, probability & SQL.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Communication Skills -->
                <div class="col-md-4">
                    <a href="https://www.coursera.org/learn/wharton-communication-skills" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-purple me-3"><i class="fas fa-comments"></i></div>
                                <div>
                                    <h5 class="card-title">Communication Skills</h5>
                                    <p class="card-text text-muted mb-0">Official Coursera course from Wharton on professional communication.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Leadership & Teamwork -->
                <div class="col-md-4">
                    <a href="https://www.coursera.org/learn/leading-teams" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-gray me-3"><i class="fas fa-users"></i></div>
                                <div>
                                    <h5 class="card-title">Leadership & Teamwork</h5>
                                    <p class="card-text text-muted mb-0">Official Coursera course: Learn to lead teams, resolve conflicts, and collaborate effectively.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Problem Solving -->
                <div class="col-md-4">
                    <a href="https://www.coursera.org/learn/creative-problem-solving" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-teal me-3"><i class="fas fa-lightbulb"></i></div>
                                <div>
                                    <h5 class="card-title">Problem Solving</h5>
                                    <p class="card-text text-muted mb-0">Official Coursera course: Learn structured problem-solving and critical thinking skills.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Time Management -->
                <div class="col-md-4">
                    <a href="https://www.coursera.org/learn/work-smarter-not-harder" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-orange me-3"><i class="fas fa-clock"></i></div>
                                <div>
                                    <h5 class="card-title">Time Management</h5>
                                    <p class="card-text text-muted mb-0">Official Coursera course on productivity and prioritization.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Emotional Intelligence -->
                <div class="col-md-4">
                    <a href="https://www.coursera.org/learn/emotional-intelligence-at-work" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-red me-3"><i class="fas fa-heart"></i></div>
                                <div>
                                    <h5 class="card-title">Emotional Intelligence</h5>
                                    <p class="card-text text-muted mb-0">Official Coursera course: Improve self-awareness, empathy, and interpersonal skills.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Cloud Computing -->
                <div class="col-md-4">
                    <a href="https://aws.amazon.com/training/learn-about/" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-pink me-3"><i class="fas fa-cloud"></i></div>
                                <div>
                                    <h5 class="card-title">Cloud Computing</h5>
                                    <p class="card-text text-muted mb-0">Official AWS training for cloud computing fundamentals.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Data Visualization -->
                <div class="col-md-4">
                    <a href="https://www.tableau.com/learn/training" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-lightblue me-3"><i class="fas fa-chart-line"></i></div>
                                <div>
                                    <h5 class="card-title">Data Visualization</h5>
                                    <p class="card-text text-muted mb-0">Official Tableau training for dashboards & visualization.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Entrepreneurship -->
                <div class="col-md-4">
                    <a href="https://ocw.mit.edu/courses/sloan-school-of-management/15-390-new-enterprises-spring-2013/" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-lime me-3"><i class="fas fa-briefcase"></i></div>
                                <div>
                                    <h5 class="card-title">Entrepreneurship</h5>
                                    <p class="card-text text-muted mb-0">Official MIT OCW course: Learn business planning, startup strategies, and idea validation.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Artificial Intelligence (IBM) -->
                <div class="col-md-4">
                    <a href="https://www.ibm.com/skills/ai" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-darkblue me-3"><i class="fas fa-robot"></i></div>
                                <div>
                                    <h5 class="card-title">AI Fundamentals</h5>
                                    <p class="card-text text-muted mb-0">Official IBM AI courses: Learn AI, machine learning, and neural networks.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Digital Marketing -->
                <div class="col-md-4">
                    <a href="https://learndigital.withgoogle.com/digitalgarage/course/digital-marketing" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-yellow me-3"><i class="fas fa-bullhorn"></i></div>
                                <div>
                                    <h5 class="card-title">Digital Marketing</h5>
                                    <p class="card-text text-muted mb-0">Official Google course: Learn SEO, analytics, and digital marketing strategies.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Blockchain Technology -->
                <div class="col-md-4">
                    <a href="https://ocw.mit.edu/courses/sloan-school-of-management/15-s12-blockchain-and-money-spring-2018/" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-darkblue me-3"><i class="fas fa-link"></i></div>
                                <div>
                                    <h5 class="card-title">Blockchain Technology</h5>
                                    <p class="card-text text-muted mb-0">Official MIT OCW course: Learn blockchain basics, cryptocurrencies, and applications.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Financial Literacy -->
                <div class="col-md-4">
                    <a href="https://www.khanacademy.org/college-careers-more/personal-finance" target="_blank" style="text-decoration:none;">
                        <div class="card p-3">
                            <div class="card-body d-flex align-items-center">
                                <div class="card-icon bg-gray me-3"><i class="fas fa-dollar-sign"></i></div>
                                <div>
                                    <h5 class="card-title">Financial Literacy</h5>
                                    <p class="card-text text-muted mb-0">Official Khan Academy lessons on money management, investing, and finance fundamentals.</p>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

            </div>

            <div class="mt-4">
                <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
            </div>
        </div>

    </body>
    </html>
    """)

# ======================================================
# PROFESSIONAL CHATBOT
# ======================================================
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    # =================== PROFESSIONAL KNOWLEDGE BASE ===================
    CAREERS = {
        "web developer": {
            "overview": "Responsible for developing and maintaining websites and web applications.",
            "skills": ["HTML", "CSS", "JavaScript", "React", "Git"],
            "tools": ["VS Code", "Chrome DevTools", "GitHub"],
            "courses": ["Frontend Development", "React Bootcamp"],
            "certifications": ["Meta Frontend Certificate", "Google UX Basics"],
            "salary": "₹3 – 8 LPA (India, Entry–Mid level)",
            "companies": ["TCS", "Infosys", "Zoho", "Accenture"],
            "interview": [
                "Explain HTML vs HTML5",
                "Difference between Flexbox and Grid",
                "What is REST API?"
            ],
            "roadmap": "HTML → CSS → JavaScript → React → Projects → Internship"
        },

        "data scientist": {
            "overview": "Analyzes data to extract insights and build predictive models.",
            "skills": ["Python", "Statistics", "Pandas", "Machine Learning"],
            "tools": ["Jupyter", "Power BI", "Excel"],
            "courses": ["Data Science with Python", "Machine Learning A-Z"],
            "certifications": ["IBM Data Science", "Google Data Analytics"],
            "salary": "₹6 – 15 LPA",
            "companies": ["Amazon", "Flipkart", "TCS", "Deloitte"],
            "interview": [
                "What is overfitting?",
                "Bias vs Variance",
                "Explain Pandas DataFrame"
            ],
            "roadmap": "Python → Statistics → Pandas → ML → Projects"
        },

        "ai engineer": {
            "overview": "Designs and deploys AI and deep learning systems.",
            "skills": ["Python", "Machine Learning", "TensorFlow", "NLP"],
            "tools": ["PyTorch", "Google Colab"],
            "courses": ["Deep Learning Specialization"],
            "certifications": ["AI Engineer – IBM"],
            "salary": "₹8 – 20 LPA",
            "companies": ["Google", "Microsoft", "Amazon"],
            "interview": [
                "What is neural network?",
                "CNN vs RNN",
                "Explain backpropagation"
            ],
            "roadmap": "Python → ML → Deep Learning → Deployment"
        },

        "software tester": {
            "overview": "Ensures software quality through manual and automated testing.",
            "skills": ["Manual Testing", "Selenium", "SQL", "JIRA"],
            "tools": ["Selenium IDE", "Postman"],
            "courses": ["Software Testing", "Automation with Selenium"],
            "certifications": ["ISTQB"],
            "salary": "₹3 – 6 LPA",
            "companies": ["Infosys", "Wipro", "Cognizant"],
            "interview": [
                "What is test case?",
                "Verification vs Validation",
                "What is regression testing?"
            ],
            "roadmap": "Manual Testing → Automation → Tools → Projects"
        }
    }

    # =================== SESSION INIT ===================
    if "chat_history" not in session:
        session["chat_history"] = []

    answer = (
        "👋 Hi! I’m your **Professional Career Assistant**.\n\n"
        "You can ask me about:\n"
        "• Careers\n• Skills\n• Salary\n• Companies\n• Certifications\n• Roadmaps\n• Interview preparation"
    )

    # =================== CHAT LOGIC ===================
    if request.method == "POST":
        user_q = request.form["question"]
        q = user_q.lower()
        found = False

        for career, info in CAREERS.items():
            if career in q:
                found = True

                if "skill" in q:
                    answer = f"🛠 Skills for {career.title()}:\n• " + "\n• ".join(info["skills"])

                elif "tool" in q:
                    answer = f"🧰 Tools used by {career.title()}:\n• " + "\n• ".join(info["tools"])

                elif "course" in q or "learn" in q:
                    answer = f"📚 Recommended Courses:\n• " + "\n• ".join(info["courses"])

                elif "certificate" in q:
                    answer = f"📜 Certifications:\n• " + "\n• ".join(info["certifications"])

                elif "salary" in q or "package" in q:
                    answer = f"💰 Salary Range for {career.title()}:\n{info['salary']}"

                elif "company" in q:
                    answer = f"🏢 Companies hiring {career.title()}s:\n• " + "\n• ".join(info["companies"])

                elif "interview" in q:
                    answer = f"🎯 Interview Questions:\n• " + "\n• ".join(info["interview"])

                elif "roadmap" in q or "path" in q:
                    answer = f"🗺 Learning Roadmap:\n{info['roadmap']}"

                else:
                    answer = (
                        f"💼 Career: {career.title()}\n"
                        f"📌 Overview: {info['overview']}\n"
                        f"🛠 Skills: {', '.join(info['skills'])}\n"
                        f"💰 Salary: {info['salary']}"
                    )
                break

        if not found:
            answer = (
                "❓ I didn’t understand fully.\n\n"
                "Try asking like:\n"
                "• Skills for web developer\n"
                "• Salary of data scientist\n"
                "• Roadmap for AI engineer\n"
                "• Interview questions for tester"
            )

        session["chat_history"].append({
            "question": user_q,
            "answer": answer
        })

    history = session.get("chat_history", [])

    # =================== UI ===================
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Professional Career Chatbot</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background:#f4f6fb; font-family:'Segoe UI'; }
.chat-container { max-width:900px; margin:50px auto; }
.chat-card { background:white; padding:20px; border-radius:18px; box-shadow:0 6px 20px rgba(0,0,0,0.1); }
.bubble { padding:12px 16px; border-radius:18px; margin-bottom:12px; white-space:pre-line; }
.user { background:#0d6efd; color:white; margin-left:auto; text-align:right; }
.bot { background:#e9ecef; }
</style>
</head>

<body>
<div class="chat-container">
<h2 class="text-center mb-4">🤖 Professional Career Chatbot</h2>

<div class="chat-card">
<div style="max-height:450px; overflow-y:auto;">
{% for item in history %}
  <div class="bubble user">{{ item.question }}</div>
  <div class="bubble bot">{{ item.answer }}</div>
{% endfor %}
{% if not history %}
  <div class="bubble bot">{{ answer }}</div>
{% endif %}
</div>

<form method="post" class="d-flex mt-3">
<input name="question" class="form-control me-2" placeholder="Ask about career, salary, skills, roadmap..." required>
<button class="btn btn-primary">Ask</button>
</form>
</div>

<a href="/dashboard" class="btn btn-secondary mt-3 w-100">⬅ Back to Dashboard</a>
</div>
</body>
</html>
""", history=history, answer=answer)

# ======================================================
# SKILL GAP
# ======================================================
@app.route("/skill-gap", methods=["GET", "POST"])
def skill_gap():
    if "user" not in session:
        return redirect("/login")

    # ================= CAREER FRAMEWORK =================
    CAREER_FRAMEWORK = {

        "Web Developer": {
            "Core Skills": ["HTML", "CSS", "JavaScript"],
            "Frontend Frameworks": ["Bootstrap", "React"],
            "Backend Basics": ["Python", "Flask", "SQL"],
            "Version Control": ["Git"]
        },

        "Software Engineer": {
            "Programming": ["Java", "Python", "C++"],
            "Core Concepts": ["OOP", "Data Structures", "Algorithms"],
            "Databases": ["SQL", "MongoDB"],
            "Tools": ["Git", "Docker"]
        },

        "Data Scientist": {
            "Core Skills": ["Python", "Statistics"],
            "Data Analysis": ["Pandas", "NumPy"],
            "Visualization": ["Matplotlib", "Power BI"],
            "Advanced": ["Machine Learning"]
        },

        "AI Engineer": {
            "Core Skills": ["Python", "Machine Learning"],
            "Deep Learning": ["TensorFlow", "PyTorch"],
            "AI Concepts": ["Neural Networks", "NLP"],
            "Deployment": ["Model Deployment", "APIs"]
        },

        "Cloud Engineer": {
            "Cloud Platforms": ["AWS", "Azure", "GCP"],
            "Core Skills": ["Linux", "Networking"],
            "Cloud Services": ["EC2", "S3"],
            "Security": ["IAM", "Cloud Security Basics"]
        },

        "DevOps Engineer": {
            "CI/CD": ["Jenkins", "GitHub Actions"],
            "Containers": ["Docker", "Kubernetes"],
            "Cloud": ["AWS", "Azure"],
            "Monitoring": ["Prometheus", "Grafana"]
        },

        "Cyber Security Analyst": {
            "Security Fundamentals": ["Network Security", "Cryptography"],
            "Tools": ["Wireshark", "Nmap"],
            "Security Ops": ["Incident Response", "Risk Assessment"],
            "Compliance": ["Cyber Laws"]
        },

        "Data Analyst": {
            "Core Skills": ["Excel", "SQL"],
            "Programming": ["Python"],
            "Visualization": ["Power BI", "Tableau"],
            "Analysis": ["Data Cleaning", "Reporting"]
        }
    }

    # ================= STATE VARIABLES =================
    selected_career = None
    user_skills = []
    matched = []
    missing = []
    match_percentage = 0
    required_skills = []

    # ================= POST LOGIC =================
    if request.method == "POST":
        selected_career = request.form.get("career")
        user_skills = request.form.getlist("skills")

        career_data = CAREER_FRAMEWORK.get(selected_career)
        if career_data:
            for skills in career_data.values():
                required_skills.extend(skills)

            matched = list(set(user_skills) & set(required_skills))
            missing = list(set(required_skills) - set(user_skills))

            if required_skills:
                match_percentage = int((len(matched) / len(required_skills)) * 100)

    # ================= ALL SKILLS (SAFE) =================
    all_skills = set()
    for career in CAREER_FRAMEWORK.values():
        for skill_list in career.values():
            all_skills.update(skill_list)
    all_skills = sorted(all_skills)

    # ================= HTML RESPONSE =================
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Skill Gap Analyzer</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{ background:#f4f6fb; font-family:'Segoe UI'; }}
.container {{ max-width:1100px; margin-top:40px; }}
.card {{ border-radius:16px; box-shadow:0 8px 25px rgba(0,0,0,0.08); }}
.skill {{ padding:8px 14px; margin:5px; border-radius:20px; display:inline-block; }}
.match {{ background:#d1e7dd; color:#0f5132; }}
.miss {{ background:#f8d7da; color:#842029; }}
.progress {{ height:24px; }}
.section-title {{ font-weight:600; color:#0d6efd; }}
</style>
</head>

<body>
<div class="container">

<h2 class="mb-2">🧠 Professional Skill Gap Analyzer</h2>
<p class="text-muted">Evaluate your readiness for industry roles and identify improvement areas.</p>

<div class="card p-4 mb-4">
<form method="POST">

<label class="section-title">🎯 Target Career Role</label>
<select name="career" class="form-select mb-3" required>
<option value="">Select Career</option>
{''.join([f"<option {'selected' if c==selected_career else ''}>{c}</option>" for c in CAREER_FRAMEWORK])}
</select>

<label class="section-title">💼 Your Current Skills</label>
<div class="mb-3">
{"".join([f'<input type="checkbox" name="skills" value="{s}" {"checked" if s in user_skills else ""}> {s}&nbsp;&nbsp;' for s in all_skills])}
</div>

<button class="btn btn-primary w-100">Run Skill Gap Analysis</button>
</form>
</div>

{f'''
<div class="card p-4 mb-4">
<h5 class="section-title">📊 Skill Match Score</h5>
<div class="progress mb-3">
<div class="progress-bar bg-success" style="width:{match_percentage}%">
{match_percentage}% Ready
</div>
</div>

<h6>✅ Strengths</h6>
{''.join([f'<span class="skill match">{s}</span>' for s in matched]) or "<p>No strengths identified yet</p>"}

<h6 class="mt-3">⚠ Skill Gaps</h6>
{''.join([f'<span class="skill miss">{s}</span>' for s in missing]) or "<p>No skill gaps 🎉</p>"}
</div>

<div class="card p-4 mb-4">
<h5 class="section-title">📅 30-60-90 Day Upskilling Plan</h5>
<ul>
<li><b>0–30 Days:</b> Learn basics of {', '.join(missing[:2]) or 'advanced topics'}</li>
<li><b>31–60 Days:</b> Build hands-on mini projects</li>
<li><b>61–90 Days:</b> Portfolio building & mock interviews</li>
</ul>
</div>
''' if selected_career else ""}

<a href="/dashboard" class="btn btn-secondary">⬅ Back to Dashboard</a>

</div>
</body>
</html>
"""

# -----------------------------
# Live AI Mock Interview (HARD LOCKED)
# -----------------------------
@app.route("/mock-interview-live")
def mock_interview_live():
    if "user" not in session:
        return redirect("/login")

    QUESTIONS = [
        {
            "q": "Tell me about yourself.",
            "sample": "I am a Computer Science student with a strong interest in web development and artificial intelligence. I enjoy building real-world applications and continuously improving my skills."
        },
        {
            "q": "Why did you choose Computer Science as your field?",
            "sample": "I chose Computer Science because I enjoy problem-solving and developing logical solutions using technology."
        },
        {
            "q": "Explain a project you have worked on recently.",
            "sample": "I worked on a Smart Online Shopping Cart system that allows users to browse products, manage carts, and place orders through a responsive interface."
        },
        {
            "q": "What programming languages are you comfortable with?",
            "sample": "I am comfortable with HTML, CSS, JavaScript, Python, and Java, mainly for web development and academic projects."
        },
        {
            "q": "How do you debug errors in your code?",
            "sample": "I carefully read the error message, isolate the issue, test possible fixes, and refer to documentation when needed."
        },
        {
            "q": "What are your strengths?",
            "sample": "My strengths include adaptability, teamwork, and a strong willingness to learn new technologies."
        },
        {
            "q": "What is your weakness?",
            "sample": "I sometimes overthink, but I am improving by planning tasks better and managing my time effectively."
        },
        {
            "q": "How do you handle pressure or tight deadlines?",
            "sample": "I prioritize tasks, stay organized, and focus on completing one task at a time without compromising quality."
        },
        {
            "q": "Why should we hire you?",
            "sample": "I have strong fundamentals, a positive learning mindset, and the dedication to contribute effectively to the team."
        }
    ]

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Live AI Mock Interview</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background:#f4f6fb; }
video { width:100%; height:280px; border-radius:10px; border:2px solid #222; margin-top:15px; }
#question { font-size:1.4rem; font-weight:600; margin-top:20px; }
#sample { background:#eef3ff; padding:15px; border-radius:8px; margin-top:10px; }
#status { font-weight:600; margin-top:10px; }
</style>
</head>

<body>
<div class="container mt-5" style="max-width:820px;">
<h2>🎤 Live AI Mock Interview</h2>

<button class="btn btn-success mb-3" onclick="startInterview()">▶ Start Interview</button>

<div id="question"></div>

<div id="sample">
<strong>Sample Answer (Hint):</strong>
<p id="sampleText"></p>
</div>

<div id="status" class="text-danger">Waiting to start interview.</div>
<div class="text-primary">Speaking Time: <span id="timer">0</span>s</div>

<video id="preview" autoplay muted></video>

<div class="mt-3">
<button id="nextBtn" class="btn btn-primary" disabled onclick="nextQuestion()">Next Question</button>
<a href="/dashboard" class="btn btn-secondary ms-2">Back</a>
</div>
</div>

<script>
const questions = {{ questions | tojson }};
let index = 0;

// Audio + speech variables
let audioCtx, analyser, mic;
let transcript = "";
let speakingSeconds = 0;
let speechFrames = 0;
let lastEnergy = 0;
let validAnswer = false;

const questionBox = document.getElementById("question");
const sampleBox = document.getElementById("sampleText");
const statusBox = document.getElementById("status");
const timerBox = document.getElementById("timer");
const nextBtn = document.getElementById("nextBtn");
const video = document.getElementById("preview");

function resetState() {
    transcript = "";
    speakingSeconds = 0;
    speechFrames = 0;
    validAnswer = false;
    lastEnergy = 0;
    timerBox.innerText = "0";
    nextBtn.disabled = true;
    statusBox.className = "text-danger";
    statusBox.innerText = "You are not speaking.";
}

function startInterview() {
    navigator.mediaDevices.getUserMedia({ audio:true, video:true })
    .then(stream => {
        video.srcObject = stream;

        audioCtx = new AudioContext();
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        mic = audioCtx.createMediaStreamSource(stream);
        mic.connect(analyser);

        startVoiceDetection();
        startSpeechRecognition();
        loadQuestion();
    })
    .catch(() => alert("Camera & microphone permission required."));
}

function startVoiceDetection() {
    const data = new Uint8Array(analyser.fftSize);

    setInterval(() => {
        analyser.getByteTimeDomainData(data);

        let energy = 0;
        for (let i = 0; i < data.length; i++) {
            energy += Math.abs(data[i] - 128);
        }

        const delta = Math.abs(energy - lastEnergy);
        lastEnergy = energy;

        // ✅ REAL HUMAN SPEECH CHECK (energy + variation)
        if (energy > 1600 && delta > 300) {
            speechFrames++;
            speakingSeconds++;
            timerBox.innerText = speakingSeconds;
            statusBox.className = "text-warning";
            statusBox.innerText = "🎙 Listening...";
        }

        // ✅ FINAL UNLOCK CONDITION
        if (!validAnswer && speechFrames >= 6 && transcript.length >= 20) {
            validAnswer = true;
            nextBtn.disabled = false;
            statusBox.className = "text-success";
            statusBox.innerText = "✅ Answer detected. You may continue.";
        }
    }, 1000);
}

function startSpeechRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = false;
    rec.lang = "en-US";

    rec.onresult = (e) => {
        const result = e.results[e.results.length - 1];
        if (result.isFinal && speechFrames > 0) {
            transcript += " " + result[0].transcript.trim();
        }
    };

    rec.start();
}

function loadQuestion() {
    resetState();

    if (index < questions.length) {
        questionBox.innerText = "Interviewer: " + questions[index].q;
        sampleBox.innerText = questions[index].sample;
        speechSynthesis.speak(new SpeechSynthesisUtterance(questions[index].q));
    } else {
        questionBox.innerText = "✅ Interview Completed";
        sampleBox.innerText = "";
        statusBox.className = "text-success";
        statusBox.innerText = "Interview finished successfully.";
        nextBtn.disabled = true;
    }
}

function nextQuestion() {
    if (!validAnswer) return;
    index++;
    loadQuestion();
}
</script>
</body>
</html>
""", questions=QUESTIONS)

# ======================================================
# INTERNSHIPS
# ======================================================
@app.route("/internship", strict_slashes=False)
def internship():
    if "user" not in session:
        return redirect("/login")

    # Fetch filter values
    location_filter = request.args.get("location", "").strip().lower()
    mode_filter = request.args.get("mode", "").strip().lower()
    skill_filter = request.args.get("skill", "").strip().lower()

    # Filter internships
    filtered = []
    for i in internships:
        if location_filter and location_filter not in i["location"].lower():
            continue
        if mode_filter and mode_filter not in i["mode"].lower():
            continue
        if skill_filter and skill_filter not in i["skills"].lower():
            continue
        filtered.append(i)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Internship Opportunities</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        body { background: #f0f4f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        h3 { color: #0d6efd; font-weight: 700; }
        .card { border-radius: 16px; transition: 0.3s; background: #fff; }
        .card:hover { transform: translateY(-6px); box-shadow: 0 12px 30px rgba(0,0,0,0.15); }
        .badge { font-size: 0.8rem; margin-right: 5px; }
        .skills { font-size: 0.9rem; color: #495057; }
        .btn-apply { border-radius: 12px; font-weight: 600; transition: 0.3s; }
        .btn-apply:hover { transform: scale(1.05); }
        .card-title { font-size: 1.1rem; font-weight: 600; color: #0d6efd; }
        .company { font-size: 0.95rem; color: #212529; font-weight: 500; }
        .intern-icon { font-size: 40px; color: #0d6efd; margin-bottom: 10px; }
        .filter-form { margin-bottom: 30px; }
    </style>
</head>
<body>
<div class="container mt-5">
    <h3 class="text-center mb-4">🎓 Internship Opportunities</h3>

    <!-- Filters -->
    <form class="row g-3 filter-form" method="get">
        <div class="col-md-4">
            <input type="text" name="location" class="form-control" placeholder="Filter by Location" value="{{ request.args.get('location','') }}">
        </div>
        <div class="col-md-4">
            <select name="mode" class="form-select">
                <option value="">Filter by Mode</option>
                <option value="Remote" {% if request.args.get('mode')=='Remote' %}selected{% endif %}>Remote</option>
                <option value="Onsite" {% if request.args.get('mode')=='Onsite' %}selected{% endif %}>Onsite</option>
                <option value="Hybrid" {% if request.args.get('mode')=='Hybrid' %}selected{% endif %}>Hybrid</option>
            </select>
        </div>
        <div class="col-md-4">
            <input type="text" name="skill" class="form-control" placeholder="Filter by Skill" value="{{ request.args.get('skill','') }}">
        </div>
        <div class="col-12 text-end">
            <button type="submit" class="btn btn-primary btn-sm">Apply Filters</button>
            <a href="/internship" class="btn btn-secondary btn-sm">Reset</a>
        </div>
    </form>

    <!-- Internship Cards -->
    <div class="row g-4">
        {% if filtered %}
            {% for i in filtered %}
            <div class="col-md-6 col-lg-4">
                <div class="card p-4 text-center">
                    <div class="intern-icon"><i class="fas fa-briefcase"></i></div>
                    <h5 class="card-title">{{ i.title }}</h5>
                    <p class="company"><i class="fas fa-building"></i> {{ i.company }}</p>
                    <div class="mb-2">
                        <span class="badge bg-primary"><i class="fas fa-map-marker-alt"></i> {{ i.location }}</span>
                        <span class="badge bg-info"><i class="fas fa-user-clock"></i> {{ i.mode }}</span>
                    </div>
                    <p class="mb-1"><i class="fas fa-money-bill-wave"></i> {{ i.stipend }}</p>
                    <p class="skills"><i class="fas fa-tools"></i> {{ i.skills }}</p>
                    <a href="/apply/{{i.id}}" class="btn btn-success btn-sm w-100 btn-apply mt-2">Apply Now</a>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center text-muted">
                <h5>No internships found matching your filters.</h5>
            </div>
        {% endif %}
    </div>

    <div class="text-center mt-4">
        <a href="/dashboard" class="btn btn-secondary"><i class="fas fa-arrow-left"></i> Back to Dashboard</a>
    </div>
</div>
</body>
</html>
""", filtered=filtered, request=request)

@app.route("/apply/<int:intern_id>", methods=["GET","POST"])
def apply(intern_id):
    if "user" not in session:
        return redirect("/login")

    # Find the internship by ID from the global list
    internship = next((i for i in internships if i["id"] == intern_id), None)
    if not internship:
        return "Internship not found", 404

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        resume = request.files.get("resume")
        resume_path = ""

        if resume:
            # Make sure uploads folder exists
            if not os.path.exists("uploads"):
                os.makedirs("uploads")

            resume_path = os.path.join("uploads", resume.filename)
            resume.save(resume_path)

        # Save application to database
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO applications (internship_title,user_name,user_email,user_phone,resume_path) VALUES (?,?,?,?,?)",
            (internship["title"], name, email, phone, resume_path)
        )
        conn.commit()
        conn.close()

        return redirect(f"/apply-success?title={internship['title']}")

    # Render the premium styled form
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Apply for {{internship.title}}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .apply-card {
                background: #fff;
                padding: 40px 30px;
                border-radius: 20px;
                box-shadow: 0 12px 30px rgba(0,0,0,0.15);
                width: 100%;
                max-width: 500px;
                text-align: center;
            }
            .apply-card h3 {
                color: #0d6efd;
                margin-bottom: 15px;
                font-weight: 700;
            }
            .apply-card p {
                color: #495057;
                font-size: 0.95rem;
                margin-bottom: 25px;
            }
            .form-control {
                border-radius: 12px;
                padding-left: 35px;
            }
            .form-group {
                position: relative;
                margin-bottom: 15px;
            }
            .form-group i {
                position: absolute;
                top: 50%;
                left: 12px;
                transform: translateY(-50%);
                color: #0d6efd;
            }
            .btn-submit {
                border-radius: 12px;
                font-weight: 600;
                transition: 0.3s;
            }
            .btn-submit:hover {
                transform: scale(1.05);
            }
            input[type="file"] {
                padding: 3px 10px;
            }
        </style>
    </head>
    <body>
        <div class="apply-card">
            <h3><i class="fas fa-briefcase"></i> Apply for {{internship.title}}</h3>
            <p><i class="fas fa-building"></i> {{internship.company}} | 
               <i class="fas fa-map-marker-alt"></i> {{internship.location}} | 
               <i class="fas fa-clock"></i> {{internship.mode}}</p>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <i class="fas fa-user"></i>
                    <input type="text" name="name" placeholder="Your Name" class="form-control" required>
                </div>
                <div class="form-group">
                    <i class="fas fa-envelope"></i>
                    <input type="email" name="email" placeholder="Your Email" class="form-control" required>
                </div>
                <div class="form-group">
                    <i class="fas fa-phone"></i>
                    <input type="text" name="phone" placeholder="Phone Number" class="form-control" required>
                </div>
                <div class="form-group">
                    <i class="fas fa-file-upload"></i>
                    <input type="file" name="resume" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-success w-100 btn-submit mt-2">
                    <i class="fas fa-paper-plane"></i> Submit Application
                </button>
            </form>
        </div>
    </body>
    </html>
    """, internship=internship)

@app.route("/apply-success")
def apply_success():
    title = request.args.get("title", "the internship")
    return f"""
    <div style='text-align:center;margin-top:100px;font-family:Segoe UI;background:#f0f4f9; padding:50px;'>
        <div style='display:inline-block;background:white;padding:40px 50px;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,0.1);'>
            <h2 style='color:#28a745;'><i class="fas fa-check-circle"></i> Application Submitted</h2>
            <p>Your profile has been shared with the HR for <strong>{title}</strong>.</p>
            <p>You will be contacted via email if shortlisted.</p>
            <a href="/internship" class="btn btn-primary mt-3" style="border-radius:12px;"><i class="fas fa-arrow-left"></i> Back to Internships</a>
        </div>
    </div>
    """
# ======================================================
# EVENTS & WEBINARS (PROFESSIONAL VERSION)
# ======================================================
@app.route("/events")
def events():
    if "user" not in session:
        return redirect("/login")

    events = [
        {
            "title": "NVIDIA GTC 2026 – AI Conference",
            "date": "16–19 March 2026",
            "mode": "Hybrid",
            "organizer": "NVIDIA",
            "location": "San Jose & Online",
            "description": "World’s leading AI conference covering Generative AI, Robotics, and High-Performance Computing.",
            "link": "https://www.nvidia.com/gtc/"
        },
        {
            "title": "Google AI Virtual Summit",
            "date": "12 February 2026",
            "mode": "Online",
            "organizer": "Google",
            "location": "Online",
            "description": "Explore AI tools, career paths, and hands-on learning directly from Google AI experts.",
            "link": "https://events.withgoogle.com/"
        },
        {
            "title": "Microsoft Build 2026",
            "date": "20–22 May 2026",
            "mode": "Online",
            "organizer": "Microsoft",
            "location": "Online",
            "description": "Developer conference focusing on AI, cloud, full-stack development, and career growth.",
            "link": "https://build.microsoft.com/"
        },
        {
            "title": "AWS Innovate – AI & ML Edition",
            "date": "28 February 2026",
            "mode": "Online",
            "organizer": "Amazon Web Services",
            "location": "Online",
            "description": "Free virtual conference covering AI/ML, cloud architecture, and industry best practices.",
            "link": "https://aws.amazon.com/events/"
        },
        {
            "title": "IBM Data & AI Summit",
            "date": "5 March 2026",
            "mode": "Online",
            "organizer": "IBM SkillsBuild",
            "location": "Online",
            "description": "Enterprise-level sessions on Data Science, AI careers, and industry certifications.",
            "link": "https://skillsbuild.org/"
        },
        {
            "title": "Meta Developer Conference (AI Track)",
            "date": "April 2026",
            "mode": "Online",
            "organizer": "Meta",
            "location": "Online",
            "description": "AI development sessions focusing on open-source, LLMs, and next-gen applications.",
            "link": "https://developers.facebook.com/events/"
        }
    ]

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Events & Webinars | Career AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body{
    background:#f4f6fb;
    font-family:'Segoe UI',sans-serif;
}

.page-title{
    font-weight:700;
}

.event-card{
    background:white;
    border-radius:16px;
    padding:24px;
    height:100%;
    transition:0.3s;
}

.event-card:hover{
    transform:translateY(-6px);
    box-shadow:0 16px 35px rgba(0,0,0,0.12);
}

.badge-mode{
    background:#0d6efd;
}

.register-btn{
    background:linear-gradient(135deg,#2563eb,#1e40af);
    border:none;
    border-radius:12px;
    padding:10px;
    font-weight:500;
}

.register-btn:hover{
    opacity:0.9;
}
</style>
</head>

<body>

<div class="container py-5">

    <div class="text-center mb-5">
        <h2 class="page-title">🎤 Tech Events & Webinars</h2>
        <p class="text-muted">
            Explore real-world AI, Cloud, and Developer events from top global companies
        </p>
    </div>

    <div class="row g-4">
        {% for e in events %}
        <div class="col-md-6 col-lg-4">
            <div class="event-card">
                <h5 class="fw-semibold">{{ e.title }}</h5>
                <span class="badge badge-mode mt-1">{{ e.mode }}</span>

                <p class="mt-3 mb-1"><strong>📅 {{ e.date }}</strong></p>
                <p class="mb-1">🏢 {{ e.organizer }}</p>
                <p class="mb-1">📍 {{ e.location }}</p>

                <p class="text-muted mt-2">{{ e.description }}</p>

                <a href="{{ e.link }}" target="_blank"
                   class="btn btn-primary register-btn w-100 mt-3">
                   Register on Official Website →
                </a>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="text-center mt-5">
        <a href="/dashboard" class="btn btn-outline-secondary px-4">
            ⬅ Back to Dashboard
        </a>
    </div>

</div>

</body>
</html>
""", events=events)

#----------------------------
#RESUME BUILDING
#----------------------------
# ======================================================
# RESUME BUILDER
# ======================================================
from flask import Flask, render_template_string, request, redirect, session, flash, send_file
from io import BytesIO
from reportlab.pdfgen import canvas

@app.route("/resume-builder", methods=["GET", "POST"])
def resume_builder():
    if "user" not in session:
        return redirect("/login")
    
    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        return redirect("/login")

    s = Student.query.filter_by(user_id=user.id).first()
    if not s:
        s = Student(user_id=user.id, name=user.username)
        db.session.add(s)
        db.session.commit()

    if request.method == "POST":
        # Update student resume fields
        s.name = request.form.get("name", s.name)
        s.email = request.form.get("email", getattr(s, "email", ""))
        s.phone = request.form.get("phone", getattr(s, "phone", ""))
        s.education = request.form.get("education", getattr(s, "education", ""))
        s.skills_or_hobbies = request.form.get("skills", getattr(s, "skills_or_hobbies", ""))
        s.experience = request.form.get("experience", getattr(s, "experience", ""))
        s.summary = request.form.get("summary", getattr(s, "summary", ""))
        s.linkedin = request.form.get("linkedin", getattr(s, "linkedin", ""))
        s.certifications = request.form.get("certifications", getattr(s, "certifications", ""))

        db.session.add(s)
        db.session.commit()
        flash("✅ Resume details saved!", "success")
        return redirect("/resume-builder")

    # Resume form
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Resume Builder</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background: #f8f9fa; }
.container { max-width: 800px; background: #fff; padding: 30px; margin-top: 30px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1);}
h2 { color: #343a40; }
.btn-download { margin-top: 15px; }
</style>
</head>
<body>
<div class="container">
<h2>📝 Professional Resume Builder</h2>
<form method="POST">
<div class="mb-3">
<label>Name</label>
<input type="text" name="name" class="form-control" value="{{ s.name or '' }}" required>
</div>

<div class="mb-3">
<label>Email</label>
<input type="email" name="email" class="form-control" value="{{ s.email or '' }}">
</div>

<div class="mb-3">
<label>Phone</label>
<input type="text" name="phone" class="form-control" value="{{ s.phone or '' }}">
</div>

<div class="mb-3">
<label>LinkedIn URL</label>
<input type="text" name="linkedin" class="form-control" value="{{ s.linkedin or '' }}">
</div>

<div class="mb-3">
<label>Professional Summary</label>
<textarea name="summary" class="form-control">{{ s.summary or '' }}</textarea>
</div>

<div class="mb-3">
<label>Education</label>
<textarea name="education" class="form-control">{{ s.education or '' }}</textarea>
</div>

<div class="mb-3">
<label>Skills / Hobbies (comma separated)</label>
<textarea name="skills" class="form-control">{{ s.skills_or_hobbies or '' }}</textarea>
</div>

<div class="mb-3">
<label>Experience / Projects</label>
<textarea name="experience" class="form-control">{{ s.experience or '' }}</textarea>
</div>

<div class="mb-3">
<label>Certifications / Achievements</label>
<textarea name="certifications" class="form-control">{{ s.certifications or '' }}</textarea>
</div>

<button class="btn btn-primary w-100">Save Resume</button>
</form>

<a href="/download-resume" class="btn btn-success w-100 btn-download">📄 Download PDF Resume</a>
<a href="/dashboard" class="btn btn-secondary w-100 mt-2">⬅ Back to Dashboard</a>
</div>
</body>
</html>
""", s=s)

# Resume PDF download route
@app.route("/download-resume")
def download_resume():
    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        return redirect("/login")

    s = Student.query.filter_by(user_id=user.id).first()
    if not s:
        flash("No resume data found! Please fill your resume first.", "warning")
        return redirect("/resume-builder")

    # Create PDF in memory
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(595, 842))  # A4 size
    width, height = 595, 842
    margin = 50
    y = height - margin

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(margin, y, s.name or "Your Name")

    pdf.setFont("Helvetica", 12)
    y -= 30
    contact_info = f"{s.email or ''} | {s.phone or ''} | LinkedIn: {s.linkedin or ''}"
    pdf.drawString(margin, y, contact_info)
    y -= 15
    pdf.line(margin, y, width - margin, y)
    y -= 20

    # Sections
    sections = [
        ("Professional Summary", getattr(s, "summary", "")),
        ("Education", getattr(s, "education", "")),
        ("Skills / Hobbies", getattr(s, "skills_or_hobbies", "")),
        ("Experience / Projects", getattr(s, "experience", "")),
        ("Certifications / Achievements", getattr(s, "certifications", ""))
    ]

    for title, content in sections:
        if content:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin, y, title)
            y -= 18
            pdf.setFont("Helvetica", 12)
            lines = content.split("\n") if "\n" in content else content.split(",")
            for line in lines:
                pdf.drawString(margin + 10, y, f"• {line.strip()}")
                y -= 15
            y -= 10

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{s.name or 'Resume'}.pdf",
        mimetype="application/pdf"
    )

# ======================================================
# ADMIN
# ======================================================
@app.route("/admin")
def admin():
    if "user" not in session or session.get("role")!="admin":
        return redirect("/login")
    students=Student.query.all()
    return render_template_string("""
    <html><head><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="bg-light"><div class="container mt-5">
      <h2>Admin - Students Overview</h2>
      <table class="table table-striped">
        <tr><th>ID</th><th>Name</th><th>Career</th><th>Score</th><th>Readiness</th></tr>
        {% for s in students %}
        <tr><td>{{s.id}}</td><td>{{s.name}}</td><td>{{s.career}}</td><td>{{s.score}}</td><td>{{s.readiness}}</td></tr>
        {% endfor %}
      </table>
      <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
    </div></body></html>
    """, students=students)

# ======================================================
# LOGOUT
# ======================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
# ======================================================
# RUN APP
# ======================================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)