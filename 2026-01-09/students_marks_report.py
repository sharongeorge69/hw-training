name = "George"
age = 23
marks = [78.5, 65.0, 82.5,30]
subjects = ("Maths","English","Physics")

student = {
    "Name": name,
    "Age" : age,
    "Marks": marks,
    "Subjects":subjects
}

print("Data Type of each Value :")

for key,value in student.items():
    print(f"{key}: {type(value)}")

#Calculate Total marks and print individual marks

total_marks = 0
for mark in marks:
    print(mark)
    total_marks+=mark

print(f"Total Marks = {total_marks}")

#Calculate Average Marks:

average_marks = total_marks//len(marks)
print(f"Average_Marks = {average_marks}")


# Convert marks list to set
marks_set = set(marks)
print(marks_set)

is_passed = True
print(type(is_passed))

# Check pass or fail
if average_marks >= 40:
    is_passed = True
else:
    is_passed = False

#add a variable remarks=None and print its type
remarks = None
print(type(remarks))


#Formated Student report

print(f"Name           : {name}")
print(f"Age            : {age}")
print(f"Subjects       : {subjects}")
print(f"Marks          : {marks}")
print(f"Total Marks    : {total_marks}")
print(f"Average Marks  : {average_marks:.2f}")
print(f"Marks Set      : {marks_set}")
print(f"Result         : {'PASS' if is_passed else 'FAIL'}")