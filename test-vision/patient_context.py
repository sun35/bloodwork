class Patient():
    def __init__(self, height, weight, age, ethnicity, diet, exercise):
        self.height = height
        self.weight = weight
        self.age = age
        self.ethnicity = ethnicity
        self.diet = diet
        self.exercise = exercise

    def patient_to_dict(self):
        patient_dict = {
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "ethnicity": self.ethnicity,
            "diet": self.diet,
            "exercise": self.exercise
        }
        return patient_dict

class Patients():
    def __init__(self):
        self.num_patient = 0
        self.patients = {}

    def add_patient(self, patient):
        self.patients[self.num_patient] = patient.patient_to_dict()
        self.num_patient += 1

patients = Patients()
patient_zero = Patient("5'8", "135", "24", "Asian", "Gluten-Free", "0-2 times per week")
patients.add_patient(patient_zero)

def prompt_for_patient(patient):
    prompt = "Given that I am " + patient.age + " years old, " + patient.height + " and " + patient.weight + " pounds, " + " of " + patient.ethnicity + " ethnicity, and that my diet is " + patient.diet + " and my exercise frequency is " + patient.exercise + " times per week, "
    return prompt

    

