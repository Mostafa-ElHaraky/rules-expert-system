"""
PyKnow/Experta Rules
Tasks:
- Implement at least 8 rules using various logical operators and conditional elements.
- Demonstrate field constraints, variable binding, and salience.
"""

from experta import *


class Student(Fact):
    """Student information."""
    name = Field(str, mandatory=True)
    gpa = Field(float, mandatory=True)
    credits_completed = Field(int, mandatory=True)


class Prerequisite(Fact):
    """Course prerequisite."""
    course = Field(str, mandatory=True)
    required_course = Field(str, mandatory=True)


class Enrollment(Fact):
    """Student enrollment request."""
    student = Field(str, mandatory=True)
    course = Field(str, mandatory=True)


class CompletedCourse(Fact):
    """Course already completed by student."""
    student = Field(str, mandatory=True)
    course = Field(str, mandatory=True)
    grade = Field(str, default='C')


class CourseCapacity(Fact):
    """Available seats in a course."""
    course = Field(str, mandatory=True)
    seats = Field(int, mandatory=True)


class SpecialPermission(Fact):
    """Special permission for a student to enroll."""
    student = Field(str, mandatory=True)
    course = Field(str, mandatory=True)


class CourseAdvisor(KnowledgeEngine):

    @Rule(Student(name='Alice'))
    def rule1_recognize_alice(self):
        print("Rule 1 fired: Recognized student Alice.")

    @Rule(AND(Student(name=MATCH.name, gpa=P(lambda x: x >= 3.5)),
              CompletedCourse(student=MATCH.name, course='CS101')))
    def rule2_high_gpa_and_cs101(self, name):
        print(f"Rule 2 fired: {name} has high GPA and completed CS101. Eligible for honors track.")

    @Rule(OR(Student(name=MATCH.name, gpa=P(lambda x: x >= 3.0)),
             CompletedCourse(student=MATCH.name, course='MATH101')))
    def rule3_gpa_or_math(self, name):
        print(f"Rule 3 fired: {name} meets GPA >=3.0 OR has completed MATH101. Eligible for intermediate courses.")

    @Rule(Enrollment(student=MATCH.name, course=MATCH.course),
          NOT(Prerequisite(course=MATCH.course, required_course=W())))
    def rule4_no_prereq(self, name, course):
        print(f"Rule 4 fired: Course {course} has no prerequisites. {name} can enroll directly.")


    @Rule(EXISTS(CourseCapacity(course='CS202', seats=P(lambda x: x > 0))))
    def rule5_cs202_has_seats(self):
        print("Rule 5 fired: CS202 has at least one seat available. Enrollment open.")


    @Rule(Student(name=MATCH.name, gpa=MATCH.gpa),
          Enrollment(student=MATCH.name, course=MATCH.course),
          CourseCapacity(course=MATCH.course, seats=MATCH.seats),
          TEST(lambda gpa, seats: gpa >= 2.5 and seats > 0))
    def rule6_eligible_if_seats_and_gpa(self, name, course):
        print(f"Rule 6 fired: {name} is eligible for {course} (GPA >=2.5 and seats >0).")


    @Rule(Enrollment(student=MATCH.name, course=MATCH.course),
          NOT(AND(Prerequisite(course=MATCH.course, required_course=MATCH.req),
                  NOT(CompletedCourse(student=MATCH.name, course=MATCH.req)))))
    def rule7_all_prereqs_met(self, name, course):
        print(f"Rule 7 fired: {name} has met all prerequisites for {course}.")


    @Rule(CompletedCourse(student=MATCH.name, course=W(), grade=P(lambda g: g in ['A', 'B'])))
    def rule8_good_grade_in_any_course(self, name):
        print(f"Rule 8 fired: {name} has at least one course with grade A or B.")


    @Rule(Enrollment(student=MATCH.name, course='CS500'),
          salience=10)
    def rule9_graduate_course_warning(self, name):
        print(f"Rule 9 (high salience) fired: {name} is attempting to enroll in graduate course CS500. Special approval required.")


    @Rule(AS.enrollment << Enrollment(student=MATCH.name, course=MATCH.course),
          CourseCapacity(course=MATCH.course, seats=0))
    def rule10_course_full(self, enrollment, name, course):
        print(f"Rule 10 fired: Course {course} is full. Cannot enroll {name}.")
        # Could retract the enrollment fact
        self.retract(enrollment)


    @Rule(Student(name=MATCH.name, credits_completed=P(lambda c: c >= 90)))
    def rule11_senior_status(self, name):
        print(f"Rule 11 fired: {name} has senior status (>=90 credits).")



if __name__ == "__main__":
    engine = CourseAdvisor()
    engine.reset()

    # Declare facts
    engine.declare(Student(name='Alice', gpa=3.8, credits_completed=95))
    engine.declare(Student(name='Bob', gpa=2.9, credits_completed=45))
    engine.declare(Student(name='Charlie', gpa=3.2, credits_completed=60))

    engine.declare(CompletedCourse(student='Alice', course='CS101', grade='A'))
    engine.declare(CompletedCourse(student='Alice', course='MATH101', grade='B'))
    engine.declare(CompletedCourse(student='Bob', course='CS101', grade='C'))
    engine.declare(CompletedCourse(student='Charlie', course='MATH101', grade='A'))

    engine.declare(Prerequisite(course='CS202', required_course='CS101'))
    engine.declare(Prerequisite(course='CS202', required_course='MATH101'))

    engine.declare(Enrollment(student='Alice', course='CS202'))
    engine.declare(Enrollment(student='Bob', course='CS202'))
    engine.declare(Enrollment(student='Charlie', course='CS101'))  # No prereq
    engine.declare(Enrollment(student='Alice', course='CS500'))    # Graduate course

    engine.declare(CourseCapacity(course='CS202', seats=1))
    engine.declare(CourseCapacity(course='CS101', seats=0))


    print("\n=== Running Expert System ===\n")
    engine.run()
    print("\n=== Execution Complete ===\n")
