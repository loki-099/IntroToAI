from pyamaze import maze, agent, textLabel, COLOR
from heapq import heappush, heappop


def heuristic(cell, goal):
    # Manhattan distance heuristic
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def astar(m):

    start = (m.rows, m.cols)   # bottom-right corner
    goal  = (1, 1)             # top-left corner (pyamaze default goal)

    # Priority queue entries: (f, g, cell)
    open_heap = []
    heappush(open_heap, (heuristic(start, goal), 0, start))

    g_map   = {start: 0}       # best g-cost seen so far
    came_from = {}             # for path reconstruction
    closed  = set()

    # Direction → (row_delta, col_delta)
    direction_delta = {
        'E': (0,  1),
        'W': (0, -1),
        'N': (-1, 0),
        'S': ( 1, 0),
    }

    while open_heap:
        f, g, current = heappop(open_heap)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            break

        for direction, (dr, dc) in direction_delta.items():
            # Only move if the wall is open
            if not m.maze_map[current][direction]:
                continue

            neighbor = (current[0] + dr, current[1] + dc)
            if neighbor in closed:
                continue

            tentative_g = g + 1                       # uniform step cost
            if tentative_g < g_map.get(neighbor, float('inf')):
                g_map[neighbor] = tentative_g
                came_from[neighbor] = current
                f_new = tentative_g + heuristic(neighbor, goal)
                heappush(open_heap, (f_new, tentative_g, neighbor))

    return came_from, g_map


def reconstruct_path(came_from, start, goal):
    """Trace back from goal to start and return ordered path list."""
    path = []
    cell = goal
    while cell != start:
        path.append(cell)
        cell = came_from[cell]
    path.append(start)
    path.reverse()
    return path


if __name__ == '__main__':
    ROWS, COLS = 8, 8 # maze dimensions – feel free to change

    # Create and generate a random maze
    m = maze(ROWS, COLS)
    m.CreateMaze(loopPercent=30) # loopPercent > 0 adds extra passages

    start = (ROWS, COLS)
    goal  = (1, 1)

    # Run A*
    came_from, g_map = astar(m)

    if goal not in came_from and goal != start:
        print("No path found!")
    else:
        path_list = reconstruct_path(came_from, start, goal)
        path_dict = {path_list[i]: path_list[i + 1]
            for i in range(len(path_list) - 1)}

        path_length = len(path_list) - 1 # number of steps
        cells_explored = len(g_map)

        print(f"A* found path in {path_length} steps "
            f"(explored {cells_explored} cells).")

        # Visualisation #######################################

        # Agent that traces the solution path
        solution_agent = agent(
            m,
            footprints=True,
            shape='arrow',
            color=COLOR.cyan,
            filled=True,
        )

        # Agent that shows all explored cells
        explored_agent = agent(
            m,
            footprints=True,
            shape='square',
            color=COLOR.yellow,
            filled=False,
        )

        # Labels
        textLabel(m, 'A* Path Length',    path_length)
        textLabel(m, 'Cells Explored',    cells_explored)

        explored_ordered = sorted(g_map, key=lambda c: g_map[c])
        explored_dict = {explored_ordered[i]: explored_ordered[i + 1]
            for i in range(len(explored_ordered) - 1)}

        # Animate: first show explored cells, then the solution
        m.tracePath(
            {explored_agent: explored_dict},
            delay=100,
        )
        m.tracePath(
            {solution_agent: path_dict},
            delay=200,
        )

        m.run()