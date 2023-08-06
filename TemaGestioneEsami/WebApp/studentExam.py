# Progetto Basi di Dati mod.2 2023
# Componenti:   Pagotto Angelo(875829), Berto Giovanni (), Zemello Samuele (882735)

# Gestione degli esami del docente.
# Funzionalità:
# 	1. Aggiunta del proprio esame
# 	2. Mostrare gli esami aggiunti
# 	3. Cancellazione di un esame
#   4. Mostrare i voti di ciascun esame sostenuto
#   5. Mostrare quanti e quali studenti partecipano all' esame del giornoc


from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date
from sqlalchemy.orm import joinedload

# mantiene il collegamento con l'app principale mainPage
app_studentExam = Blueprint('app_studentExam', __name__)

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
isEnrolled = Base.classes.IsEnrolled
Test = Base.classes.Tests
Appeals = Base.classes.ExamAppeals

@app_studentExam.route('/showAllCourses')
@login_required
def showAllCourses():
    if current_user.is_authenticated:
        # tutti i corsi esistenti
        allCourses = session.query(Exams.Id, Exams.ExamName, Exams.Description, Exams.nTest, Exams.CFU, Exams.Faculty,
                                   Exams.IdTeacher)
        # i corsi a cui sono già iscritto
        myCourses = session.query(isEnrolled.IdExam).filter(current_user.id == isEnrolled.IdStudent)
        # lista dei corsi a cui posso iscrivermi
        displayCourses = session.query(Exams.Id, Exams.ExamName, Exams.Description, Exams.nTest, Exams.CFU, Exams.Faculty,
                                       Exams.IdTeacher).filter(Exams.Id.notin_(myCourses))


        # informazioni riguardo i docenti
        teachersInfo = session.query(Teachers.Id, Teachers.Name, Teachers.Surname)

        return render_template('studentShowAllExam.html', courses=displayCourses, teachersInfo=teachersInfo,
                               myCourses=allCourses)
    else:
        return redirect('/')

@app_studentExam.route('/showAllExamTest', methods=['GET', 'POST'])
def showAllExamTest():
    if current_user.is_authenticated:
        # Mostra tutti test dell'esame del docente corrente
        IdExamForm = int(request.form["IdExam"])


        tests = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm)
        tests = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        # Recupera tutti gli id dei test associati all'esame
        test_ids = [test.Id for test in tests]
        AllAppealData = session.query(Appeals).filter(Appeals.IdTest == test_ids)
        # Recupera le date degli appelli per ciascun test
        AllExams = session.query(Exams.Id, Exams.nTest).filter(Test.IdExam == IdExamForm)
        return render_template('studentShowAllExamTests.html', myTest=tests, myAppeal=AllAppealData, test=tests, exam=testInfo,myExam=AllExams)
    else:
        return redirect('/')

@app_studentExam.route('/showMyEnrolledExam')
@login_required
def showMyEnrolledExam():
    if current_user.is_authenticated:
        myCourses = session.query(isEnrolled.IdExam).filter(current_user.id == isEnrolled.IdStudent)
        coursesInfo = session.query(Exams).filter(Exams.Id.in_(myCourses)).order_by(Exams.ExamName)
        return render_template('studentShowMyEnrolledExams.html', myCourses=coursesInfo)
    else:
        return redirect('/')

@app_studentExam.route('/enrollStudent', methods=['GET', 'POST'])
@login_required
def enrollStudent():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form["IdExam"])

            # Controlla se lo studente è già iscritto all'esame
            existing_enrollment = session.query(isEnrolled).filter(
                isEnrolled.IdExam == IdExamForm,
                isEnrolled.IdStudent == current_user.id
            ).first()

            if existing_enrollment:
                return render_template('studentArea.html', message="Sei già iscritto a questo esame.")

            newEnrollment = isEnrolled(IdStudent=current_user.id, IdExam=IdExamForm)
            session.add(newEnrollment)
            session.commit()

            return render_template('studentArea.html')
        except Exception as e:
            print("Errore:", str(e))  # Tratta l'errore in modo appropriato
            return redirect('/')
    else:
        return redirect('/')

# tengo o non tengo traccia delle prenotazioni dello studente relative all' esame?
@app_studentExam.route('/unenrollExam', methods=['GET', 'POST'])
@login_required
def unenrollExam():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form["IdExam"])

            # Rimuovi l'iscrizione dello studente
            existing_enrollment = session.query(isEnrolled).filter(
                isEnrolled.IdExam == IdExamForm,
                isEnrolled.IdStudent == current_user.id
            ).first()

            if existing_enrollment:
                session.delete(existing_enrollment)  # Rimuove l'iscrizione esistente
                session.commit()

            return render_template('studentArea.html')
        except Exception as e:
            print("Errore:", str(e))  # Tratta l'errore in modo appropriato
            return redirect('/')
    else:
        return redirect('/')

# mostra tutti i test creati per un certo esame
@app_studentExam.route('/showTeacherTests', methods=['GET', 'POST'])
def showTeacherTests():
    if current_user.is_authenticated:
        # Mostra tutti test dell'esame del docente corrente
        IdExamForm = int(request.form["IdExam"])


        tests = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm)
        tests = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        # Recupera tutti gli id dei test associati all'esame
        test_ids = [test.Id for test in tests]
        AllAppealData = session.query(Appeals).filter(Appeals.IdTest == test_ids)
        # Recupera le date degli appelli per ciascun test
        AllExams = session.query(Exams.Id, Exams.nTest).filter(Test.IdExam == IdExamForm)
        return render_template('teacherShowMyTests.html', myTest=tests, myAppeal=AllAppealData, test=tests, exam=testInfo,myExam=AllExams)
    else:
        return redirect('/')


