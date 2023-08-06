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
from sqlalchemy.orm import relationship, joinedload
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
Sustains = Base.classes.Sustains



@app_teacherTest.route('/newTest', methods=['GET', 'POST'])
@login_required
def newTest():
    IdExamForm = int(request.form["IdExam"])
    NameForm = request.form["name"]
    TipoForm = request.form["type"]
    ValForm = request.form["value"]

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

                AllExams = session.query(Exams.Id,
                                         Exams.ExamName,
                                         Exams.Description,
                                         Exams.nTest,
                                         Exams.Faculty,
                                         Exams.CFU,
                                         Exams.IdTeacher,
                                         func.count(Tests.Id).label('NumTestCreati')) \
                    .outerjoin(Tests, Tests.IdExam == Exams.Id) \
                    .filter(Exams.IdTeacher == current_user.id) \
                    .group_by(Exams.Id,
                              Exams.ExamName,
                              Exams.Description,
                              Exams.nTest,
                              Exams.Faculty,
                              Exams.CFU,
                              Exams.IdTeacher)


                return render_template('teacherShowMyExams.html', IdTest=idTests, checkUsedName=checkUsedName , IdExam=IdExamForm, myCourses=AllExams)

            else:
                return render_template('teacherRegistrationTest.html', error="Nome del test già utilizzato",
                                           IdTest=IdExamForm,
                                           tipology=TipoForm,
                                           valtype=ValForm, IdExam=IdExamForm)


        else:
            return redirect('/newTest')
    else:
        return redirect('/')

@app_teacherTest.route('/newAppeal', methods=['GET', 'POST'])
@login_required
def newAppeal():
    IdExamForm = int(request.form["IdExam"])
    IdTestForm = int(request.form["IdTest"])
    DateForm = request.form["data"]  # si decide la data del proprio test di quell'esame
    DateExForm = request.form["dataEx"]
    # dateFormCast = datetime.strptime(DateForm, '%d/%m/%Y').date()

    if current_user.is_authenticated:

        if request.method == 'POST':
            # aggiungo la lezione al database
            checkUsedDate = session.query(Appeals.Id).filter(and_(Appeals.ExamData == DateForm,
                                                                Appeals.Id == IdTestForm)).first()

            if checkUsedDate is None:
                idTests = session.query(Tests.Id).filter(
                    and_(Tests.IdExam == IdExamForm)).first()
                AllExams = session.query(Exams.Id, Exams.ExamName, Exams.Description, Exams.nTest, Exams.Faculty,
                                         Exams.CFU,
                                         Exams.IdTeacher).filter(Exams.IdTeacher == current_user.id)
                newExamAppeal = Appeals(ExamData=DateForm, IdTest=IdTestForm, ValutationExpireData=DateExForm)
                session.add(newExamAppeal)
                session.commit()
                AllAppealData = session.query(Appeals.Id, Appeals.ExamData, Appeals.IdTest,Appeals.ValutationExpireData).filter(
                    Appeals.IdTest == idTests.Id)
                tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)
                return render_template('teacherShowMyTests.html', IdTest=idTests, checkUsedDate=checkUsedDate,
                                       IdExam=IdExamForm, myCourses=AllExams, myAppeal=AllAppealData, myTest=tests)

            else:
                return render_template('teacherRegistrationAppeal.html', error="Nome del test già utilizzato",
                                       IdTest=IdExamForm,IdExam=IdExamForm)


        else:
            return redirect('/newAppeal')
    else:
        return redirect('/')

@app_teacherTest.route('/showAllTeacherTests', methods=['GET', 'POST'])
@login_required
def showAllTeacherTests():
    if current_user.is_authenticated:
        # Mostra tutti test dell'esame del docente corrente
        IdExamForm = int(request.form["IdExam"])


        tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)


        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm)
        tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)

        # Recupera tutti gli id dei test associati all'esame
        test_ids = [test.Id for test in tests]
        AllAppealData = session.query(Appeals).filter(Appeals.IdTest == test_ids.Id)
        # Recupera le date degli appelli per ciascun test
        AllExams = session.query(Exams.Id, Exams.nTest).filter(Tests.IdExam == IdExamForm)
        return render_template('teacherShowMyTests.html', myTest=tests, myAppeal=AllAppealData, test=tests, exam=testInfo,myExam=AllExams)
    else:
        return redirect('/')

