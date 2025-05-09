from z3 import *


def solve_SMT_LIA(course_list, course_conflicts, k, classroom_list, classroom_capacity, enrollments):
    """
    Overview: 
    - Creates the solver, 
    - Creates a dictionary where each course corresponds to an SMT Int variable corresponding to a slot constrained between 1 and the # of slots.
    - Creates a dictionary where each course corresponds to an SMT Int variable corresponding to a room constrained between 1 and the # of classrooms
    - Adds the constraints:
        - Classroom capacity, Must be greater than or equal to enrollment size
        - two courses cannot be in the same room at the same time
        - Eliminate course conflicts
    """
    # Define your courses and available time slots


    # Create the Z3 solver instance
    solver = Solver()

    #Create an SMT variable for each course's exam time, restricting it to domain 1..k
    #Create a dictionary in which course name corresponds to an Int SMT variable.
    exam_time = {course: Int(course) for course in course_list}

    #begin to add constraints such that each course must be assigned to a "slot" between 1 annd k
    for course in course_list:
        solver.add(And(exam_time[course] >= 1, exam_time[course] <= k))

    # Create an SMT variable for each course's exam room, restricting to domain 1..number of classrooms
    exam_room = {course: Int(f"{course}_room") for course in course_list}
    for course in course_list:
        solver.add(And(exam_room[course] >= 1, exam_room[course] <= len(classroom_list)))

    # Add classroom capacity constraints: ensure each assigned room can hold the course's enrollment
    for course in course_list:
        for i, room in enumerate(classroom_list, start=1):
            #EX: Course 1 in Classroom 1 -> classroom_capacity[room] >= enrollments[course]
            solver.add(Implies(exam_room[course] == i, classroom_capacity[room] >= enrollments[course]))


    # Prevent two courses from being scheduled in the same room at the same time
    for i, c1 in enumerate(course_list):
        #C1Time != C2Time or C1Room != C2Room
        for c2 in course_list[i+1:]:
            solver.add(Or(exam_time[c1] != exam_time[c2], exam_room[c1] != exam_room[c2]))


    # Define conflict pairs - these pairs cannot share the same exam time.
    # This could be computed from student enrollment data.

    # Add the conflict constraints to the solver
    for c1, c2, key in course_conflicts:
        solver.add(exam_time[c1] != exam_time[c2])

    # Check if the constraints are satisfiable and, if so, print a schedule.
    if solver.check() == sat:
        model = solver.model()
        print("Final Exam Schedule:")
        schedule = {}
        for course in course_list:
            assigned_slot = model[exam_time[course]].as_long()
            #print(f"Course {course}: Exam Slot {assigned_slot}")
            assigned_room = model[exam_room[course]].as_long()
            assigned_room_translation = classroom_list[assigned_room-1]
            #print(f"Room: {classroom_list[assigned_room-1]}")
            schedule[course] = [assigned_slot, assigned_room_translation]
        return schedule

    else:
        print("No valid exam schedule found.")


def conflict_solve(course_list, course_conflicts, k, classroom_list, classroom_capacity, enrollments):
    """
    Use Z3's Library to solve the problem as optimally as possible.
    """
    # Create the Z3 solver instance
    solver = Optimize()

    #Create an SMT variable for each course's exam time, restricting it to domain 1..k
    #Create a dictionary in which course name corresponds to an Int SMT variable.
    exam_time = {course: Int(course) for course in course_list}

    #begin to add constraints such that each course must be assigned to a "slot" between 1 annd k
    for course in course_list:
        solver.add(And(exam_time[course] >= 1, exam_time[course] <= k))

    # Create an SMT variable for each course's exam room, restricting to domain 1..number of classrooms
    exam_room = {course: Int(f"{course}_room") for course in course_list}
    for course in course_list:
        solver.add(And(exam_room[course] >= 1, exam_room[course] <= len(classroom_list)))

    # Add classroom capacity constraints: ensure each assigned room can hold the course's enrollment
    for course in course_list:
        for i, room in enumerate(classroom_list, start=1):
            #EX: Course 1 in Classroom 1 -> classroom_capacity[room] >= enrollments[course]
            solver.add(Implies(exam_room[course] == i, classroom_capacity[room] >= enrollments[course]))


    # Prevent two courses from being scheduled in the same room at the same time
    for i, c1 in enumerate(course_list):
        #C1Time != C2Time or C1Room != C2Room
        for c2 in course_list[i+1:]:
            solver.add(Or(exam_time[c1] != exam_time[c2], exam_room[c1] != exam_room[c2]))


    # Define conflict pairs - these pairs cannot share the same exam time.
    # This could be computed from student enrollment data.


    
    # build a list of 0/1 penalties: 1 if two conflicting courses _share_ a slot
    penalties = [
        If(exam_time[c1] == exam_time[c2], 1, 0)
        for c1, c2, _ in course_conflicts
    ]

    # Optimize and retrieve model
    solver.minimize(cost := Int('conflict_cost'))
    solver.add(cost == Sum(penalties))
    if solver.check() == sat:
        m = solver.model()
        print("Conflicts remaining:", m[cost])
        print("Final Exam Schedule (with minimized conflicts):")
        for course in course_list:
            assigned_slot = m[exam_time[course]].as_long()
            print(f"Course {course}: Exam Slot {assigned_slot}")
            assigned_room = m[exam_room[course]].as_long()
            print(f"Room: {classroom_list[assigned_room-1]}")
    else:
        print("No valid assignment found")
        return
    

    #Encode in QF_LRA, Can compare to QF_LIA
    #Show on a subset, graphical representation might be helpful -
    #


