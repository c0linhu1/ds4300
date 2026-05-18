"""
J. Rachlin
Demonstration of working with Relational Database with python
"""

import os
from docpat_mysql import DoctorPatientAPI
from docpat_objects import Doctor, Patient

def main():

    # Authenticate
    api = DoctorPatientAPI(os.environ["DOCPAT_USER"], os.environ["DOCPAT_PASSWORD"], "doctorpatient")

    # Get oncologists accepting new patients
    docs = api.accepting_patients("oncology")
    for d in docs:
        print(d)

    # Register a new patient
    pat = Patient("Gates", "Billy", "M", "1955-10-28")
    api.register_patient(pat)


if __name__ == '__main__':
    main()