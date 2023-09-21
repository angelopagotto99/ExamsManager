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
            AllStudents = session.query(Sustains , Students).filter(
                and_(Sustains.IdAppeal == IdAppealForm)).order_by(Students.Email)
            session.commit()  # conferma le modifiche
            return render_template('teacherShowMyEnrolledStudents.html', IdAppeal=IdAppealForm, IdStudent=IdStudentForm,myStudents=AllStudents,
                                       IdValutations=myValutations)

        else:
            return redirect('/newValutation')
    else:
        return redirect('/')



@app_teacherValutation.route('/newValutationFinal', methods=['GET', 'POST'])
@login_required
def newValutationFinal():
    IdExamForm = int(request.form["IdExam"])

    if current_user.is_authenticated:
        if request.method == 'POST':
            student_enrollment = session.query(EnrolledStudents).filter(
                EnrolledStudents.IdStudent == current_user.id,
                EnrolledStudents.IdExam == IdExamForm
            ).first()

            if student_enrollment:
                exam = session.query(Exams).filter(Exams.Id == IdExamForm).first()

                # Calcola la media dei voti dei risultati degli appelli
                # ottenuti dallo studente per i test previsti dall'esame
                average_valutation = session.query(func.avg(Sustains.Valutation)) \
                    .join(Appeals, Sustains.IdAppeal == Appeals.Id) \
                    .join(Tests, Appeals.IdTest == Tests.Id) \
                    .filter(Sustains.IdStudent == current_user.id, Tests.IdExam == IdExamForm) \
                    .scalar()

                # Recupera tutti gli ID degli appelli associati ai test
                myTest = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName).all()
                test_ids = [test.Id for test in myTest]
                myAppeal = session.query(Appeals).filter(Appeals.IdTest.in_(test_ids)).all()
                appeal_ids = [appeal.Id for appeal in myAppeal]

                if average_valutation is not None:
                    average_valutation = round(average_valutation, 2)

                    # Controlla se tutti i voti dei test sono diversi da null
                    all_tests_graded = session.query(Sustains).filter(
                        and_(Sustains.IdStudent == current_user.id, Sustains.IdAppeal.in_(appeal_ids)),
                        Sustains.Valutation.is_(None)
                    ).count() == 0

                    # Controlla se la media dei voti è compresa tra 18 e 30
                    is_average_valid = 18 <= average_valutation <= 30

                    # Controllo sulla data di scadenza
                    current_date = datetime.now()
                    is_valid_date = all(datetime.strptime(appeal.ValutationExpireData, '%Y-%m-%dT%H:%M') >= current_date for appeal in myAppeal)

                    # Aggiorna la tabella EnrolledStudents con le prime due cifre decimali della media calcolata
                    if all_tests_graded and is_average_valid and not exam.isIdoneo and is_valid_date:
                        student_enrollment.Valutation = average_valutation
                        session.commit()
                    else:
                        student_enrollment.Valutation = "IDONEITA'"
                        session.commit()

                    # Query per recuperare le informazioni sugli esami associati all'esame
                    testInfo = session.query(Exams).filter(Exams.Id == IdExamForm).first()

                    # Query per recuperare le valutazioni dello studente per i test
                    student_valutations = session.query(Sustains).filter(
                        and_(Sustains.IdStudent == current_user.id, Sustains.IdAppeal.in_(appeal_ids))
                    ).all()

                    # Creare un dizionario per memorizzare le valutazioni dei test dello studente
                    student_test_grades = {valutation.IdAppeal: valutation.Valutation for valutation in student_valutations}
                    return render_template('studentShowAllExamTests.html', student_test_grades=student_test_grades,
                                           IdExam=IdExamForm, myTest=myTest)

            else:
                myTest = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName).all()
                return render_template('studentShowAllExamTests.html', error="studente non presente", IdExam=IdExamForm, myTest=myTest)

    else:
        myTest = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName).all()
        return render_template('studentShowAllExamTests.html', error="studente non presente", IdExam=IdExamForm, myTest=myTest)

    return redirect('/newValutationFinal')












