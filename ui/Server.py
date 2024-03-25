
# Library used in code
from flask import Flask, render_template, request, redirect, url_for, Response, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,text
import base64
import cv2
import json
import os

app = Flask(__name__)


# For Database
# configuration of the database 
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'survey_secret'

db = SQLAlchemy(app)

class Survey1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225))
    There_Department = db.Column(db.String(50))
    There_TDepartment = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    suggestion = db.Column(db.Text)
    srating = db.Column(db.Integer)
    
class Slider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

class Aboutimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

class Coursesimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

class Administration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

def load_responses():
    if os.path.exists('responses.json'):
        with open('responses.json', 'r') as file:
            return json.load(file)
    return {}

def save_responses(responses):
    with open('responses.json', 'w') as file:
        json.dump(responses, file, indent=4)

def load_unknown_questions():
    if os.path.exists('unknown_questions.json'):
        with open('unknown_questions.json', 'r') as file:
            return json.load(file)
    return []

def save_unknown_questions(unknown_questions):
    with open('unknown_questions.json', 'w') as file:
        json.dump(unknown_questions, file, indent=4)

def store_unknown_question(question):
    unknown_questions = load_unknown_questions()
    unknown_questions.append(question)
    save_unknown_questions(unknown_questions)


# For Camera Settings
camera = cv2.VideoCapture(0)
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route Index Login page
@app.route('/')
def index():
    return redirect(url_for('SEBASTYINDEX'))

# Route Login Settings 
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'Sebasty' and password == '12345':
        return redirect(url_for('admin'))
    elif username == 'Sebastyui' and password == '1233':
       return redirect(url_for('SEBASTYINDEX'))
    else:
        return render_template('Login.html', message='Invalid username or password. Please try again.')

# Admin interface
@app.route('/admin')
def admin():
    query = text("""
        SELECT 
            There_TDepartment AS Target_Department,
            COUNT(*) AS total_voter,
            COUNT(*) * 5 AS expected_total_stars,
            SUM(rating) AS total_earned_stars
        FROM 
            Survey1
        GROUP BY 
            There_TDepartment;
        """)

    conn = db.engine.connect()
    results = conn.execute(query)
    average_ratings = results.fetchall()

    query_overall_srating = text("""
        SELECT 
            AVG(srating) AS overall_average_rating,
            COUNT(*) AS    Stotal_voter,
            COUNT(*) * 5 AS Sexpected_total_stars,
            SUM(srating) AS Stotal_earned_stars
        FROM Survey1
        """)

    # Execute the query for overall school rating
    results_overall_srating = conn.execute(query_overall_srating)
    overall_srating = results_overall_srating.fetchall()

    surveys = Survey1.query.all()
    conn.close()

    unknown_questions = load_unknown_questions()
    return render_template('Admin.html', surveys=surveys, average_ratings=average_ratings, overall_srating=overall_srating, unknown_questions=unknown_questions)
  
  
# Admin Form-Post
# Update form Slider
@app.route('/upload_slider', methods=['GET','POST'])
def upload_slider():
    if request.method == 'POST':
        slider_name = request.form['Slide_name']
        slider_image = request.files['image'].read()
        existing_slider = Slider.query.filter_by(name=slider_name).first()
        if existing_slider:
            existing_slider.image = slider_image
            db.session.commit()
            flash('Slider image updated successfully', 'success')
        else:
            new_slider = Slider(name=slider_name, image=slider_image)
            db.session.add(new_slider)
            db.session.commit()
            flash('New slider uploaded successfully', 'success')
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

# Update form About
@app.route('/upload_About', methods=['GET','POST'])
def upload_About():
    if request.method == 'POST':
        About_name = request.form['About_name']
        About_image = request.files['About_image'].read()
        existing_About = Aboutimage.query.filter_by(name=About_name).first()
        if existing_About:
            existing_About.image = About_image
            db.session.commit()
            flash('About image updated successfully', 'success')
        else:
            new_slider = Aboutimage(name=About_name, image=About_image)
            db.session.add(new_slider)
            db.session.commit()
            flash('New About uploaded successfully', 'success')
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

# Update form Courses
@app.route('/upload_Course', methods=['GET','POST'])
def upload_Course():
    if request.method == 'POST':
        Course_name = request.form['Course_name']
        Course_image = request.files['Course_image'].read()
        existing_Course = Coursesimage.query.filter_by(name=Course_name).first()
        if existing_Course:
            existing_Course.image = Course_image
            db.session.commit()
            flash('Course image updated successfully', 'success')
        else:
            new_Course = Coursesimage(name=Course_name, image=Course_image)
            db.session.add(new_Course)
            db.session.commit()
            flash('New Course uploaded successfully', 'success')
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

