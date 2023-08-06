# Progetto Basi di Dati mod.2 2022
# Nome gruppo:  PagReg9900
# Componenti:   Pagotto Angelo(875829), Regazzo Andrea (881486)

# Gestione delle lezioni del docente.
# Funzionalità:
# 	1. Aggiunta delle lezioni al corso
# 	2. Distinzione fra lezione online e in presenza(FTF)
# 	3. Cancellazione di una lezione
#   4. Modifica di una lezione

# Importazione delle librerie
import string
import random
from sqlalchemy import create_engine, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request, app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date, datetime

from TemaGestioneEsami.WebApp.teacherValutation import EnrolledStudents, Appeals

# Definizione dell'app Flask
app_teacherTest = Blueprint('app_teacherTest', __name__)

# Creazione dell'engine e della sessione per il database
engine = create_engine('postgresql+pg8000://postgres:Angelo99@localhost:5432/Exams_Manager', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
Base.metadata.reflect(engine)

# Definizione delle classi per le tabelle del database
class Students(Base):
    __table__ = Base.metadata.tables['Students']

class Teachers(Base):
    __table__ = Base.metadata.tables['Teachers']

class Exams(Base):
    __table__ = Base.metadata.tables['Exams']

class Tests(Base):
    __table__ = Base.metadata.tables['Tests']

class IsEnrolled(Base):
    __table__ = Base.metadata.tables['IsEnrolled']

class ExamAppeals(Base):
    __table__ = Base.metadata.tables['ExamAppeals']

# Definizione delle route

@app_teacherTest.route('/newTest', methods=['GET', 'POST'])
@login_required
def newTest():
    if current_user.is_authenticated:
        if request.method == 'POST':
            try:
                IdExamForm = int(request.form["IdExam"])
                NameForm = request.form["name"]
                TipoForm = request.form["type"]
                ValForm = request.form["value"]

                if not (NameForm and TipoForm and ValForm):
                    return render_template('error.html', message="Campi obbligatori mancanti.")

                existing_test = session.query(Tests).filter(and_(
                    Tests.TestName == NameForm,
                    Tests.Id == IdExamForm
                )).first()

                if existing_test:
                    return render_template('error.html', message="Nome del test già utilizzato.")

                new_test = Tests(
                    TestName=NameForm,
                    Tipology=TipoForm,
                    ValType=ValForm,
                    IdExam=IdExamForm,
                    IdResponsabile=current_user.id
                )

                session.add(new_test)
                session.commit()

                idTests = session.query(Tests.Id).filter(and_(
                    Tests.TestName == NameForm,
                    Tests.Tipology == TipoForm,
                    Tests.ValType == ValForm,
                    Tests.IdExam == IdExamForm
                )).first()

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

                return render_template('teacherShowMyExams.html', IdTest=idTests, checkUsedName=None, IdExam=IdExamForm, myCourses=AllExams)

            except Exception as e:
                print(f"An error occurred: {e}")
                return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
        else:
            return redirect('/newTest')
    else:
        return redirect('/')



@app_teacherTest.route('/newAppeal', methods=['GET', 'POST'])
@login_required
def newAppeal():
    if current_user.is_authenticated:
        if request.method == 'POST':
            try:
                IdExamForm = int(request.form["IdExam"])
                IdTestForm = int(request.form["IdTest"])
                DateForm = request.form["data"]
                DateExForm = request.form["dataEx"]

                checkUsedDate = session.query(Appeals.Id).filter(and_(
                    Appeals.ExamData == DateForm,
                    Appeals.Id == IdTestForm
                )).first()

                if checkUsedDate:
                    return render_template('teacherRegistrationAppeal.html', error="Data dell'appello già utilizzata",
                                           IdTest=IdExamForm, IdExam=IdExamForm)

                idTests = session.query(Tests.Id).filter(
                    and_(Tests.IdExam == IdExamForm)).first()

                AllExams = session.query(Exams.Id, Exams.ExamName, Exams.Description, Exams.nTest, Exams.Faculty,
                                         Exams.CFU,
                                         Exams.IdTeacher).filter(Exams.IdTeacher == current_user.id)

                new_exam_appeal = Appeals(
                    ExamData=DateForm,
                    IdTest=idTests.Id,
                    ValutationExpireData=DateExForm
                )

                session.add(new_exam_appeal)
                session.commit()

                AllAppealData = session.query(Appeals.Id, Appeals.ExamData, Appeals.IdTest, Appeals.ValutationExpireData).filter(
                    Appeals.IdTest == idTests.Id)

                tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)

                return render_template('teacherShowMyTests.html', IdTest=idTests, checkUsedDate=None, IdExam=IdExamForm, myCourses=AllExams, myAppeal=AllAppealData, myTest=tests)

            except Exception as e:
                print(f"An error occurred: {e}")
                return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
        else:
            return redirect('/newAppeal')
    else:
        return redirect('/')

