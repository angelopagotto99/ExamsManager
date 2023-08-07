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
        # Gli appelli a cui sono già iscritto
        myAppeal_ids = session.query(Sustains.IdAppeal).filter(current_user.id == Sustains.IdStudent)

        # Lista di tutti gli appelli disponibili (esclusi quelli a cui sono già iscritto)
        availableAppeals = session.query(Appeals.Id, Exams.ExamName, Tests.TestName,
                                         Exams.Faculty, Exams.IdTeacher,
                                         Appeals.IdTest).filter(Appeals.Id.notin_(myAppeal_ids))

        # Numero di iscrizioni fatte per ciascun corso
        nEnrollmentsGroup = \
            session.query(func.count(Sustains.Id), Sustains.IdAppeal) \
                .group_by(Sustains.IdAppeal)

        # Informazioni riguardo i docenti
        teachersInfo = session.query(Teachers.Id, Teachers.Name, Teachers.Surname)

        return render_template('studentShowAllAppeal.html', courses=availableAppeals, teachersInfo=teachersInfo,
                               nEnrollmentsGroup=nEnrollmentsGroup)
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

        # Controlla se lo studente è già iscritto all'appello
        already_enrolled = session.query(Sustains).filter(
            Sustains.IdStudent == current_user.id,
            Sustains.IdAppeal == IdAppealForm,
            Sustains.isValid == True
        ).first()

        if already_enrolled:
            return render_template('studentArea.html', name=current_user.name, surname=current_user.surname)

        newEnrollment = Sustains(IdStudent=current_user.id, IdAppeal=IdAppealForm, isValid=True)
        session.add(newEnrollment)
        session.commit()

        return render_template('studentArea.html', name=current_user.name, surname=current_user.surname)
    else:
        return redirect('/')



