

class Patient:

    def __init__(self, first, last, sex, dob):
        self.first = first
        self.last = last
        self.sex = sex
        self.dob = dob

class Doctor:

    def __init__(self, first, last, new_patients, specialty, hospital):
        self.first = first
        self.last = last
        self.new_patients = new_patients
        self.specialty = specialty
        self.hospital = hospital

    def __str__(self):
        return f"Doctor: {self.first} {self.last} ({self.specialty})"

