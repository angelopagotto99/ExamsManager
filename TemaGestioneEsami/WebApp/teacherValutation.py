# Progetto Basi di Dati mod.2 2022-23
# Componenti:   Pagotto Angelo(875829), Berto Giovanni(), Zemello Samuele(882735)

# Gestione delle votazioni dello studente.
# Funzionalità:
# 	1. Aggiunta della votazione per lo studente
#   1.1 Controlliamo il campo isIdoneo dell'esame: se false-> allora la valutazione finale dovrà essere tra 18 e 30+1, altrimenti IDONEO
#   1.2 Controlliamo se lo studente ha sostenuto e passato tutte le prove previste dall'esame: se si allora si registra la valutazione per lo studente, altrimenti no
#   1.3 Query per calcolare la media dei voti presi nei test e registrazione automatica del voto lato studente dopo aver passato tutti i test
#   1.4 Il voto deve essere salvato nel libretto con un valore intero per gli esami che prevedono una valutazione in 30esimi

# 	2. Mostra La Lista di tutti gli studenti con la loro valutazione
# 	3. Modifica del voto lato docente

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
app_teacherValutation = Blueprint('app_teacherValutation', __name__)

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


@app_teacherValutation.route('/newValutation', methods=['GET', 'POST'])
@login_required
def newValutationPartial():
    ValutationForm = float(request.form["valutation"])
    IdStudentForm = int(request.form["IdStudent"])
    # IdAppealForm = int(request.form["IdAppeal"])

    if current_user.is_authenticated:
        if request.method == 'POST':
            # controllo sul titolo del corso
            # Verifica se esiste già una riga con Valutation non NULL per lo studente e l'appello specificato
            existing_valutation = session.query(Sustains).filter(
                Sustains.IdStudent == IdStudentForm,
                Sustains.IdAppeal == Appeals.Id
            ).first()
            myValutations = session.query(Sustains).filter(Sustains.IdStudent==IdStudentForm).all()

            if existing_valutation.Valutation is None:  # controlla se titleForm è usata da qualche docente
                # titleForm non è usata da nessun docente
                session.query(Sustains).filter(and_(Sustains.IdStudent==IdStudentForm, Sustains.IdAppeal == Appeals.Id)).update({Sustains.Valutation:ValutationForm})
                session.commit()  # conferma le modifiche
                return render_template('teacherShowMyEnrolledStudents.html', IdStudent=IdStudentForm, Valutations=myValutations)
            else:
                return render_template('teacherGiveValutation.html', error="Valutazione già presente", IdStudent=IdStudentForm)
        else:
            return redirect('/newValutationPartial')
    else:
        return redirect('/')

@app_teacherValutation.route('/newValutationFinal', methods=['GET', 'POST'])
@login_required
def newValutationFinal():
    IdStudentForm = int(request.form["IdStudent"])
    IdExamForm = int(request.form["IdExam"])


    if current_user.is_authenticated:
        if request.method == 'POST':
            if current_user.Id == EnrolledStudents.IdStudent:
                if Exams.isIdoneo == False:
                    tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)
                    sustains = session.query(Sustains).filter(Sustains.IdStudent == IdStudentForm).order_by(Sustains.IdStudent)

                    session.query(EnrolledStudents).filter(EnrolledStudents.IdStudent==IdStudentForm).update({EnrolledStudents.Valutation:"IDONEO"})

                else:
            else:
                render_template('studentShowAllExam.html', error="studente non presente", IdStudent=IdStudentForm, IdExam=IdExamForm)

        else:
            return redirect('/newValutationPartial')
    else:
        return redirect('/')


@app_teacherValutation.route('/showAllEnrolledStudents/<int:IdExam>', methods=['GET', 'POST'])
@login_required
def showAllEnrolledStudents(IdExam):
    if current_user.is_authenticated:
        # Mostra tutti gli studenti iscritti ai relativi corsi
        AllStudents = session.query(EnrolledStudents.IdStudent, Students.Surname, Students.Name,
                                    Students.Email).filter(
            and_(EnrolledStudents.IdStudent == Students.Id, EnrolledStudents.IdExam == IdExam)).order_by(
            Students.Email)

        return render_template('teacherShowMyEnrolledStudents.html', myStudents=AllStudents, IdExam=IdExam)
    else:
        return redirect('/')

@app_teacherValutation.route('/showAllTeacherAppeal', methods=['GET', 'POST'])
@login_required
def showAllTeacherAppeal():
    if current_user.is_authenticated:


        # Recupera tutti gli esami del docente corrente
        exams = session.query(Exams).filter(Exams.IdTeacher == current_user.id).all()

        # Recupera tutti gli appelli dei test dei vari esami
        all_appeals_data = session.query(Appeals, Tests, Exams).join(Tests, Appeals.IdTest == Tests.Id).\
            join(Exams,Tests.IdExam == Exams.Id).filter(Exams.IdTeacher == current_user.id).\
            order_by(Tests.TestName, Appeals.ExamData).all()

        num_enrolled_students = session.query(func.count(Appeals.Id)).filter(Appeals.IdTest == Tests.Id).scalar()

        return render_template('teacherShowMyAppeal.html', exams=exams, all_appeals_data=all_appeals_data, Iscritti=num_enrolled_students)
    else:
        return redirect('/')


@app_teacherValutation.route('/deleteCurrentTest', methods=['GET', 'POST'])
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
        AllExams = session.query(Exams.Id, Exams.nTest).filter(Tests.IdExam == IdExamForm)
        return render_template('teacherShowMyTests.html', IdExam=IdExamForm, myTest=tests, myAppeal=dates, myExam=AllExams)
    else:
        return redirect('/')


@app_teacherValutation.route('/updateCurrentTest', methods=['GET', 'POST'])
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

@app_teacherValutation.route('/ReUpdateCurrentTest', methods=['GET', 'POST'])
@login_required
def ReUpdateCurrentTest():

    if current_user.is_authenticated:

        IdTestForm = int(request.form["IdTest"])
        IdExamForm = int(request.form["IdExam"])


        NameForm = request.form["name"]
        TipoForm = request.form["type"]
        ValForm = request.form["value"]
        DataForm= request.form["date"]

        session.query(Tests).filter(and_(Tests.Id == IdTestForm, Tests.IdExam == IdExamForm)).update({Tests.TestName: NameForm, Tests.Tipology: TipoForm, Tests.ValType: ValForm})
        session.query(Appeals).filter(and_(Appeals.IdTest==IdTestForm)).update({Appeals.ExamData:DataForm})

        session.commit()
        return render_template('teacherArea.html')
    else:
        return redirect('/')





@app_teacherValutation.route('/registrationTest', methods=['GET', 'POST'])
def registrationTest():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])
        return render_template('teacherRegistrationTest.html', IdExam=IdExamForm)
    else:
        return redirect('/')



