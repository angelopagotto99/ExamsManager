# Progetto Basi di Dati mod.2 2022-23
# Componenti:   Pagotto Angelo(875829), Berto Giovanni(), Zemello Samuele(882735)

# Gestione delle votazioni dello studente.
# Funzionalità:
# 	1. Aggiunta della votazione per lo studente(controllo del numero dei test per Esami, il tipo di voto(se Scritto si dà un voto da 18 a 31, INS altrimenti))
# 	2. Mostra La Lista di tutti gli studenti con la loro valutazionec
# 	3. Modifica del voto

import string
import random
from imghdr import tests

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date, datetime
from flask import Flask, flash, redirect, render_template, request, url_for

# mantiene il collegamento con l'app principale mainPage
app_teacherValutation = Blueprint('app_teacherValutation', __name__)

# creazione dell'engine - inserisci le credenziali in modo sicuro
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


# ...

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

'''
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
'''

@app_teacherValutation.route('/showAllEnrolledStudents/<int:IdExam>', methods=['GET', 'POST'])
@login_required
def showAllEnrolledStudents(IdExam):
    if current_user.is_authenticated:
        # Mostra tutti gli studenti iscritti ai relativi corsi
        AllStudents = session.query(EnrolledStudents.IdStudent, Students.Surname, Students.Name, Students.Email).filter(
            and_(EnrolledStudents.IdStudent == Students.Id, EnrolledStudents.IdExam == IdExam)).order_by(Students.Email)

        return render_template('teacherShowMyEnrolledStudents.html', myStudents=AllStudents, IdExam=IdExam)
    else:
        return redirect('/')


# ...

@app_teacherValutation.route('/deleteCurrentTest', methods=['GET', 'POST'])
@login_required
def deleteCurrentTest(dates=None):
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form.get("IdExam"))
            IdTestForm = int(request.form.get("IdTest"))

            # Rimuovi appelli e test
            session.query(Appeals).filter(Appeals.IdTest == IdTestForm).delete()
            session.query(Tests).filter(and_(Tests.IdExam == IdExamForm, Tests.Id == IdTestForm)).delete()

            session.commit()

            AllExams = session.query(Exams.Id, Exams.nTest).filter(Tests.IdExam == IdExamForm)
            return render_template('teacherShowMyTests.html', IdExam=IdExamForm, myTest=tests, myAppeal=dates,
                                   myExam=AllExams)

        except Exception as e:
            # Gestisci l'errore in modo appropriato, ad esempio registralo
            print(f"Errore durante la cancellazione del test: {e}")
            session.rollback()
            return redirect('/')
    else:
        return redirect('/')


@app_teacherValutation.route('/updateCurrentTest', methods=['GET', 'POST'])
@login_required
def updateCurrentTest():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form.get("IdExam"))
            IdTestForm = int(request.form.get("IdTest"))

            # Ottieni i dati del test e degli appelli
            test = session.query(Tests).filter(Tests.IdExam == IdExamForm, Tests.Id == IdTestForm).first()
            appeal = session.query(Appeals).filter(Appeals.IdTest == IdTestForm).first()

            return render_template('teacherUpdateTests.html', myTest=test, IdExam=IdExamForm, IdTest=IdTestForm, myAppeal=appeal)
        except Exception as e:
            flash("Errore durante il recupero dei dati del test.", "error")
            return redirect('/')
    else:
        return redirect('/')

@app_teacherValutation.route('/ReUpdateCurrentTest', methods=['POST'])
@login_required
def ReUpdateCurrentTest():
    if current_user.is_authenticated:
        try:
            IdTestForm = int(request.form.get("IdTest"))
            IdExamForm = int(request.form.get("IdExam"))
            NameForm = request.form.get("name")
            TipoForm = request.form.get("type")
            ValForm = request.form.get("value")
            DataForm = request.form.get("date")

            # Aggiorna i dati del test e dell'appello
            session.query(Tests).filter(Tests.Id == IdTestForm, Tests.IdExam == IdExamForm).update({
                Tests.TestName: NameForm,
                Tests.Tipology: TipoForm,
                Tests.ValType: ValForm
            })
            session.query(Appeals).filter(Appeals.IdTest == IdTestForm).update({Appeals.ExamData: DataForm})

            session.commit()
            flash("Dati del test aggiornati con successo.", "success")
        except Exception as e:
            session.rollback()
            flash("Si è verificato un errore durante l'aggiornamento dei dati del test.", "error")
        finally:
            return redirect('/')

    else:
        return redirect('/')

# ...

@app_teacherValutation.route('/registrationTest', methods=['POST'])
@login_required
def registrationTest():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form.get("IdExam"))
            return render_template('teacherRegistrationTest.html', IdExam=IdExamForm)
        except Exception as e:
            flash("Errore durante la registrazione del test.", "error")
            return redirect('/')
    else:
        return redirect('/')

# ...

@app_teacherValutation.route('/registrationAppeal', methods=['POST'])
@login_required
def registrationAppeal():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form.get("IdExam"))
            IdTestForm = int(request.form.get("IdTest"))
            return render_template('teacherRegistrationAppeal.html', IdExam=IdExamForm, IdTest=IdTestForm)
        except Exception as e:
            flash("Errore durante la registrazione dell'appello.", "error")
            return redirect('/')
    else:
        return redirect('/')

