import matplotlib.pyplot as plt
import networkx as nx


def check_Sat(graph, schedule):
    """
    This function checks the validity of the assignment provided by the SAT solver implementation of the Final Exam Scheduler
    Displays a graphical representation of the assignment by coloring the courses corresponding to each color
    Manually checks validity by iterating through and ensuring that neighbors are not the same color
    """
    #iterate through the graph and compare neighbors: 
    for node in graph.nodes():
        for neighbor in graph.neighbors(node):
            if schedule[node] == schedule[neighbor]:
                print(f"Invalid assignment: {node} and {neighbor} have the same color.")
                return False
    
    visualize_schedule(graph, schedule)
    
    #Color the graph:

def visualize_schedule(graph, schedule):
    """
    Visualize the graph with nodes colored according to their assigned slot.
    graph: a NetworkX graph
    schedule: dict mapping node -> slot
    """
    # Determine unique slots
    
    unique_slots = sorted(set(schedule.values()))
    # Create a color map using matplotlib colormap
    cmap = plt.get_cmap('tab20')
    color_mapping = {slot: cmap(i % cmap.N) for i, slot in enumerate(unique_slots)}
    # Assign colors to nodes
    node_colors = [color_mapping[schedule[node]] for node in graph.nodes()]
    # Compute layout
    pos = nx.spring_layout(graph)
    # Draw nodes and edges
    nx.draw(graph, pos, with_labels=True, node_color=node_colors, edge_color='gray')
    # Create legend mapping slots to colors
    from matplotlib.patches import Patch
    legend_handles = [Patch(color=color_mapping[slot], label=f"Slot {slot}") for slot in unique_slots]
    plt.legend(handles=legend_handles)
    plt.title("Exam Schedule Coloring by Slot")
    plt.show()

def visualize_schedule_by_room(graph, schedule):
    """
    Visualize the graph with nodes colored according to their assigned room.
    graph: a NetworkX graph
    schedule: dict mapping node -> [slot, room]
    """
    unique_rooms = sorted(set([room for slot, room in schedule.values()]))
    cmap = plt.get_cmap('tab20')
    color_mapping = {room: cmap(i % cmap.N) for i, room in enumerate(unique_rooms)}
    node_colors = [color_mapping[schedule[node][1]] for node in graph.nodes()]
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color=node_colors, edge_color='gray')
    from matplotlib.patches import Patch
    legend_handles = [Patch(color=color_mapping[room], label=f"{room}") for room in unique_rooms]
    plt.legend(handles=legend_handles)
    plt.title("Exam Schedule Coloring by Room")
    plt.show()

def check_SMT(graph, schedule, room_list, room_capacity, course_enrollment):
    """
    Takes in the conflict graph, schedule(a dictionary mapping course -> [Slot, Room]), room_list(A dict associating the # of the room with the room name), Course_enrollment(A dict associating the course with the enrollment size)
    and room_capacity(A dict associating the room with the capacity) (I have no clue why i did it in such a roundabout way)
    This function checks the validity of the assignment provided by the SMT solver implementation of the Final Exam Scheduler
    Displays a graphical representation of the assignment by coloring the courses corresponding
    """
    # Iterate through the graph and compare neighbors:
    for node in graph.nodes():
        for neighbor in graph.neighbors(node):
            if schedule[node] == schedule[neighbor]:
                print(f"Invalid assignment: {node} and {neighbor} have the same color.")
                return False
            
    """
    Here's me making sense of it all: 
    Schedule = Dictionary where {Course -> [Slot,Room NAME]}
    Room_list = Dictionary where {Room # -> Room Name}
    Room_capacity = Dictionary where {Room Name -> Room Capacity}
    Course_enrollment = Dictionary where {Course Name -> Enrollment Size}
    Assigned_Rooms = List of [Slot, Room]
    Course_list = List of Courses, indexed the same as Assigned_Rooms
    """
    
            
    #Confirm Room Assignments are correct: Need to check all concurrent slots aren't in the same room 
    #Currently, schedule is a dict mapping a course -> [Slot, Room] 
    #Essentially just flatten it to [Slot, Room]
    Assigned_Rooms = list(schedule.values())
    Course_list = list(schedule.keys())
    # Check if the current Course and next course are enrolled in the same slot
    # THe following code essentially iterates through the Assignments [1,# Of Courses] and compares it to the next assignment, to see if they are in the same slot
    # Working example would be: 3 classes: Compare [1,2], [1,3], and [2,3]
    for i in range(len(Assigned_Rooms)-1):
        # Assigned[rooms...] gives the room #, roomlist[room #] gives the room name, room_capacity[room name] gives the room capacity, compare to the Course capacity -- Course_list[i] gives the course name, course_enrollment[Course_list[i]] gives the course enrollment #
        print(Assigned_Rooms[i][1])
        if room_capacity[Assigned_Rooms[i][1]] < course_enrollment[Course_list[i]]:
                print(f"Invalid assignment: {Course_list[i]} exceeds room capacity.")
                return False
        for j in range(i+1, len(Assigned_Rooms)):
            # If in the same slot,
            if Assigned_Rooms[i][0] == Assigned_Rooms[j][0]:
                # Check if they are in the same room: 
                if Assigned_Rooms[i][1] == Assigned_Rooms[j][1]:
                    # If they are in the same room, return false
                    # Print a warning 
                    print(f"Invalid assignment: {Course_list[i]} and {Course_list[j]} are in the same room.")
                    return False
    #Check that the last course doesn't exceed the room capacity
    if room_capacity[Assigned_Rooms[j][1]] < course_enrollment[Course_list[i]]:
        print(f"Invalid assignment: {Course_list[len(Assigned_Rooms)-1]} exceeds room capacity.")
        return False
    

    print("Valid assignment: No Room Conflicts found.")

    vis_schedule = {}
    for key in schedule.keys():
        vis_schedule[key] = schedule[key][0]
    print("Visualizing schedule...", vis_schedule)
    visualize_schedule(graph, vis_schedule)
    #visualize_schedule_by_room(graph, schedule)
