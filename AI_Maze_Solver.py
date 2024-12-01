import pygame
import random
import heapq

# Colors
WHITE = (255, 255, 255)
GREY = (220, 220, 220)
DARK_GREY = (120, 120, 120)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

UPDATE_TIME_MS = 250
# Initialize Pygame
pygame.init()

# Set up the window size and title
window_height = 700
window_width = 700
window_size = (window_width, window_height)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Maze Solver")

# Define the size of the maze and size of each cell
maze_size = 10
cell_size = window_size[0] // maze_size

# Button class
class Button:
    def __init__(self, x, y, width, height, color, text, font, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, screen, mouse_pos):
        # Change color if the mouse is over the button
        if self.rect.collidepoint(mouse_pos):
            display_color = DARK_GREY  
        else:
            display_color = self.color

        # Draw the button
        pygame.draw.rect(screen, display_color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        # Check if the button is clicked
        return self.rect.collidepoint(mouse_pos)

# Font for buttons
font = pygame.font.Font(None, 36)

# Button setup
button_width = 220
button_height = 50
button_spacing = 20  
num_buttons = 5
total_button_height = (button_height * num_buttons) + (button_spacing * (num_buttons - 1))

start_y = (window_size[1] - total_button_height) // 2
start_x = (window_size[0] - button_width) // 2  

buttons = [
    Button(start_x, start_y, button_width, button_height, BLACK, 'Generate Maze', font, WHITE),
    Button(start_x, start_y + button_height + button_spacing, button_width, button_height, BLACK, 'Solve by DFS', font, WHITE),
    Button(start_x, start_y + 2 * (button_height + button_spacing), button_width, button_height, BLACK, 'Solve by BFS', font, WHITE),
    Button(start_x, start_y + 3 * (button_height + button_spacing), button_width, button_height, BLACK, 'Solve by UCS', font, WHITE),
    Button(start_x, start_y + 4 * (button_height + button_spacing), button_width, button_height, BLACK, 'Quit', font, WHITE)
]
back_button = Button(window_width-39, -4, 40, 40, WHITE, '<', font, BLACK)

# Maze class and generation logic
class Cell:
    def __init__(self,cost=1):
        self.neighbor = []
        self.generated = False
        self.visited = False
        self.cost = cost

    def set_neighbor(self, neighbor):
        self.neighbor.append(neighbor)
    def set_generated(self):
        """Mark the cell as generated"""
        self.generated = True

    def set_visited(self):
        """Mark the cell as visited"""
        self.visited = True

    def get_neighbor(self):
        """Get the list of neighboring cells"""
        return self.neighbor

    def get_generated(self):
        """Check if the cell has been generated"""
        return self.generated

    def get_visited(self):
        """Check if the cell has been visited"""
        return self.visited
        
    def get_cost(self):
        return self.cost
    
class Maze:
    def __init__(self, maze_size, cell_size):
        self.maze_size = maze_size
        self.cell_size = cell_size
        self.maze = [
            Cell(cost=2 if random.random() < 0.3 else 1) for _ in range(self.maze_size * self.maze_size)
            ]
        self.path = {  
            'DFS': [],
            'BFS': [],
            'UCS': []
        }

    def at(self, x, y):
        return self.maze[y * self.maze_size + x]

    def generate(self, extra_paths=5):
        visited = 0
        stack = []
        # Start from a random cell
        x = random.randint(0, self.maze_size - 1)
        y = random.randint(0, self.maze_size - 1)
        stack.append((x, y))
        self.at(x, y).set_generated()
        visited += 1

        # Generate the single-solution maze
        while visited < self.maze_size * self.maze_size:
            x = stack[-1][0]
            y = stack[-1][1]

            neighbor = []

            if x > 0 and not self.at(x - 1, y).get_generated():
                neighbor.append('left')
            if x < self.maze_size - 1 and not self.at(x + 1, y).get_generated():
                neighbor.append('right')
            if y > 0 and not self.at(x, y - 1).get_generated():
                neighbor.append('up')
            if y < self.maze_size - 1 and not self.at(x, y + 1).get_generated():
                neighbor.append('down')

            if neighbor:
                random_next = random.choice(neighbor)

                if random_next == 'left':
                    self.at(x, y).set_neighbor('left')
                    self.at(x - 1, y).set_neighbor('right')
                    self.at(x - 1, y).set_generated()
                    stack.append((x - 1, y))
                elif random_next == 'right':
                    self.at(x, y).set_neighbor('right')
                    self.at(x + 1, y).set_neighbor('left')
                    self.at(x + 1, y).set_generated()
                    stack.append((x + 1, y))
                elif random_next == 'up':
                    self.at(x, y).set_neighbor('up')
                    self.at(x, y - 1).set_neighbor('down')
                    self.at(x, y - 1).set_generated()
                    stack.append((x, y - 1))
                elif random_next == 'down':
                    self.at(x, y).set_neighbor('down')
                    self.at(x, y + 1).set_neighbor('up')
                    self.at(x, y + 1).set_generated()
                    stack.append((x, y + 1))
                visited += 1
            else:
                stack.pop()

        # Add extra paths to allow multiple solutions
        for _ in range(extra_paths):
            self._add_random_connection()

    def _add_random_connection(self):
        x, y = random.randint(0, self.maze_size - 1), random.randint(0, self.maze_size - 1)
        directions = []

        if x > 0:
            directions.append('left')
        if x < self.maze_size - 1:
            directions.append('right')
        if y > 0:
            directions.append('up')
        if y < self.maze_size - 1:
            directions.append('down')

        if directions:
            direction = random.choice(directions)
            nx, ny = x, y

            if direction == 'left':
                nx, ny = x - 1, y
            elif direction == 'right':
                nx, ny = x + 1, y
            elif direction == 'up':
                nx, ny = x, y - 1
            elif direction == 'down':
                nx, ny = x, y + 1

            # Ensure the neighboring cell exists and doesn't already have a connection
            if (nx, ny) in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                self.at(x, y).set_neighbor(direction)
                opposite = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}
                self.at(nx, ny).set_neighbor(opposite[direction])


