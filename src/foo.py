import curses
import random
import heapq

class Cell:
    def __init__(self, value=0):
        self.value = value

    def toggle(self):
        self.value = 1 if self.value == 0 else 0

class Enemy:
    def __init__(self, x, y, health, speed, damage):
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed
        self.damage = damage

    def move(self, grid):
        path = self.a_star(grid, (self.x, self.y), (self.x, grid.height - 1))
        if path and len(path) > 1:
            next_x, next_y = path[1]  # Take the first step on the path
            grid.cells[self.y][self.x].value = 0
            self.x, self.y = next_x, next_y
            grid.cells[self.y][self.x].value = 2
        elif grid.cells[self.y][self.x].value == 1:
            grid.cells[self.y][self.x].value = 0  # Destroy the tower if blocked

    def a_star(self, grid, start, goal):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        open_set = []
        heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[2]
            if current == goal:
                return self.reconstruct_path(came_from, current)
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < grid.width and 0 <= neighbor[1] < grid.height:
                    if grid.cells[neighbor[1]][neighbor[0]].value == 1:
                        continue  
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], id(neighbor), neighbor))
        return []

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(current)
        return path[::-1]

class Grid:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]
        self.enemies = []

    def render(self, stdscr, x, y):
        for i in range(self.height):
            for j in range(self.width):
                cell = self.cells[i][j]
                if i == y and j == x:
                    stdscr.attron(curses.color_pair(3))
                    stdscr.addstr(i, j * 2, "X ")
                    stdscr.attroff(curses.color_pair(3))
                elif cell.value == 0:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(i, j * 2, "0 ")
                    stdscr.attroff(curses.color_pair(1))
                elif cell.value == 1:
                    stdscr.attron(curses.color_pair(2))
                    stdscr.addstr(i, j * 2, "1 ")
                    stdscr.attroff(curses.color_pair(2))
                elif cell.value == 2:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(i, j * 2, "E ")
                    stdscr.attroff(curses.color_pair(4))

    def toggle_cell(self, x, y):
        self.cells[y][x].toggle()

    def add_enemy_random(self):
        x = random.randint(0, self.width - 1)
        if self.cells[0][x].value == 0:
            new_enemy = Enemy(x, 0, 100, 1, 10)
            self.enemies.append(new_enemy)
            self.cells[0][x].value = 2

    def move_enemies(self):
        for enemy in list(self.enemies):
            enemy.move(self)
            if enemy.y == self.height - 1:
                self.cells[enemy.y][enemy.x].value = 0
                self.enemies.remove(enemy)

class Game:
    def __init__(self, height, width):
        self.grid = Grid(height, width)
        self.x = 0
        self.y = 0
        self.running = True

    def run(self, stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.curs_set(0)
        curses.halfdelay(3)  # Set non-blocking input delay to 0.3 seconds

        while self.running:
            stdscr.clear()
            self.grid.render(stdscr, self.x, self.y)
            self.grid.move_enemies()
            stdscr.refresh()

            key = stdscr.getch()
            if key != -1:  # If a key is pressed
                self.process_input(key)

    def process_input(self, key):
        if key == curses.KEY_UP and self.y > 0:
            self.y -= 1
        elif key == curses.KEY_DOWN and self.y < self.grid.height - 1:
            self.y += 1
        elif key == curses.KEY_LEFT and self.x > 0:
            self.x -= 1
        elif key == curses.KEY_RIGHT and self.x < self.grid.width - 1:
            self.x += 1
        elif key == ord(' '):
            self.grid.toggle_cell(self.x, self.y)
        elif key == ord('r'):
            self.grid.add_enemy_random()
        elif key == ord('q'):
            self.running = False

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: Game(24, 15).run(stdscr))
