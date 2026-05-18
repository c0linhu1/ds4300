"""
Doctor-Patient Database API for MySQL
"""

from dbutils import DBUtils
from docpat_objects import Doctor, Patient

class DoctorPatientAPI:

    def __init__(self, user, password, database, host="localhost"):
        self.dbu = DBUtils(user, password, database, host)

    def register_patient(self, pat):
        sql = "INSERT INTO patient (lastname, firstname, sex, dob) VALUES (%s, %s, %s, %s) "
        val = (pat.last, pat.first, pat.sex, pat.dob)
        self.dbu.insert_one(sql, val)

    def accepting_patients(self, specialty):
        sql = """
                select doctor_id, lastname, firstname, new_patients, specialty, h.name hospital
                from doctor d join specialty using (specialty_id) 
                join hospital h using (hospital_id)
                where new_patients = 1
                and specialty like '""" + specialty + "'"
        df = self.dbu.execute(sql)
        docs = [Doctor(*df.iloc[i][1:]) for i in range(len(df))]
        return docs


