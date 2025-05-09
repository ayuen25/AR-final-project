import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def data_conv(File_Name): 
    df = pd.DataFrame() # Create a DataFrame directly
    data = pd.read_csv(File_Name) # Read a CSV file directly
    #print(data.columns) #Print Column Names
    student_list = list(set(data['Anonymized ID'])) #Compile the list of Unique Students
    #print(student_list[:10], len(student_list)) #Print the first 10 and the # of total Students
    exclude_courses = ['Domestic Study Away', 'International Study Away', 'Doshisha University', 'New College Oxford', 
                       'Gottingen University', 'UIC Yonsei University', 'Universidad de los Andes']
    # Filter out the Study away courses and any course that contains 'Lab'
    course_list = [course for course in list(set(data['Course Title'])) if course not in exclude_courses ] #or 'lab' not in course.lower()
    #print(course_list)

    """
    Organize the data frame into a dictionary, Where a key is the students anonymized ID, and the dict returns a list of the Course titles the student is enrolled in
    """
    #INIT: Dictionary to Store Students and Course Titles 
    student_dict = {}
    #Iterate through the unique students 
    for student in student_list:
        # Filter rows for that student
        student_data = data[data['Anonymized ID'] == student]
        #print(student_data) #Test print
        # Create a dictionary or list of courses, terms, etc.
        courses = list(set(student_data['Course Title'].to_list()))  #Convert to a list
        #Filter out labs:
        #courses = [course for course in courses if 'lab' not in course.lower()]
        
        # Store it in the dictionary
        student_dict[student] = courses

    """
    Create an edge "list", create a new dictionary where key returns the list of possible edges.
    """
    #Dictionary to store the edges of each student (Reminder: Edges are students enrolled in both nodes(classes))
    student_edges = {}
    #Iterate through the dictionary of students
    for key in student_dict:
        #Get this students courses 
        student_courses = student_dict[key]
        
        #Create all of the possible edges: 
        edge_list = []
        #Iterate through the courses creating all the possible edge pairs
        for i in range(len(student_courses)-1):
            for j in range(i+1,len(student_courses)):
                edge_list.append((student_courses[i],student_courses[j]))
        student_edges[key] = edge_list
    #Test: Print the total number of edges created: 
    """
    totaledge = 0
    for key in student_edges:
        totaledge += len(student_edges[key])
    print("Total Number of Edges Created: ", totaledge)
    """

    return data, course_list, student_dict, student_edges

"""
Given the list of all the courses, and all the edges for each student, creates a 2D graph.
"""
def graph_conv(course_list, student_edges, show):
    #print(student_edges.keys())
    keys = list(student_edges.keys())
    G = nx.MultiGraph()
    G.add_nodes_from(course_list)
    #keys = keys[:2] #Test the first two
    #print(keys)
    for key in keys:
        #print("Student: ", key, "Edges: ",student_edges[key]) #Test Print
        curr_edges = student_edges[key]
        G.add_edges_from([(u, v, {'label': key}) for u, v in curr_edges])
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.3, iterations=50)
    if show:
        # Draw and display the graph
        nx.draw(G, pos, with_labels=True)
        plt.title(f"Graph Visualization\nNodes: {G.number_of_nodes()}  Edges: {G.number_of_edges()}")
        plt.show()
    return G

import plotly.graph_objects as go

"""
Given the list of all the courses, and all the edges for each student, creates a 3D graph.
"""

def graph_conv_3d(course_list, student_edges):
    keys = list(student_edges.keys())
    G = nx.MultiGraph()
    G.add_nodes_from(course_list)
    for key in keys:
        curr_edges = student_edges[key]
        G.add_edges_from([(u, v, {'label': key}) for u, v in curr_edges])
    
    # Compute a 3D spring layout
    pos = nx.spring_layout(G, dim=3, seed=42)
    
    # Extract node coordinates
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_z = [pos[node][2] for node in G.nodes()]
    
    # Prepare edge coordinates
    edge_x, edge_y, edge_z = [], [], []
    for u, v in G.edges():
        x0, y0, z0 = pos[u]
        x1, y1, z1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]



    
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(width=2, color='#888'),
        hoverinfo='none'
    )
    
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=5, color='blue'),
        text=list(G.nodes()),
        hoverinfo='text'
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title="3D Graph Visualization",
                        showlegend=False,
                        margin=dict(l=0, r=0, b=0, t=40),
                        scene=dict(
                            xaxis=dict(showbackground=False),
                            yaxis=dict(showbackground=False),
                            zaxis=dict(showbackground=False)
                        )
                    ))
    fig.show()
    return G


