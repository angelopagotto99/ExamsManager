from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('postgresql+pg8000://postgres:Angelo99@localhost:5432/Exams_Manager', echo=True)

Base = declarative_base()

class Teachers(Base):
    __tablename__ = 'Teachers'

    #dichiarazione dei campi della tabella

    IdTeacher = Column(Integer, primary_key=True)
    Email = Column(String(30), nullable=False, unique=True)
    Password = Column(String(30), nullable=False)
    Nome = Column(String(30), nullable=False)
    Cognome = Column(String(30), nullable=False)
    Telefono = Column(String(30), nullable=False)
    #relazione con esami 1 a n
    Exams = relationship('Exams', back_populates='Teacher')
    #relazione con prove 1 a 1
    Test = relationship('Tests', uselist=False, back_populates='Responsabile')

class Students(Base):
    __tablename__ = 'Students'

    #dichiarazione dei campi della tabella

    IdStudent = Column(Integer, primary_key=True)
    Email = Column(String(30), nullable=False, unique=True)
    Password = Column(String(30), nullable=False)
    Nome = Column(String(30), nullable=False)
    Cognome = Column(String(30), nullable=False)
    Telefono = Column(Integer, nullable=False)
    IdExam = Column(Integer, nullable=False)
    #relazione con prove n a m
    Tests = relationship('Tests', secondary='Sustains')
    #relazione con esami n a m
    Exams = relationship('Exams', secondary='IsEnrolled')

class IsEnrolled(Base):
    __tablename__ = 'IsEnrolled'

    #dichiarazione dei campi della tabella

    IdStudent = Column(Integer, ForeignKey('Students.IdStudent'), primary_key=True)
    IdExam = Column(Integer, ForeignKey('Exams.IdExam'), primary_key=True)
    DataRegistrazioneVoto = Column(DateTime)
    DataScadenzaVoto = Column(DateTime)
    # relazione con esami n a m
    Exam = relationship('Exams', back_populates='Students')
    # relazione con studenti n a m
    Student = relationship('Students', back_populates='Exams')

class Exams(Base):
    __tablename__ = 'Exams'

    #dichiarazione dei campi della tabella

    IdExam = Column(Integer, primary_key=True)
    NomeExam = Column(String(30), nullable=False)
    Descrizione = Column(String(100))
    nProve = Column(Integer, nullable=False)
    IdTeacher = Column(Integer, ForeignKey('Teachers.IdTeacher'))

    Teacher = relationship('Teachers', back_populates='Exams')
    Tests = relationship('Tests', back_populates='Exam')
    Students = relationship('Students', secondary='IsEnrolled')

class Tests(Base):
    __tablename__ = 'Tests'

    #dichiarazione dei campi della tabella

    IdTest = Column(Integer, primary_key=True)
    NomeTest = Column(String(30), nullable=False)
    Tipologia = Column(String(30), nullable=False)
    TipoValutazione = Column(Enum('Esame', 'Idoneità', 'Bonus'), nullable=False)
    IdResponsabile = Column(Integer, ForeignKey('Teachers.IdTeacher'))
    IdExam = Column(Integer, ForeignKey('Exams.IdExam'))

    #relazione con docenti 1 a 1
    Responsabile = relationship('Teachers', back_populates='Test')
    #relazione con esami 1 a n
    Exam = relationship('Exams', back_populates='Tests')
    #relazione con studenti n a m
    Students = relationship('Students', secondary='Sustains')

class ExamAppeals(Base):
    __tablename__ = 'ExamAppeals'

    #dichiarazione dei campi della tabella

    IdAppeal = Column(Integer, primary_key=True)
    DataEsame = Column(DateTime, nullable=False)
    IdTest = Column(Integer, ForeignKey('Tests.IdTest'))
    #relazione con test 1 a n
    Test = relationship('Tests', back_populates='Appeals')

class Sustains(Base):
    __tablename__ = 'Sustains'

    #dichiarazione dei campi della tabella

    IdStudent = Column(Integer, ForeignKey('Students.IdStudent'), primary_key=True)
    IdAppeal = Column(Integer, ForeignKey('ExamAppeals.IdAppeal'), primary_key=True)
    Valutazione = Column(Float, nullable=False)
    Idoneo = Column(Boolean, nullable=False, default=False)
    isBonus = Column(Boolean, nullable=False, default=False)

    #relazione con studenti n a m
    Student = relationship('Students', back_populates='Tests')
    #relazione con appelli n a m
    Appeal = relationship('ExamAppeals', back_populates='Sustains')


Base.metadata.create_all(engine)