@app_teacherTest.route('/showAllTeacherAppeal', methods=['GET', 'POST'])
@login_required
def showAllTeacherAppeal():
    if current_user.is_authenticated:
        try:
            session = Session()

            exams = session.query(Exams).filter(Exams.IdTeacher == current_user.id).all()
            tests = session.query(Tests).filter(Tests.IdExam.in_([exam.Id for exam in exams])).order_by(Tests.TestName)

            AllExams = session.query(Exams.Id, Exams.nTest).filter(Tests.IdExam == Exams.Id)

            all_appeals = session.query(Appeals, Tests, Exams).join(Tests, Appeals.IdTest == Tests.Id).\
                join(Exams, Tests.IdExam == Exams.Id).filter(Exams.IdTeacher == current_user.id).\
                order_by(Tests.TestName, Appeals.ExamData).all()

            num_enrolled_students = session.query(func.count(EnrolledStudents.Id)).filter(
                EnrolledStudents.IdExam == Tests.IdExam).scalar()

            return render_template('teacherShowMyAppeal.html', exams=AllExams, all_appeals_data=all_appeals, Iscritti=num_enrolled_students)

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
    else:
        return redirect('/')

@app_teacherTest.route('/deleteCurrentTest', methods=['POST'])
@login_required
def deleteCurrentTest():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form["IdExam"])
            IdTestForm = int(request.form["IdTest"])

            session = Session()

            tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).order_by(Tests.TestName)
            dates = session.query(Appeals).filter(Appeals.IdTest == IdTestForm).order_by(Appeals.ExamData)

            session.query(Appeals).filter(Appeals.IdTest == IdTestForm).delete()
            session.query(Tests).filter(and_(Tests.IdExam == IdExamForm, Tests.Id == IdTestForm)).delete()

            session.commit()

            AllExams = session.query(Exams.Id, Exams.nTest).filter(Tests.IdExam == IdExamForm)

            return render_template('teacherShowMyTests.html', IdExam=IdExamForm, myTest=tests, myAppeal=dates, myExam=AllExams)

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
    else:
        return redirect('/')


@app_teacherTest.route('/updateCurrentTest', methods=['GET', 'POST'])
@login_required
def updateCurrentTest():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form["IdExam"])
            IdTestForm = int(request.form["IdTest"])

            session = Session()

            tests = session.query(Tests).filter(Tests.IdExam == IdExamForm).first()
            dates = session.query(Appeals).filter(Appeals.IdTest == IdTestForm).first()

            return render_template('teacherUpdateTests.html', myTest=tests, IdExam=IdExamForm, IdTest=IdTestForm, myAppeal=dates)

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
    else:
        return redirect('/')

@app_teacherTest.route('/ReUpdateCurrentTest', methods=['POST'])
@login_required
def ReUpdateCurrentTest():
    if current_user.is_authenticated:
        try:
            IdTestForm = int(request.form["IdTest"])
            IdExamForm = int(request.form["IdExam"])

            NameForm = request.form["name"]
            TipoForm = request.form["type"]
            ValForm = request.form["value"]

            session = Session()

            session.query(Tests).filter(and_(Tests.Id == IdTestForm, Tests.IdExam == IdExamForm)).update({
                Tests.TestName: NameForm,
                Tests.Tipology: TipoForm,
                Tests.ValType: ValForm
            })

            session.commit()

            return render_template('teacherArea.html')

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
    else:
        return redirect('/')

@app_teacherTest.route('/registrationTest', methods=['POST'])
@login_required
def registrationTest():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form["IdExam"])
            return render_template('teacherRegistrationTest.html', IdExam=IdExamForm)

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
    else:
        return redirect('/')

@app_teacherTest.route('/registrationAppeal', methods=['POST'])
@login_required
def registrationAppeal():
    if current_user.is_authenticated:
        try:
            IdExamForm = int(request.form["IdExam"])
            IdTestForm = int(request.form["IdTest"])
            return render_template('teacherRegistrationAppeal.html', IdExam=IdExamForm, IdTest=IdTestForm)

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="Errore durante l'elaborazione della richiesta.")
    else:
        return redirect('/')

# Esegui l'app Flask
if __name__ == '__main__':
    app.run(debug=True)