def create_clauses(course_list, student_dict, student_edges, graph, k):
    """
    For this, all we need to do is find the adjacencies for each of the nodes which can easily be done. From there you need to encode that no adjacent can be
    the same color, to encode this: 
    - Give each of the nodes a number  1 - n 
    - OKay so.... How to encode each one as a unique integer?
    Here is the schematic I think: 
    for each node: # of node (0-n-1) * # colors + color #
    to interpret: key-1 // (integer division) # of colors gives you the 


    Create the CNF clauses encoding the following constraints: 
    - Each node must be at least one color (A color is a proposed exam slot)
    - Each Noode Can only be at most one color
    - Each node cannot be the same color as its neighbors.
    """

    clauses = []
    translate_dict = {}
    reverse_translate = {}
    counter = 0
    #For each node in the graph
    for node in graph: 
        #Set the reverse
        reverse_translate[counter] = node
        #Set the counter as the key, correspond to a node
        translate_dict[node] = counter
        counter += 1


    """
    Each Node must be at least one color:
    to translate a node, grab its value from the dict, multiply by k to get its "translation" then add [0,k) to get a unique color 
    Each node must be at least one color: (0 V 1 V 2... k)
    """
    for node in graph: 
        translation = translate_dict[node] * k 
        least_once = []
        #range [1...k] 
        for i in range(1,k+1):
            least_once.append(translation + i)
        clauses.append(least_once)
    

    #***********************************************************

    """
    Each Node can only be AT MOST one color: 
    i.e if there were 3 nodes and 3 colors: 0,1,2 to express all 3 colors possible for node 1/0 however you look at it 
    expressed by: (-1 V -2), (-1 V -3), (-2 V -3)
    """
    for node in graph:
        translation = translate_dict[node] * k
        for i in range(1,k):
            for j in range(i+1, k+1):
                most_once = [-(translation + i),-(translation + j)]
                clauses.append(most_once)
    #***********************************************************************************



    """
    Each Node Cannot be the Same color as its neighbor: i.e if 1 and 2 are neighbors (3colors):
    (-0 V -3), (-1 V -4), (-2 V -5)
    """

    for node in graph: 
        node_trans = translate_dict[node]
        neighbors = graph.neighbors(node)
        for adjnode in neighbors:
            neighbor_trans = translate_dict[adjnode]
            for i in range(1,k+1):
                diff_neighbors = [-((node_trans*k) + i), -((neighbor_trans*k) + i)]
                clauses.append(diff_neighbors) 
     
     #**********************************************************************************

    return clauses, reverse_translate


def to_DIMACS(clauses, graph, filename):
    """
    Write the list of clauses to a DIMACS file.
    """
    num_vars = len(graph)  # Number of variables (nodes)
    num_clauses = len(clauses)  # Number of CNF clauses

    with open(filename, "w") as f:
        # Write the problem line
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        
        # Write each clause, ensuring correct formatting
        for clause in clauses:
            for literal in clause:
                f.write(str(literal) + " ")
            f.write("0\n")
    
    print(f"DIMACS file '{filename}' created successfully.")



def SAT_solve(course_list, student_dict, student_edges, graph, k):
    clauses, reverse_translate = create_clauses(course_list, student_dict, student_edges, graph, k)
    to_DIMACS(clauses, graph, 'final_exam.cnf')

    student_times = solve_final_exam_dimacs("final_exam.cnf", k)
    print(student_times)
    exam_schedule = []
    for lit in student_times:
        if lit > 0:
            exam_schedule.append(lit)
    schedule = {}
    #To Convert back to node 
    for exam in exam_schedule:
        #Subtract 1 to reset indexes
        x = exam - 1
        #Integer Division 
        x = x//k
        #print(exam, x)
        #Use dictionary to find correct course
        course = reverse_translate[x]
        #Append to the schedule
        schedule[course] = exam - (x * k)
        
    print(schedule)
    return schedule



def SMT_solve(graph, data, filename, course_list, k):
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
    LIA_model = solve_SMT_LIA(course_list, conflicts, k, room_list, room_capacities , enrollments)
    return LIA_model, room_list, room_capacities, enrollments





def SMT_conflict_solve(graph, data, filename, course_list, k):
    conflicts = graph.edges
    # Compute a series mapping course title -> count
    counts = data['Course Title'].value_counts()
    #print(counts)
    rooms = pd.read_csv(filename)
    room_capacities = {}
    room_list = []
    for idx, row in rooms.iterrows():
        room_name    =  row['Building'] + ' ' + str(row['Room'])       # the room identifier
        room_list.append(room_name)
        room_capacity = row['EMS']  # whatever the column holding capacity is
        room_capacities[room_name] = room_capacity
    # Convert to a plain dict
    enrollments = counts.to_dict()
    #print(enrollments)
    #print(room_capacities)

    smt_model = conflict_solve(course_list, conflicts, k, room_list, room_capacities , enrollments)
    print(smt_model)

from solve_final import solve_final_exam_dimacs
from smt_solve import *
from Assignment_Check import *
def main():
    #Registration File: Specify the file name of the registration data
    registration_file = "test-subset.csv"
    #Convert the csv file to dictionairies of student:class and student:edges as well as return a course_list and the data frame "data"
    data, course_list, student_dict, student_edges = data_conv(registration_file)

    print("# of Students: ", len(student_dict))

    graph = graph_conv(course_list, student_edges,True)

    #K = Number of Slots: change for more slots
    k = 5

    #print("Number of nodes: ",graph.number_of_nodes(), " Number of Edges: ", graph.number_of_edges()) #Test print to see the number of nodes and edges

    #Schedule Final Exams Using SAT Solver.
    print("Sat Solve: \n")
    schedule = SAT_solve(course_list,student_dict,student_edges,graph, k)
    #Manual Check of the SAT solver
    check_Sat(graph, schedule)


    #room_file: Specify the file name of the room data
    room_file = "Room_Test.csv"
    #SMT Solver:
    print("SMT Solve \n")
    SMT_schedule, room_list, room_capacity, enrollments = SMT_solve(graph, data, room_file, course_list,k)
    #Check the SMT solver
    check_SMT(graph,SMT_schedule,room_list,room_capacity, enrollments)

    #SMT With Conflicts:
    print("Optimize Solve: \n")
    SMT_conflict_solve(graph,data,room_file, course_list,k=4)



if __name__ == "__main__":
    main()