# -------------- Solving by DFS Functions ----------------

    def solve_dfs(self, show: bool = True, delay: int = 10, show_visited: bool = True):

        stack = [(0,0)]
        x = 0
        y = 0
        stack.append((x, y))
        self.at(x, y).set_visited()

        while x != self.maze_size - 1 or y != self.maze_size - 1:
            x = stack[-1][0]
            y = stack[-1][1]
            self.at(x, y).set_visited()

            backtrack: bool = True
            neighbor: list[str] = self.at(x, y).get_neighbor()

            for go_to in neighbor:
                if go_to == 'left' and self.at(x - 1, y).get_visited() is False:
                    stack.append((x - 1, y))
                    backtrack = False
                elif go_to == 'right' and self.at(x + 1, y).get_visited() is False:
                    stack.append((x + 1, y))
                    backtrack = False
                elif go_to == 'up' and self.at(x, y - 1).get_visited() is False:
                    stack.append((x, y - 1))
                    backtrack = False
                elif go_to == 'down' and self.at(x, y + 1).get_visited() is False:
                    stack.append((x, y + 1))
                    backtrack = False

            if backtrack:
                stack.pop()

            if show:
                self.show(algorithm='DFS',show_visited=show_visited)
                pygame.draw.rect(screen, GREEN, (x * self.cell_size,
                                                y * self.cell_size,
                                                self.cell_size,
                                                self.cell_size))
                pygame.display.update()
                pygame.time.delay(delay)

        self.path['DFS'] = stack

        return self.__get_path()

    def __get_path(self):

        self.__remove_ghost_path()
        return self.path['DFS']

    def __remove_ghost_path(self):

        remove: list = list()
        for i in range(1, len(self.path['DFS'])):
            x = self.path["DFS"][i][0]
            y = self.path["DFS"][i][1]

            count: int = 0
            neighbor: list[str] = self.at(x, y).get_neighbor()

            for go_to in neighbor:
                if go_to == 'left' and (x - 1, y) not in self.path['DFS']:
                    count += 1
                elif go_to == 'right' and (x + 1, y) not in self.path['DFS']:
                    count += 1
                elif go_to == 'up' and (x, y - 1) not in self.path['DFS']:
                    count += 1
                elif go_to == 'down' and (x, y + 1) not in self.path['DFS']:
                    count += 1

            if len(neighbor) - count == 1:
                remove.append(i)

        for i in remove[::-1]:
            self.path['DFS'].pop(i)

        if (self.maze_size - 1, self.maze_size - 1) not in self.path['DFS']:
            self.path['DFS'] += [(self.maze_size - 1, self.maze_size - 1)]

