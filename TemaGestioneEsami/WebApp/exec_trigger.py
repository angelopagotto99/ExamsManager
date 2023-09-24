
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('postgresql+pg8000://postgres:', echo=True)

def create_trigger():
    engine.execute(text(open("Trigger.sql").read()))

create_trigger()