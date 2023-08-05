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
from sqlalchemy.orm import joinedload

# mantiene il collegamento con l'app principale mainPage
app_studentAppeal = Blueprint('app_studentAppeal', __name__)

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
Tests = Base.classes.Tests
Appeals = Base.classes.ExamAppeals
Sustains = Base.classes.Sustains

@app_studentAppeal.route('/showAllAppeals')
@login_required
def showAllAppeals():
    if current_user.is_authenticated:
        '''
        all_appeals_data = session.query(Appeals). \
            join(Tests, Appeals.IdTest == Tests.Id). \
            join(Exams, Tests.IdExam == Exams.Id). \
            options(joinedload(Appeals.Test).joinedload(Tests.Exam)). \
            order_by(Tests.TestName, Appeals.ExamData).all()
        '''
        all_appeals = session.query(Appeals, Tests, Exams).join(Tests, Appeals.IdTest == Tests.Id). \
            join(Exams, Tests.IdExam == Exams.Id). \
            order_by(Tests.TestName, Appeals.ExamData).all()

        return render_template('studentShowAllAppeal.html', allAppeal=all_appeals)
    else:
        return redirect('/')

@app_studentAppeal.route('/showMyEnrolledExam')
@login_required
def showMyEnrolledExam():
    if current_user.is_authenticated:
        myCourses = session.query(isEnrolled.IdExam).filter(current_user.id == isEnrolled.IdStudent)
        coursesInfo = session.query(Exams).filter(Exams.Id.in_(myCourses)).order_by(Exams.ExamName)
        return render_template('studentShowMyEnrolledExams.html', myCourses=coursesInfo)
    else:
        return redirect('/')

# studente che si iscrive all'appello
@app_studentAppeal.route('/enrollStudentAppeal', methods=['GET', 'POST'])
@login_required
def enrollStudentAppeal():
    if current_user.is_authenticated:
        IdAppealForm = int(request.form["IdAppeal"])
        today = date.today()

        newEnrollment = Sustains(IdStudent=current_user.id, IdAppeal=IdAppealForm)
        session.add(newEnrollment)
        session.commit()

        return render_template('studentArea.html', name=current_user.name, surname=current_user.surname)
    else:
        return redirect('/')