def solve_SMT_lra(course_list, course_conflicts, k, classroom_list, classroom_capacity, enrollments):
    """
    Overview: 
    - Creates the solver, 
    - Creates a dictionary where each course corresponds to an SMT Int variable corresponding to a slot constrained between 1 and the # of slots.
    - Creates a dictionary where each course corresponds to an SMT Int variable corresponding to a room constrained between 1 and the # of classrooms
    - Adds the constraints:
        - Classroom capacity, Must be greater than or equal to enrollment size
        - two courses cannot be in the same room at the same time
        - Eliminate course conflicts
    """
    # Define your courses and available time slots


    # Create the Z3 solver instance
    solver = Solver()

    #Create an SMT variable for each course's exam time, restricting it to domain 1..k
    #Create a dictionary in which course name corresponds to an Int SMT variable.
    exam_time = {course: Real(course) for course in course_list}

    for c in course_list:
        solver.add(
            Or(*[ exam_time[c] == i
                for i in range(1, k+1) ])
        )


    #begin to add constraints such that each course must be assigned to a "slot" between 1 annd k
    """
    for course in course_list:
        solver.add(And(exam_time[course] >= 1, exam_time[course] <= k))
    """
    # Create an SMT variable for each course's exam room, restricting to domain 1..number of classrooms
    
    exam_room = {course: Real(f"{course}_room") for course in course_list}

    """
    for course in course_list:
        solver.add(And(exam_room[course] >= 1, exam_room[course] <= len(classroom_list)))
    """
     # and likewise for rooms:
    for c in course_list:
        solver.add(
            Or(*[ exam_room[c] == i
                for i in range(1, len(classroom_list)+1) ])
        )

    # Add classroom capacity constraints: ensure each assigned room can hold the course's enrollment
    for course in course_list:
        for i, room in enumerate(classroom_list, start=1):
            #EX: Course 1 in Classroom 1 -> classroom_capacity[room] >= enrollments[course]
            solver.add(Implies(exam_room[course] == i, classroom_capacity[room] >= enrollments[course]))


    # Prevent two courses from being scheduled in the same room at the same time
    for i, c1 in enumerate(course_list):
        #C1Time != C2Time or C1Room != C2Room
        for c2 in course_list[i+1:]:
            solver.add(Or(exam_time[c1] != exam_time[c2], exam_room[c1] != exam_room[c2]))


    # Define conflict pairs - these pairs cannot share the same exam time.
    # This could be computed from student enrollment data.

    # Add the conflict constraints to the solver
    for c1, c2, key in course_conflicts:
        solver.add(exam_time[c1] != exam_time[c2])

    # Check if the constraints are satisfiable and, if so, print a schedule.
    if solver.check() == sat:
        model = solver.model()
        print("Final Exam Schedule:")
        for course in course_list:
            assigned_slot = model[exam_time[course]]
            num = assigned_slot.numerator_as_long()
            denom = assigned_slot.denominator_as_long()
            print(f"Course {course}: Exam Slot {num}/{denom}")
            assigned_room = model[exam_room[course]]
            num = assigned_room.numerator_as_long()
            denom = assigned_room.denominator_as_long()
            print(f"Room: {num}/{denom}")
            #print(f"Room: {classroom_list[assigned_room-1]}")
    else:
        print("No valid exam schedule found.")