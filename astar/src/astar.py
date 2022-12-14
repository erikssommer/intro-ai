from map import Map_Obj
from node import Node
from solution import Solution

# All algorithms are implemented based on the pseudocode given in "Essentials of the A* Algorithm" - handout


def best_first_search(map_obj: Map_Obj, task: int):
    """
    Using task parameter for choosing heuristic function based on if goal is moving or not
    """
    open: list[Node] = []  # Contains nodes sorted cheapest first by f-value
    closed: list[Node] = []  # Contains all visited nodes, unsorted

    # Initiating start and goal nodes
    start_node = Node(map_obj.get_start_pos())
    goal_node = Node(map_obj.get_goal_pos())

    # Initiating starting values (can also be done in construction of node)
    start_node.g = 0
    start_node.h = heuristic_function(
        start_node, goal_node) if task != 5 else heuristic_function_moving(start_node, goal_node)
    start_node.calculate_f()

    open.append(start_node)

    # Agenda loop - while no solution is found -> open-stack contains nodes
    while open:
        # Moves the goal one step every fourth call on task 5: moving goal
        if task == 5:
            goal_node.state = map_obj.tick()

        if len(open) == 0:
            return Solution.FAIL, None  # Fail

        current_node: Node = open.pop()

        closed.append(current_node)

        if current_node == goal_node:
            return Solution.SUCCESS, current_node  # Solution

        # Generating all successors from current node
        successors = current_node.generate_all_successors(map_obj)

        for successor in successors:
            # Checked for uniqueness
            node = uniqueness_check(successor, open, closed)
            current_node.children.append(successor)
            if node not in open and node not in closed:
                attach_and_eval(node, current_node, goal_node, map_obj, task)
                open.append(node)
                # Sorted by ascending f value
                open.sort(key=lambda node: node.f, reverse=True)
            elif (current_node.g + arc_cost(node, map_obj)) < node.g:
                attach_and_eval(node, current_node, goal_node, map_obj, task)
                if node in closed:
                    propagate_path_improvements(node, map_obj)


def uniqueness_check(successor: Node, open: list[Node], closed: list[Node]) -> Node:
    """
    Returns node if previously created, and successor if not
    Function is needed because "generate_all_successors()" method in node class
    creates new nodes without passing reference to the allready created node.
    This can be improved further
    """
    for node in open:
        if node == successor:
            return node

    for node in closed:
        if node == successor:
            return node

    return successor


def attach_and_eval(child: Node, parent: Node, goal_node: Node, map_obj: Map_Obj, task: int) -> None:
    """
    Attaches a child node to a node that is considered its best parent so far
    """
    child.parent = parent
    child.g = parent.g + arc_cost(child, map_obj)
    # Using different heuristic function in task 5 for better prediction
    child.h = heuristic_function(
        child, goal_node) if task != 5 else heuristic_function_moving(child, goal_node)
    child.f = child.g + child.h


def heuristic_function(current_node: Node, goal_node: Node) -> int:
    """
    Returns the Manhattan distance between the two nodes without any assumptions
    """
    return abs(current_node.state[0] - goal_node.state[0]) + abs(current_node.state[1] - goal_node.state[1])


def heuristic_function_moving(current_node: Node, goal_node: Node):
    """
    Heuristic function that uses manhattan distance using assumptions to make an estimate cost to the goal state,
    taking into account that the goal is moving 1/4 of our speed in negative x-direction.
    """
    cost_estimate = heuristic_function(current_node, goal_node)
    predict_goal_state = goal_node.state[0] - cost_estimate, goal_node.state[1]
    return abs(current_node.state[0] - predict_goal_state[0]) + abs(current_node.state[1] - predict_goal_state[1])


def arc_cost(child: Node, map_obj: Map_Obj) -> int:
    """
    Calculates the cost of taking the step
    """
    return map_obj.get_cell_value(child.state)


def propagate_path_improvements(parent: Node, map_obj: Map_Obj) -> None:
    """
    Insures that all nodes in the search graph are always aware of their current best parent and their current best g value,
    given the information that has been uncovered by the search algorithm up to that point in time.
    Recurses through the children.
    """
    child: Node
    for child in parent.children:
        if parent.g + arc_cost(child, map_obj) < child.g:
            child.parent = parent
            child.g = parent.g + arc_cost(child, map_obj)
            child.f = child.g + child.h
            propagate_path_improvements(child, map_obj)