# -------------- Solving by BFS Functions ----------------

    def solve_bfs(self, show=True, delay=UPDATE_TIME_MS, show_visited=True):
        queue = [(0, 0)]
        self.at(0, 0).set_visited()
        parent_map = {}

        while queue:
            x, y = queue.pop(0)

            if x == self.maze_size - 1 and y == self.maze_size - 1:
                self.path['BFS'] = self.__reconstruct_path(parent_map, (0, 0), (x, y))
                return self.__get_path()

            for direction in self.at(x, y).get_neighbor():
                nx, ny = x, y
                if direction == 'left':
                    nx, ny = x - 1, y
                elif direction == 'right':
                    nx, ny = x + 1, y
                elif direction == 'up':
                    nx, ny = x, y - 1
                elif direction == 'down':
                    nx, ny = x, y + 1

                if not self.at(nx, ny).get_visited():
                    self.at(nx, ny).set_visited()
                    parent_map[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

                    if show:
                        self.show(show_visited,algorithm='BFS')
                        pygame.draw.rect(screen, GREEN, (nx * self.cell_size,
                                                         ny * self.cell_size,
                                                         self.cell_size,
                                                         self.cell_size))
                        pygame.display.flip()
                        pygame.time.delay(delay)

        return []

    def __reconstruct_path(self, parent_map, start, goal):
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent_map[current]
        path.append(start)
        path.reverse()
        return path

    def __get_path(self):
        return self.path['BFS']
    
# -------------- Solving by UCS Functions ----------------

    def solve_ucs(self, show=True, delay=UPDATE_TIME_MS, show_visited=True):
        # Priority queue for UCS, stores (cost, x, y)
        priority_queue = [(0, 0, 0)]
        heapq.heapify(priority_queue)
        self.at(0, 0).set_visited()
        parent_map = {}
        cost_map = {(0, 0): 0}

        while priority_queue:
            cost, x, y = heapq.heappop(priority_queue)

            if x == self.maze_size - 1 and y == self.maze_size - 1:
                self.path['UCS'] = self.__reconstruct_path(parent_map, (0, 0), (x, y))
                return self.__get_path(), cost_map

            for direction in self.at(x, y).get_neighbor():
                nx, ny = x, y
                if direction == 'left':
                    nx, ny = x - 1, y
                elif direction == 'right':
                    nx, ny = x + 1, y
                elif direction == 'up':
                    nx, ny = x, y - 1
                elif direction == 'down':
                    nx, ny = x, y + 1

                new_cost = cost + self.at(nx, ny).get_cost()
                if (nx, ny) not in cost_map or new_cost < cost_map[(nx, ny)]:
                    cost_map[(nx, ny)] = new_cost
                    parent_map[(nx, ny)] = (x, y)
                    heapq.heappush(priority_queue, (new_cost, nx, ny))
                    self.at(nx, ny).set_visited()

                    if show:
                        self.show(show_visited, (nx, ny), cost_map,'UCS')
                        pygame.draw.rect(screen, GREEN, (nx * self.cell_size,
                                                         ny * self.cell_size,
                                                         self.cell_size,
                                                         self.cell_size))
                        pygame.display.flip()
                        pygame.time.delay(delay)
        return [], cost_map

# -------------- Showing the path Functions ----------------

    def reset(self):
        for cell in self.maze:
            cell.visited = False  # Clear visited status
        

    def show(self, show_visited=False, current=None, cost_map=None,algorithm=None):
    
        for y in range(self.maze_size):
            for x in range(self.maze_size):
                cell = self.at(x, y)
                
                # Draw visited cells
                if show_visited and cell.get_visited():
                    pygame.draw.rect(
                        screen,
                        DARK_GREY if cell.get_cost() == 2 else GREY,
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    )
                if algorithm == "UCS":
                    pygame.draw.rect(
                        screen,
                        DARK_GREY if cell.get_cost() == 2 else GREY,
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    )
                # Draw cost values on cells if cost_map is provided
                if show_visited and cost_map and (x, y) in cost_map:
                    cost = cost_map[(x, y)]
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(str(cost), True, BLACK)
                    text_rect = text.get_rect(
                        center=(
                            x * self.cell_size + self.cell_size // 2,
                            y * self.cell_size + self.cell_size // 2,
                        )
                    )
                    screen.blit(text, text_rect)
                
                # Draw maze walls
                if 'left' not in cell.neighbor:
                    pygame.draw.line(
                        screen, BLACK,
                        (x * self.cell_size, y * self.cell_size),
                        (x * self.cell_size, (y + 1) * self.cell_size)
                    )
                if 'right' not in cell.neighbor:
                    pygame.draw.line(
                        screen, BLACK,
                        ((x + 1) * self.cell_size, y * self.cell_size),
                        ((x + 1) * self.cell_size, (y + 1) * self.cell_size)
                    )
                if 'up' not in cell.neighbor:
                    pygame.draw.line(
                        screen, BLACK,
                        (x * self.cell_size, y * self.cell_size),
                        ((x + 1) * self.cell_size, y * self.cell_size)
                    )
                if 'down' not in cell.neighbor:
                    pygame.draw.line(
                        screen, BLACK,
                        (x * self.cell_size, (y + 1) * self.cell_size),
                        ((x + 1) * self.cell_size, (y + 1) * self.cell_size)
                    )
        
        
        # Highlight the current cell for UCS or other algorithms
        if (algorithm == 'UCS') and current:
            print(current)
            
            # Ensure current is a tuple with exactly two numeric values
            if len(current) != 2:
                print(f"Invalid current state: {current}")
                return
            
            cx, cy = current  # Only unpack two values
            
            try:
                cx = int(cx)
                cy = int(cy)
            except ValueError:
                print(f"Invalid coordinate: cx = {cx}, cy = {cy}")
                return  # Skip this iteration if coordinates are invalid

            print(f"cx: {cx}, cy: {cy}, cell_size: {self.cell_size}")

            pygame.draw.rect(
                screen, GREEN,
                (cx * self.cell_size, cy * self.cell_size, self.cell_size, self.cell_size),
                width=3
            )

        # Highlight the path
        if algorithm:
            for x, y in self.path[algorithm]:
                pygame.draw.circle(
                    screen,
                    BLUE,
                    (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2),
                    self.cell_size // 8
                )
        
        pygame.display.update()

    def display_saved_path(self, algorithm, cost_map=None):
        if algorithm in self.path and self.path[algorithm]:
 
                for x, y in self.path[algorithm]:
                    # Draw the path circle
                    pygame.draw.circle(
                        screen,
                        BLUE,
                        (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2),
                        self.cell_size // 8
                    )

                    # Draw the cost on the path (if a cost map is available)
                    if algorithm == 'UCS' and cost_map and (x, y) in cost_map:
                        cost = cost_map[(x, y)]
                        font = pygame.font.SysFont(None, 24)
                        text = font.render(str(cost), True, BLACK)
                        text_rect = text.get_rect(
                            center=(
                                x * self.cell_size + self.cell_size // 2,
                                y * self.cell_size + self.cell_size // 2,
                            )
                        )
                        screen.blit(text, text_rect)
            
                pygame.display.update()
        else:
            print(f"No path saved for {algorithm}.")


# Game states
MAIN_MENU = "MAIN_MENU"
MAZE_VIEW = "MAZE_VIEW"
DFS_VIEW = "DFS_VIEW"
BFS_VIEW = "BFS_VIEW"
UCS_VIEW = "UCS_VIEW"
current_state = MAIN_MENU
maze = None
dfs_solution = False
bfs_solution = False
ucs_solution = False
# Main loop
running = True

while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    back_button.draw(screen, mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle MAIN_MENU state
            if current_state == MAIN_MENU:
                for button in buttons:
                    if button.is_clicked(mouse_pos):
                        if button.text == 'Quit':
                            running = False
                        elif button.text == 'Generate Maze':
                            dfs_solution = bfs_solution = ucs_solution = False
                            current_state = MAZE_VIEW
                            maze = Maze(maze_size, cell_size)
                            maze.generate(extra_paths=8)
                        elif button.text.startswith('Solve'):
                            if not maze:
                                print("There is no maze generated")
                                continue
                            current_state = MAZE_VIEW

                            if button.text == 'Solve by DFS':
                                if dfs_solution:
                                    current_state = DFS_VIEW
                                    print("Solution is already found!")
                                    maze.display_saved_path("DFS")
                                elif maze:
                                    if bfs_solution or ucs_solution:
                                        maze.reset()
                                    current_state = DFS_VIEW
                                    solution_path= maze.solve_dfs(show=True,delay = UPDATE_TIME_MS,show_visited=True)
                                    print('Solution path: ', solution_path)
                                    maze.show(True,algorithm='DFS')
                                    dfs_solution = True
                                else:
                                    print("There is no maze generated")
                            elif button.text == 'Solve by BFS':
                                if bfs_solution:
                                    current_state = BFS_VIEW
                                    print("Solution is already found!")
                                    maze.display_saved_path("BFS")
                                elif maze:
                                    if dfs_solution or ucs_solution:
                                        maze.reset()
                                    current_state = BFS_VIEW
                                    solution_path = maze.solve_bfs(show=True,delay = UPDATE_TIME_MS,show_visited=True)
                                    print('Solution path: ', solution_path)
                                    maze.show(True,algorithm='BFS')
                                    bfs_solution = True
                                else:
                                    print("There is no maze generated")
                            elif button.text == 'Solve by UCS':
                                if ucs_solution:
                                    current_state = UCS_VIEW
                                    print("Solution is already found!")
                                    maze.display_saved_path("DFS",cost_map=cost_map)
                                elif maze:
                                    if dfs_solution or bfs_solution:
                                        maze.reset()
                                    current_state = UCS_VIEW
                                    solution_path, cost_map = maze.solve_ucs(show=True,delay = UPDATE_TIME_MS,show_visited=True)
                                    print('Solution path: ', solution_path)
                                    maze.show(True,algorithm= 'UCS', cost_map=cost_map)
                                    ucs_solution = True
                                else:
                                    print("There is no maze generated")

                            print('Solution path:', solution_path)

            # Handle MAZE_VIEW state
            elif current_state != MAIN_MENU:
                if back_button.is_clicked(mouse_pos):
                    current_state = MAIN_MENU

    # Draw UI based on the state
    if current_state == MAIN_MENU:
        for button in buttons:
            button.draw(screen, mouse_pos)
    elif current_state == MAZE_VIEW:
        if maze:
            maze.show(algorithm=None)
    elif current_state == DFS_VIEW:
        if maze:
            maze.show(algorithm='DFS')
    elif current_state == BFS_VIEW:
        if maze:
            maze.show(algorithm='BFS')
    elif current_state == UCS_VIEW:
        if maze:
            maze.show(algorithm='UCS')

    pygame.display.update()

pygame.quit()