@app_teacherTest.route('/showAllTeacherAppeal', methods=['GET', 'POST'])
@login_required
def showAllTeacherAppeal():
    # tutti i corsi esistenti
        if current_user.is_authenticated:

            # Recupera tutti gli appelli dei test dei vari esami con il numero di iscritti per ciascun appello
            idTests = session.query(Tests.Id).filter(
                and_(Tests.IdExam == Exams.Id)).first()
            all_appeals_data = session.query(Appeals, Tests, Exams,
                                             func.count(Sustains.Id).label('NumEnrolledStudents')) \
                .join(Tests, Appeals.IdTest == Tests.Id) \
                .join(Exams, Tests.IdExam == Exams.Id) \
                .outerjoin(Sustains, Sustains.IdAppeal == Appeals.Id) \
                .filter(Exams.IdTeacher == current_user.id) \
                .group_by(Appeals.Id, Tests.Id, Exams.Id) \
                .order_by(Exams.ExamName, Tests.TestName, Appeals.ExamData) \
                .all()

            return render_template('teacherShowMyAppeal.html', all_appeals_data=all_appeals_data)
        else:
            return redirect('/')
@app_teacherTest.route('/showAllEnrolledStudents', methods=['GET', 'POST'])
@login_required
def enrolledStudents():
    if current_user.is_authenticated:
        IdAppealForm = int(request.form["IdAppeal"])
        # Mostra tutti gli studenti iscritti ai relativi corsi
        AllStudents = session.query(Students).join(Sustains, Students.Id == Sustains.IdStudent).filter(Sustains.IdAppeal == IdAppealForm).all()
        myValutations = session.query(Sustains).filter(Sustains.IdAppeal == IdAppealForm, Sustains.IdStudent == Students.Id).all()


        return render_template('teacherShowMyEnrolledStudents.html', myStudents=AllStudents, IdAppeal=IdAppealForm, Valutations=myValutations)
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
        session.query(Tests).filter(and_(Tests.IdExam == IdExamForm, Tests.Id == IdTestForm)).delete()

        session.commit()
        AllExams = session.query(Exams.Id, Exams.nTest).filter(Tests.IdExam == IdExamForm)
        return render_template('teacherShowMyTests.html', IdExam=IdExamForm, myTest=tests, myAppeal=dates, myExam=AllExams)
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

        session.query(Tests).filter(and_(Tests.Id == IdTestForm, Tests.IdExam == IdExamForm)).update({Tests.TestName: NameForm, Tests.Tipology: TipoForm, Tests.ValType: ValForm})

        session.commit()
        return render_template('teacherArea.html')
    else:
        return redirect('/')


@app_teacherTest.route('/registrationTest', methods=['GET', 'POST'])
def registrationTest():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])
        return render_template('teacherRegistrationTest.html', IdExam=IdExamForm)
    else:
        return redirect('/')

@app_teacherTest.route('/registrationAppeal', methods=['GET', 'POST'])
def registrationAppeal():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])
        IdTestForm = int(request.form["IdTest"])
        return render_template('teacherRegistrationAppeal.html', IdExam=IdExamForm, IdTest=IdTestForm)
    else:
        return redirect('/')

@app_teacherTest.route('/registrationValutation', methods=['GET', 'POST'])
def registrationValutationNotFinal():
    if current_user.is_authenticated:
        IdStudentForm = int(request.form["IdStudent"])
        IdAppealForm = int(request.form["IdAppeal"])
        return render_template('teacherGiveValutation.html', IdAppeal=IdAppealForm, IdStudent=IdStudentForm)
    else:
        return redirect('/')

