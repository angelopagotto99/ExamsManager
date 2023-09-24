
-- Trigger blocca appelli vecchi


CREATE OR REPLACE FUNCTION annullaAppelliVecchi() RETURNS trigger AS $$
  BEGIN
    UPDATE "Sustains"
    SET "isValid" = FALSE
    WHERE "Id" = ANY (SELECT s1."Id" FROM "Sustains" s1 join "ExamAppeals" a ON (s1."IdAppeal" = a."Id")
                  WHERE a."IdTest" = (SELECT a1."IdTest" FROM "ExamAppeals" a1 WHERE a1."Id" = NEW."IdAppeal")) AND "IdStudent" = NEW."IdStudent";
    RETURN new;
  END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS annullaAppelliVecchi ON "Sustains";
CREATE TRIGGER annullaAppelliVecchi
BEFORE INSERT ON "Sustains"
FOR EACH ROW
EXECUTE FUNCTION annullaAppelliVecchi();



--Trigger numero testl

CREATE OR REPLACE FUNCTION controlloNumeroTest() RETURNS trigger AS $$
  BEGIN
    IF((SELECT "nTest" FROM "Exams" WHERE "Id" = NEW."IdExam")=(SELECT COUNT(*) FROM "Tests" t WHERE t."IdExam" = NEW."IdExam")) THEN
        RAISE data_exception USING MESSAGE = 'già raggiunto il numero di test';
        return null;
    END IF;
    return NEW;
  END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS controlloNumeroTest ON "Tests";
CREATE TRIGGER controlloNumeroTest
BEFORE INSERT ON "Tests"
FOR EACH ROW
EXECUTE FUNCTION controlloNumeroTest();



--- trigger per il controllo della validità degli esami

CREATE OR REPLACE FUNCTION controlloValiditàAppello() RETURNS trigger AS $$
  BEGIN
    --UPDATE CONTROLLO SULLA VALIDITÀ DELLE DATE
    UPDATE public."Sustains"
    SET "isValid" = FALSE
    WHERE "Id" = ANY (SELECT s."Id" FROM public."Sustains" s JOIN public."ExamAppeals" ea ON (s."IdAppeal" = ea."Id")
				 WHERE ea."ValutationExpireData" < CURRENT_DATE::text);
    --CONTROLLO DI AVERE ABBASTANZA ESAMI VALIDI
    IF(SELECT count(*) FROM public."Tests" ts LEFT JOIN (public."ExamAppeals" ea JOIN public."Sustains" s ON (ea."Id" = s."IdAppeal")) ON (ts."Id" = ea."IdTest") WHERE ts."IdExam" = NEW."IdExam" AND s."IdStudent" = NEW."IdStudent" AND s."isValid" = TRUE) =
      (SELECT "nTest" FROM public."Exams" WHERE "Id" = NEW."IdExam" ) THEN RETURN NEW;
    END IF;
    RETURN OLD;
  END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS controlloValiditàAppello ON "IsEnrolled";
CREATE TRIGGER controlloValiditàAppello
BEFORE UPDATE ON "IsEnrolled"
FOR EACH ROW
EXECUTE FUNCTION controlloValiditàAppello();



--- trigger per il controllo della validità degli esami

CREATE OR REPLACE FUNCTION bloccoEsameBonus() RETURNS trigger AS $$
  BEGIN
   IF((SELECT count(*) FROM public."Tests" WHERE "IdExam" = NEW."IdExam") = (SELECT "nTest" FROM public."Exams" WHERE "Id" = NEW."IdExam") - 1)
       AND
     (NEW."ValType" = 'Bonus')THEN
       RAISE data_exception USING MESSAGE = 'esame di soli bonus';
       RETURN NULL;
   end if;
   RETURN NEW;
  END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS bloccoEsameBonus ON "Tests";
CREATE TRIGGER bloccoEsameBonus
BEFORE INSERT ON "Tests"
FOR EACH ROW
EXECUTE FUNCTION bloccoEsameBonus();




