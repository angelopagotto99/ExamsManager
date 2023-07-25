# Progetto Basi di Dati mod.2 2023
# Componenti:   Pagotto Angelo(875829), Berto Giovanni (), Zemello Samuele (882735)

# Gestione degli esami del docente.
# Funzionalità:
# 	1. Aggiunta del proprio esame
# 	2. Mostrare gli esami aggiunti
# 	3. Cancellazione di un esame
#   4. Mostrare i voti di ciascun esame sostenuto
#   5. Mostrare quanti e quali studenti partecipano all' esame del giorno


from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date

# mantiene il collegamento con l'app principale mainPage
app_teacherExam = Blueprint('app_teacherExam', __name__)

# creazione dell'engine
engine = create_engine('postgresql+pg8000://postgres:Angelo99@localhost:5432/Exams_Manager', echo=True)

# creazione della sessione
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)

# importa i dati delle tabelle del database
Students = Base.classes.Students
Teachers = Base.classes.Teachers
Exams = Base.classes.Exams
isEnrolled = Base.classes.isEnrolled




@app_teacherExam.route('/newExam', methods=['GET', 'POST'])
@login_required
def newExam():
    ExamForm = request.form["exam"]
    DescriptionForm = request.form["description"]
    nTestForm = int(request.form["nTest"])
    FacultyForm = request.form["num"]
    CFUForm = int(request.form["CFU"])
    if current_user.is_authenticated:
        if request.method == 'POST':
            # controllo sul titolo del corso
            usedTitle = session.query(Exams.Id).filter(Exams.ExamName == ExamForm).first()
            if usedTitle is None:  # controlla se titleForm è usata da qualche docente
                # titleForm non è usata da nessun docente
                # aggiungo il corso al database
                newExam = Exams(ExamName=ExamForm, Description=DescriptionForm, nTest=nTestForm,
                                    Faculty=FacultyForm, CFU=CFUForm,
                                    IdTeacher=current_user.id)
                session.add(newExam)  # aggiunge il corso al database
                session.commit()  # conferma le modifiche
                return render_template('teacherArea.html', name=current_user.name, surname=current_user.surname)
            else:
                return render_template('teacherExamRegistration.html', error="titolo", title=ExamForm,
                                       Description=DescriptionForm,
                                       nTest=nTestForm, Faculty=FacultyForm, CFU=CFUForm)
        else:
            return redirect('/newExam')
    else:
        return redirect('/')



@app_teacherExam.route('/showAllTeacherExam')
@login_required
def showAllTeacherCourses():
    if current_user.is_authenticated:
        # Mostra tutti i corsi del docente corrente
        AllExams = session.query(Exams.Id, Exams.ExamName, Exams.Description, Exams.nTest, Exams.Faculty, Exams.CFU,
                                   Exams.IdTeacher).filter(Exams.IdTeacher == current_user.id)

        # numero d'iscrizioni fatte per ciascun esame
        nEnrollmentsGroup = \
            session.query(func.count(isEnrolled.Id), isEnrolled.IdExam, Exams.nTest) \
                .join(Exams) \
                .group_by(isEnrolled.IdExam, Exams.MaxEnrollments)
        enrolledCoursesId = session.query(EnrolledStudents.IdCourse).distinct(EnrolledStudents.IdCourse)
        neverEnrolledCourses = session.query(Courses.Id, Courses.MaxEnrollments).filter(
            Courses.Id.notin_(enrolledCoursesId))

        # informazioni riguardo i docenti
        teachersInfo = session.query(Teachers.Id, Teachers.Name, Teachers.Surname)
        return render_template('teacherShowMyCourses.html', teachersInfo=teachersInfo,
                               myCourses=AllCourses, nEnrollmentsGroup=nEnrollmentsGroup,
                               neverEnrolledCourses=neverEnrolledCourses)
    else:
        return redirect('/')

'''

@app_teacherExam.route('/showAllEnrolledStudents', methods=['GET', 'POST'])
@login_required
def enrolledStudents():
    if current_user.is_authenticated:
        IdCourseForm = int(request.form["IdCourse"])
        # Mostra tutti gli studenti iscritti ai relativi corsi
        AllStudents = session.query(EnrolledStudents.IdStudent, Students.Surname, Students.Name,
                                    EnrolledStudents.EnrollmentDate,
                                    Students.Email).filter(
            and_(EnrolledStudents.IdStudent == Students.Id, EnrolledStudents.IdCourse == IdCourseForm)).order_by(
            Students.Email)

        return render_template('teacherShowMyEnrolledStudents.html', myStudents=AllStudents)
    else:
        return redirect('/')


# tengo o non tengo traccia delle lezioni che ha svolto lo studente relative al corso?
# tengo o non tengo traccia delle prenotazioni dello studente relative al corso?
@app_teacherExam.route('/unenrollCourse', methods=['GET', 'POST'])
def unenrollCourse():
    if current_user.is_authenticated:
        IdCourseForm = int(request.form["IdCourse"])

        # rimuovo l'occorrenza che identifica che lo studente segue quel corso
        session.query(EnrolledStudents).filter(and_(EnrolledStudents.IdCourse == IdCourseForm)).delete()
        lessonsId = session.query(Lessons.Id).filter(Lessons.IdCourse == IdCourseForm)
        session.query(OnlineLessons).filter(and_(OnlineLessons.Id.in_(lessonsId))).delete(synchronize_session='fetch')
        session.query(FaceToFaceLessons).filter(and_(FaceToFaceLessons.Id.in_(lessonsId))).delete(synchronize_session='fetch')
        session.query(Lessons).filter(and_(Lessons.IdCourse == IdCourseForm)).delete()
        session.query(Courses).filter(and_(Courses.Id == IdCourseForm)).delete()
        session.commit()

        return render_template('teacherArea.html')
    else:
        return redirect('/')


# controllare il numero di posti disponibili nelle lezioni FTF per garantire la possibilità di prenotarsi
@app_teacherExam.route('/showTeacherLessons', methods=['GET', 'POST'])
def showTeacherLessons():
    if current_user.is_authenticated:
        IdCourseForm = int(request.form["IdCourse"])

        lessons = session.query(Lessons).filter(Lessons.IdCourse == IdCourseForm).order_by(Lessons.Date)
        courseInfo = session.query(Courses).filter(Courses.Id == IdCourseForm)

        return render_template('teacherShowMyLessons.html', lessons=lessons, course=courseInfo)
    else:
        return redirect('/')

'''

@app_teacherExam.route('/registrationExam')
def registrationExam():
    return render_template('teacherExamRegistration.html')
