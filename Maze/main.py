import pygame
import random
import sys
import time
import heapq

# Initialize Pygame
pygame.init()

# Function to display information about the clicked cell
def display_info(mouse_x, mouse_y):
    row = mouse_y // cell_size
    col = mouse_x // cell_size
    if 0 <= row < rows and 0 <= col < cols:
        if maze[row][col] == 1:
            print("Error: This is an obstacle. Click on a free space.")
        elif maze[row][col] == 'S':
            print("Error: You already marked the start state. Click on a different free space.")
        elif maze[row][col] == 'G':
            print("Error: You already marked the goal state. Click on a different free space.")
        else:
            return row, col  # Return the coordinates if it's a valid free space
    else:
        print("Error: Click within the maze boundaries.")

# Set up display
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Maze Generator")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)  # New color for highlighting the path

# Set maze size to a fixed size of 21 rows and 21 columns
rows, cols = 21, 21
cell_size = min(width // rows, height // cols)

# Print information message
print("\n\nWelcome to Maze Generator!")
print("Generating a maze with {} rows and {} columns...".format(rows, cols))
print("Legend:")
print("  White area: Free space")
print("  Black area: Obstacles")
print("\nPlease wait while the maze is being generated...\n")
time.sleep(1)  # Add a delay

# Initialize maze grid
maze = [[0 for _ in range(cols)] for _ in range(rows)]

# Define directions
directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

# Function that provides Readable path
def convert_to_readable_path(path):
    readable_path = ""

    for i in range(1, len(path)):
        current, next_step = path[i - 1], path[i]
        dx = next_step[1] - current[1]
        dy = next_step[0] - current[0]

        if dx == 1:
            readable_path += "right"
        elif dx == -1:
            readable_path += "left"
        elif dy == 1:
            readable_path += "down"
        elif dy == -1:
            readable_path += "up"

        if i < len(path) - 1:
            readable_path += ", "

    return readable_path

class Node:
    def __init__(self, position, cost, heuristic):
        self.position = position
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

def heuristic(node_position, goal):
    return abs(node_position[0] - goal[0]) + abs(node_position[1] - goal[1])

def a_star(start, goal, maze):
    open_set = [Node(start, 0, heuristic(start, goal))]
    closed_set = set()

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.position == goal:
            path = []
            while current_node.position != start:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]

        closed_set.add(current_node.position)

        for dx, dy in directions:
            neighbor = (current_node.position[0] + dx, current_node.position[1] + dy)

            if (
                0 <= neighbor[0] < rows
                and 0 <= neighbor[1] < cols
                and maze[neighbor[0]][neighbor[1]] != 1
                and neighbor not in closed_set
            ):
                neighbor_node = Node(
                    neighbor,
                    current_node.cost + 1,
                    heuristic(neighbor, goal),
                )
                neighbor_node.parent = current_node
                heapq.heappush(open_set, neighbor_node)

    return None  # No path found

# Function to generate a maze starting from the top-left corner
def generate_maze(x, y):
    maze[x][y] = 1  # Mark the current cell as visited
    random.shuffle(directions)

    for dx, dy in directions:
        nx, ny = x + 2 * dx, y + 2 * dy

        if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
            maze[x + dx][y + dy] = 1
            generate_maze(nx, ny)

# Generate maze starting from the top-left corner
generate_maze(0, 0)
print("\nMaze generation completed successfully!\n")

# Main loop
running = True
start_state = None
goal_state = None
path = None  # Initialize path variable

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # Draw the maze
    screen.fill(white)
    for i in range(rows):
        for j in range(cols):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if maze[i][j] == 1:
                pygame.draw.rect(screen, black, rect)
            elif maze[i][j] == 'S':
                pygame.draw.rect(screen, green, rect)
            elif maze[i][j] == 'G':
                pygame.draw.rect(screen, red, rect)
            elif path is not None and (i, j) in path:
                pygame.draw.rect(screen, yellow, rect)

    # Update the display
    pygame.display.flip()

    # Mark the start state
    if start_state is None:
        print("\nClick on a free space to mark the start state (S).")
        waiting_for_start = True
        while waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        start_state = display_info(*pygame.mouse.get_pos())
                        if start_state is not None:
                            maze[start_state[0]][start_state[1]] = 'S'
                            waiting_for_start = False
                            print("\nStart state marked successfully at ({}, {}).".format(start_state[0], start_state[1]))
                            # Update the display after marking start state
                            pygame.draw.rect(screen, green, (start_state[1] * cell_size, start_state[0] * cell_size, cell_size, cell_size))
                            pygame.display.flip()

                            # Mark the goal state after marking the start state
                            if goal_state is None:
                                print("\nClick on a different free space to mark the goal state (G).")
                                waiting_for_goal = True
                                while waiting_for_goal:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                        elif event.type == pygame.MOUSEBUTTONDOWN:
                                            if event.button == 1:  # Left mouse button
                                                goal_state = display_info(*pygame.mouse.get_pos())
                                                if goal_state is not None and goal_state != start_state:
                                                    maze[goal_state[0]][goal_state[1]] = 'G'
                                                    waiting_for_goal = False
                                                    print("Goal state marked successfully at ({}, {}).".format(goal_state[0], goal_state[1]))
                                                    # Update the display after marking goal state
                                                    pygame.draw.rect(screen, red, (goal_state[1] * cell_size, goal_state[0] * cell_size, cell_size, cell_size))
                                                    pygame.display.flip()

                                                    # Calculate and display the shortest path using A*
                                                    if goal_state is not None and path is None:
                                                        path = a_star(start_state, goal_state, maze)
                                                        if path is not None:
                                                            print("\nShortest path found:")
                                                            print(path)

                                                            # Convert the path to a readable format
                                                            readable_path = convert_to_readable_path(path)
                                                            print("Readable path:", readable_path)

                                                            # Update the display after finding the shortest path
                                                            for i, j in path:
                                                                pygame.draw.rect(screen, yellow, (j * cell_size, i * cell_size, cell_size, cell_size))
                                                                pygame.display.flip()
                                                            pygame.time.wait(3000)  # Wait for 3 seconds (adjust as needed)

                                                    if goal_state is not None and path is None:
                                                        print("\nNo path found from start to goal. The goal is unreachable.")
                                                        print("Thank you for using the maze generator. Exiting...")
