import pandas as pd
import sys
import random
import time
from final_exam import *
from solve_final import *

def generate_subset_csv(input_file, num_students):
    # Load the full dataset
    df = pd.read_csv(input_file)

    # Get the unique anonymized student IDs
    unique_ids = df['Anonymized ID'].unique()


    # Randomly select the desired number of unique student IDs
    selected_ids = random.sample(list(unique_ids), num_students)

    # Filter the DataFrame to include only those student entries
    filtered_df = df[df['Anonymized ID'].isin(selected_ids)]

    # Save the filtered DataFrame to a new CSV
    output_file = f"test_{num_students}_students.csv"
    filtered_df.to_csv(output_file, index=False)
    print(f"Created: {output_file}")

def main():

    """
    "Enrollments gives a mapping of course title -> number of students enrolled"
    enrollments = counts.to_dict()
    SMT_start = time.time()
    LIA_model = solve_SMT_LIA(course_list, conflicts, 20, room_list, room_capacities , enrollments)
    satisfiable = LIA_model != None
    SMT_end = time.time()
    SMT_net = SMT_end - SMT_start
    print(f"SMT Solve Time: {SMT_net:.4f}s, Satisfiable: {satisfiable}")
    """



    """
    I will try to record the results of the Solvers for instances of 10, 25, 50, 100, 250, 500, 1000, 2392
    at each one of these instances, I will record the time it takes to solve the problem, and will try for k values of 5, 10, 15, 20, 40
    """
    input_file = "Course_Reg.csv"
    
    for num_students in [10, 25, 50, 100, 250, 500, 1000, 2392]:
        # Generate a subset CSV for the current number of students
        generate_subset_csv(input_file, num_students)
        for k in [5, 10, 20]:
            convert_start = time.time()
            data, course_list, student_dict, student_edges = data_conv(f'test_{num_students}_students.csv')
            convert_end = time.time()
            convert_net = convert_end - convert_start
            graph = graph_conv(course_list, student_edges, False)
            #create_clauses_start = time.time()
            #clauses, reverse_translate = create_clauses(course_list, student_dict, student_edges, graph, k)
            #create_clauses_end = time.time()
            #create_clauses_net = create_clauses_end - create_clauses_start
            #to_DIMACS(clauses, graph, "benchmarks.cnf")
            #solve_start = time.time()
            # Run SAT solver and record if it found a solution
            #student_times = solve_final_exam_dimacs("benchmarks.cnf", k)
            #sat = student_times != None
            #solve_end = time.time()
            #solve_net = solve_end - solve_start
            '''
            with open("timing_results.txt", "a") as f:
                f.write(
                    f"Students: {num_students}, k: {k}, "
                    f"Convert Time: {convert_net:.4f}s, Clause Time: {create_clauses_net:.4f}s, "
                    f"SAT Solve Time: {solve_net:.4f}s, SAT Satisfiable: {sat}\n"
                )
            '''

            """
            SMT Solver :
            """

            #Since we want no conflicts at all, only need a set of the conflicts.
            conflicts = list(set(graph.edges))
            # Compute a series mapping course title -> count
            counts = data['Course Title'].value_counts()
            #print(counts)
            rooms = pd.read_csv("Exam-Rooms.csv")
            room_capacities = {}
            room_list = []
            for idx, row in rooms.iterrows():
                room_name    =  row['Building'] + ' ' + str(row['Room'])       # the room identifier
                room_list.append(room_name)
                room_capacity = row['EMS']  # whatever the column holding capacity is called
                room_capacities[room_name] = room_capacity
            # Convert to a plain dict

            "Enrollments gives a mapping of course title -> number of students enrolled"
            enrollments = counts.to_dict()
            SMT_start = time.time()
            LIA_model = solve_SMT_LIA(course_list, conflicts, k, room_list, room_capacities , enrollments)
            satisfiable = LIA_model != None
            SMT_end = time.time()
            SMT_net = SMT_end - SMT_start

            with open("timing_results.txt", "a") as f:
                f.write(
                    f"SMT Solve - Students: {num_students}, k: {k}, "
                    f"SMT Solve Time: {SMT_net:.4f}s, SMT Satisfiable: {satisfiable}\n"
                )

if __name__ == "__main__":
    main()