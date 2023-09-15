
-- Trigger blocca appelli vecchi

CREATE OR REPLACE FUNCTION annullaAppelliVecchi() RETURNS trigger AS $$
  BEGIN
    UPDATE "Sustains"
    SET "isValid" = FALSE
    WHERE "Id" = ANY (SELECT s1."Id" FROM "Sustains" s1 join "ExamAppeals" a ON (s1."IdAppeal" = a."Id")
                  WHERE a."IdTest" = (SELECT a1."IdTest" FROM "ExamAppeals" a1 WHERE a1."Id" = NEW."IdAppeal"));
    RETURN new;
  END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS annullaAppelliVecchi ON "Sustains";
CREATE TRIGGER annullaAppelliVecchi
BEFORE INSERT ON "Sustains"
FOR EACH ROW
EXECUTE FUNCTION annullaAppelliVecchi();


--Trigger numero test

CREATE OR REPLACE FUNCTION controlloNumeroTest() RETURNS trigger AS $$
  BEGIN
    IF((SELECT "nTest" FROM "Exams" WHERE "Id" = NEW."IdExam")=(SELECT COUNT(*) FROM "Tests" t WHERE t."IdExam" = NEW."IdExam")) THEN return null;
    END IF;
    return NEW;
  END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS controlloNumeroTest ON "Tests";
CREATE TRIGGER controlloNumeroTest
BEFORE INSERT ON "Tests"
FOR EACH ROW
EXECUTE FUNCTION controlloNumeroTest();