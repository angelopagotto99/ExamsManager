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
Sustains = Base.classes.Sustains

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
                                       Exams.IdTeacher).filter(Exams.Id.notin_(myCourses), Students.Id == current_user.id, Students.Faculty == Exams.Faculty)

        # numero d'iscrizioni fatte per ciascun corso
        nEnrollmentsGroup = \
            session.query(func.count(isEnrolled.Id), isEnrolled.IdExam) \
                .join(Exams) \
                .group_by(isEnrolled.IdExam)
        enrolledCoursesId = session.query(isEnrolled.IdExam).distinct(isEnrolled.IdExam)
        neverEnrolledCourses = session.query(Exams.Id).filter(
            Exams.Id.notin_(enrolledCoursesId))

        # informazioni riguardo i docenti
        teachersInfo = session.query(Teachers.Id, Teachers.Name, Teachers.Surname)

        return render_template('studentShowAllExam.html', courses=displayCourses, teachersInfo=teachersInfo,
                               allCourses=allCourses, nEnrollmentsGroup=nEnrollmentsGroup,
                               neverEnrolledCourses=neverEnrolledCourses)
    else:
        return redirect('/')

@app_studentExam.route('/showAllExamTest', methods=['GET', 'POST'])
def showAllExamTest():
    if current_user.is_authenticated:
        # Mostra tutti i test dell'esame del docente corrente
        IdExamForm = int(request.form["IdExam"])

        # Query per recuperare tutti i test associati all'esame
        myTest = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName).all()

        # Recupera tutti gli ID dei test associati all'esame
        test_ids = [test.Id for test in myTest]


        # Query per recuperare le informazioni sugli appelli associati ai test
        myAppeal = session.query(Appeals).filter(Appeals.IdTest.in_(test_ids)).all()

        # Recupera tutti gli ID degli appelli associati ai test
        appeal_ids = [appeal.Id for appeal in myAppeal]

        # Query per recuperare le informazioni sugli esami associati all'esame
        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm).first()

        # Query per recuperare le valutazioni dello studente per i test
        student_valutations = session.query(Sustains).filter(
            and_(Sustains.IdStudent == current_user.id, Sustains.IdAppeal.in_(appeal_ids))
        ).all()

        # Creare un dizionario per memorizzare le valutazioni dei test dello studente
        student_test_grades = {valutation.IdAppeal: valutation.Valutation for valutation in student_valutations}
        myVal = session.query(isEnrolled).filter(current_user.id == isEnrolled.IdStudent)
        average_valutation = session.query(func.avg(Sustains.Valutation)) \
            .join(Appeals, Sustains.IdAppeal == Appeals.Id) \
            .join(Test, Appeals.IdTest == Test.Id) \
            .filter(Sustains.IdStudent == current_user.id, Test.IdExam == IdExamForm, Sustains.isValid == True,
                    Sustains.Valutation != None) \
            .scalar()

        return render_template('studentShowAllExamTests.html', myTest=myTest, myAppeal=myAppeal,
                               exam=testInfo, myVal=student_valutations, student_test_grades=student_test_grades, IdExam=IdExamForm, media=average_valutation)
    else:
        return redirect('/')

@app_studentExam.route('/showMyEnrolledExam')
@login_required
def showMyEnrolledExam():
    if current_user.is_authenticated:
        myCourses = session.query(isEnrolled.IdExam).filter(current_user.id == isEnrolled.IdStudent)
        coursesInfo = session.query(Exams).filter(Exams.Id.in_(myCourses)).order_by(Exams.ExamName)
        myVal = session.query(isEnrolled).filter(current_user.id == isEnrolled.IdStudent)
        average_valutation = session.query(func.avg(Sustains.Valutation)) \
            .join(Appeals, Sustains.IdAppeal == Appeals.Id) \
            .join(Test, Appeals.IdTest == Test.Id) \
            .filter(Sustains.IdStudent == current_user.id, Test.IdExam == Exams.Id, Sustains.isValid == True,
                    Sustains.Valutation != None) \
            .scalar()

        return render_template('studentShowMyEnrolledExams.html', myCourses=coursesInfo, myVal=myVal, media=average_valutation)
    else:
        return redirect('/')

@app_studentExam.route('/enrollStudent', methods=['GET', 'POST'])
@login_required
def enrollStudent():
    if current_user.is_authenticated:
            IdExamForm = int(request.form["IdExam"])

            # Controlla se lo studente è già iscritto all'esame
            existing_enrollment = session.query(isEnrolled).filter(
                isEnrolled.IdExam == IdExamForm,
                isEnrolled.IdStudent == current_user.id
            ).first()

            if existing_enrollment:
                return render_template('studentArea.html', message="Sei già iscritto a questo esame.", name=current_user.name,surname=current_user.surname)

            newEnrollment = isEnrolled(IdStudent=current_user.id, IdExam=IdExamForm)
            session.add(newEnrollment)
            session.commit()

            return render_template('studentArea.html',name=current_user.name, surname=current_user.surname)
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

            return render_template('studentArea.html',name=current_user.name,surname=current_user.surname)
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

        # tutti i test di quell'esame
        myTest = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        # Recupera tutti gli id dei test associati all'esame
        test_ids = [test.Id for test in myTest]

        # Query per recuperare le informazioni sugli appelli associati ai test
        myAppeal = session.query(Appeals).filter(Appeals.IdTest.in_(test_ids))

        # Query per recuperare le informazioni sugli esami associati ai test
        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm)

        # Query per recuperare le valutazioni dello studente per i test
        student_valutations = session.query(Sustains).filter(
            Sustains.IdStudent == current_user.Id,
            Sustains.IdAppeal.in_([appeal.Id for appeal in myAppeal])
        ).all()

        # query per sus

        # recuperare i voti ottenuti dallo studente nei test dell'esame
        student_test_grades = {}
        for test in myTest:
            for valutation in student_valutations:
                if valutation.IdAppeal == test.AppealId:
                    student_test_grades[test.Id] = valutation.Valutation

        return render_template('teacherShowMyTests.html', myTest=myTest, myAppeal=myAppeal,
                               test=myTest, exam=testInfo,
                               myVal=student_valutations, student_test_grades=student_test_grades)
    else:
        return redirect('/')