# Update form Administration
@app.route('/upload_Administration', methods=['GET','POST'])
def upload_Administration():
    if request.method == 'POST':
        Administration_name = request.form['Administration_name']
        Administration_image = request.files['Course_image'].read()
        existing_Administration = Administration.query.filter_by(name=Administration_name).first()
        if existing_Administration:
            existing_Administration.image = Administration_image
            db.session.commit()
            flash('Administration image updated successfully', 'success')
        else:
            new_Administration = Administration(name=Administration_name, image=Administration_image)
            db.session.add(new_Administration)
            db.session.commit()
            flash('New Administration uploaded successfully', 'success')
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))
  
# Button Funtions
# Delete button for the individual survey
@app.route('/delete/<int:id>')
def delete(id):
    survey = Survey1.query.get_or_404(id)
    db.session.delete(survey)
    db.session.commit()
    return redirect(url_for('admin'))

# Delete all Data at table Survey1
@app.route('/delete_all', methods=['POST'])
def delete_all():
    Survey1.query.delete()
    db.session.commit()
    return redirect(url_for('admin'))

# Logout Settings
@app.route('/logout')
def logout():
    return redirect(url_for('index'))

# Sebasty UI Settings
@app.route('/SEBASTYINDEX')
def SEBASTYINDEX():
    
    slides = {
        'Slide1': None,
        'Slide2': None,
        'Slide3': None,
        'Slide4': None
    }
    
    abouts = Aboutimage.query.all() 
    
    courses = {
        'GradeSchool': None,
        'JuniorHighSchool': None,
        'ABM': None,
        'HUMSS': None,
        'STEM': None,
        'BSHM': None,
        'BSTM': None,
        'BSFM': None,
        'BSBAMM': None,
        'BSCOMM': None,
        'BSA & BSMA': None,
        'BSPSYCH': None,
        'BSIEBSECE': None,
        'BSCPE': None,
        'BSIT': None,
        'BSCRIM': None,
        'BSN': None
    }

    for name, _ in courses.items():
        courses[name] = Coursesimage.query.filter_by(name=name).first()
        
    for slide, _ in slides.items():
        slides[slide] = Slider.query.filter_by(name=slide).first()
        

    for about in abouts:
        about.image = base64.b64encode(about.image).decode('utf-8')
        
    for name, course in courses.items():
        if course:
            course.image = base64.b64encode(course.image).decode('utf-8')
            
    for name, slide in slides.items():
        if slide:
            slide.image = base64.b64encode(slide.image).decode('utf-8')

    return render_template('SEBASTYINDEX.html', slides=slides, abouts=abouts, courses=courses)

#Survey Settings Sebastyui2 
@app.route('/survey', methods=['GET', 'POST'])
def formsurvey():
    if request.method == 'POST':
        name = request.form['name']
        There_Department = request.form['There_Department']
        There_TDepartment = request.form['There_TDepartment']
        rating = request.form['department_rating']
        suggestion = request.form['suggestion']
        srating = request.form['schoolrating']
        
        with app.app_context():
            new_survey = Survey1(name=name,There_Department=There_Department,There_TDepartment=There_TDepartment,rating=rating,suggestion=suggestion,srating=srating)
            db.session.add(new_survey)
            db.session.commit()
        
        flash('Survey submitted successfully', 'success')
        return render_template('Sebastyui.html')
    return render_template('Sebastyui.html')
  
@app.route('/SebastyUI')
def SebastyUI():
    return render_template('Sebastyui.html')
  


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input'].lower()
    responses = load_responses()
    bot_response = ''

    if user_input == 'quit':
        bot_response = "Goodbye!"
    elif user_input in responses:
        bot_response = responses[user_input]
    else:
        # Store unknown question to a JSON file
        store_unknown_question(user_input)
        bot_response = "Sorry, I don't know the answer to that question."

    return jsonify({'bot_response': bot_response})

@app.route('/answer', methods=['POST'])
def answer():
    question = request.form['question']
    answer = request.form['answer']
    
    responses = load_responses()
    responses[question.lower()] = answer
    save_responses(responses)
    
    unknown_questions = load_unknown_questions()
    unknown_questions.remove(question)  # Remove answered question from unknown_questions
    save_unknown_questions(unknown_questions)
    
    return redirect(url_for('admin'))

  
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
