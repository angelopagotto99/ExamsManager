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
    IdAppealForm = int(request.form["IdAppeal"])

    if current_user.is_authenticated:
        if request.method == 'POST':
            # controllo sul titolo del corso
            # Verifica se esiste già una riga con Valutation non NULL per lo studente e l'appello specificato
            existing_valutation = session.query(Sustains).filter(
                Sustains.IdStudent == IdStudentForm,
                Sustains.IdAppeal == IdAppealForm
            ).first()
            myValutations = session.query(Sustains).filter(Sustains.IdAppeal == IdAppealForm).all()

            session.query(Sustains).filter(
                    and_(Sustains.IdStudent == IdStudentForm, Sustains.IdAppeal == IdAppealForm)).update(
                    {Sustains.Valutation: ValutationForm})
            AllStudents = session.query(Sustains.IdStudent, Students.Surname, Students.Name, Students.Email).filter(
                and_(Sustains.IdAppeal == IdAppealForm)).order_by(Students.Email)
            session.commit()  # conferma le modifiche
            return render_template('teacherShowMyEnrolledStudents.html', IdAppeal=IdAppealForm, IdStudent=IdStudentForm,myStudents=AllStudents,
                                       IdValutations=myValutations)

        else:
            return redirect('/newValutation')
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

