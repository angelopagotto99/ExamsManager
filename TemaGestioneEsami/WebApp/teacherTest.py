# Progetto Basi di Dati mod.2 2022
# Nome gruppo:  PagReg9900
# Componenti:   Pagotto Angelo(875829), Regazzo Andrea (881486)

# Gestione delle lezioni del docente.
# Funzionalità:
# 	1. Aggiunta delle lezioni al corso
# 	2. Distinzione fra lezione online e in presenza(FTF)
# 	3. Cancellazione di una lezione
#   4. Modifica di una lezione

import string
import random
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date, datetime

# mantiene il collegamento con l'app principale mainPage
app_teacherTest = Blueprint('app_teacherTest', __name__)

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
Tests = Base.classes.Tests
EnrolledStudents = Base.classes.IsEnrolled
Appeals = Base.classes.ExamAppeals



@app_teacherTest.route('/newTest', methods=['GET', 'POST'])
@login_required
def newTest():
    IdExamForm = int(request.form["IdExam"])
    NameForm = request.form["name"]
    TipoForm = request.form["type"]
    ValForm = request.form["value"]
    DateForm = request.form["data"]  # si decide la data del proprio test di quell'esame
    # dateFormCast = datetime.strptime(DateForm, '%d/%m/%Y').date()

    if current_user.is_authenticated:

        if request.method == 'POST':
            # aggiungo la lezione al database
            checkUsedName = session.query(Tests.Id).filter(and_(Tests.TestName == NameForm,
                                                                       Tests.Id == IdExamForm)).first()

            if checkUsedName is None:
                newTests = Tests(TestName=NameForm, Tipology=TipoForm ,ValType=ValForm, IdExam=IdExamForm, IdResponsabile=current_user.id)
                session.add(newTests)  # aggiunge il corso al database
                session.commit()  # conferma le modifiche
                idTests = session.query(Tests.Id).filter(
                    and_(Tests.TestName == NameForm, Tests.Tipology == TipoForm,
                         Tests.ValType == ValForm,
                         Tests.IdExam == IdExamForm)).first()
                AllExams = session.query(Exams.Id, Exams.ExamName, Exams.Description, Exams.nTest, Exams.Faculty,
                                         Exams.CFU,
                                         Exams.Enrollments,
                                         Exams.IdTeacher).filter(Exams.IdTeacher == current_user.id)
                newExamAppeal = Appeals(ExamData=DateForm, IdTest=idTests.Id)
                session.add(newExamAppeal)
                session.commit()
                AllAppealData = session.query(Appeals.Id, Appeals.ExamData, Appeals.IdTest).filter(Appeals.IdTest == idTests.Id)
                return render_template('teacherShowMyExams.html', IdTest=idTests, checkUsedName=checkUsedName , IdExam=IdExamForm, myCourses=AllExams, myAppeal=AllAppealData)

            else:
                return render_template('teacherRegistrationTest.html', error="Nome del test già utilizzato",
                                           IdTest=IdExamForm,
                                           tipology=TipoForm,
                                           valtype=ValForm, IdExam=IdExamForm)


        else:
            return redirect('/newTest')
    else:
        return redirect('/')


@app_teacherTest.route('/showAllTeacherTests', methods=['GET', 'POST'])
@login_required
def showAllTeacherTests():
    if current_user.is_authenticated:
        # Mostra tutti test dell'esame del docente corrente
        IdExamForm = int(request.form["IdExam"])
        IdTestForm = int(request.form["IdTest"])


        tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)
        AllAppealData = session.query(Appeals).filter(Appeals.IdTest == IdTestForm)
        return render_template('teacherShowMyTests.html', myTest=tests, myAppeal=AllAppealData)
    else:
        return redirect('/')

@app_teacherTest.route('/deleteCurrentTest', methods=['GET', 'POST'])
@login_required
def deleteCurrentTest():

    if current_user.is_authenticated:

        IdExamForm = int(request.form["IdExam"])
        IdTestForm = int(request.form["IdTest"])

        # Mostra tutti gli studenti iscritti ai relativi esami
        tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)
        dates = session.query(Appeals).filter(Appeals.IdTest == IdTestForm).order_by(Appeals.ExamData)
        session.query(Appeals).filter(and_(Appeals.IdTest == IdTestForm)).delete()
        session.query(Tests).filter(and_(Tests.IdExam == IdExamForm, Tests.Id==IdTestForm)).delete()

        session.commit()

        return render_template('teacherShowMyTests.html', IdExam=IdExamForm, myTest=tests, myAppeal=dates)
    else:
        return redirect('/')


@app_teacherTest.route('/updateCurrentTest', methods=['GET', 'POST'])
@login_required
def updateCurrentTest():

    if current_user.is_authenticated:

        IdExamForm = int(request.form["IdExam"])
        IdTestForm = int(request.form["IdTest"])
        tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).first()
        dates = session.query(Appeals).filter(Appeals.IdTest == IdTestForm).first()
        return render_template('teacherUpdateTests.html', myTest=tests, IdExam=IdExamForm, IdTest=IdTestForm, myAppeal=dates)
    else:
        return redirect('/')

@app_teacherTest.route('/ReUpdateCurrentTest', methods=['GET', 'POST'])
@login_required
def ReUpdateCurrentTest():

    if current_user.is_authenticated:

        IdTestForm = int(request.form["IdTest"])
        IdExamForm = int(request.form["IdExam"])


        NameForm = request.form["name"]
        TipoForm = request.form["type"]
        ValForm = request.form["value"]
        DataForm= request.form["date"]

        session.query(Tests).filter(and_(Tests.Id==IdTestForm, Tests.IdExam==IdExamForm)).update({Tests.TestName: NameForm , Tests.Tipology: TipoForm, Tests.ValType: ValForm})
        session.query(Appeals).filter(and_(Appeals.IdTest==IdTestForm)).update({Appeals.ExamData:DataForm})

        session.commit()
        return render_template('teacherArea.html')
    else:
        return redirect('/')

@app_teacherTest.route('/showAllEnrolledStudents', methods=['GET', 'POST'])
@login_required
def enrolledStudents():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])
        # Mostra tutti gli studenti iscritti ai relativi corsi
        AllStudents = session.query(EnrolledStudents.IdStudent, Students.Surname, Students.Name,
                                    EnrolledStudents.EnrollmentDate,
                                    Students.Email).filter(
            and_(EnrolledStudents.IdStudent == Students.Id, EnrolledStudents.IdExam == IdExamForm)).order_by(
            Students.Email)

        return render_template('teacherShowMyEnrolledStudents.html', myStudents=AllStudents)
    else:
        return redirect('/')


# controllare il numero di posti disponibili nelle lezioni FTF per garantire la possibilità di prenotarsi
@app_teacherTest.route('/showTeacherTests', methods=['GET', 'POST'])
@login_required
def showTeacherTests():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])

        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm)
        tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)

        # Recupera tutti gli id dei test associati all'esame
        test_ids = [test.Id for test in tests]

        # Recupera le date degli appelli per ciascun test
        AllAppealData = session.query(Appeals).filter(Appeals.IdTest.in_(test_ids))

        return render_template('teacherShowMyTests.html', myTest=tests, test=tests, exam=testInfo,
                               myAppeal=AllAppealData)
    else:
        return redirect('/')


@app_teacherTest.route('/registrationTest', methods=['GET', 'POST'])
def registrationTest():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])
        return render_template('teacherRegistrationTest.html', IdExam=IdExamForm)
    else:
        return redirect('/')

