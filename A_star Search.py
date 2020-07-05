import pygame
import math
from copy import deepcopy
import time
import random

pygame.init()


class Button:
    def __init__(self, x, y, colour, width, height, text):
        self.x = x
        self.y = y
        self.colour = colour
        self.text = text
        self.width = width
        self.height = height

    def isOverButton(self, mouse):
        if self.x <= mouse[0] <= self.x + self.width:
            if self.y <= mouse[1] <= self.y + self.height:
                return True
        return False


class Grid:
    search = False
    draw_wall = False
    found_path = False
    start = False
    start_coordinates = (0, 0)
    destination = False
    failed = False
    destination_coordinates = (0, 0)

    def __init__(self):
        self.path_cost = 5
        self.walls = []
        self.optimal_path = []
        self.expanded_nodes = []
        self.path = []
        self.block_size = 16
        self.number_of_blocks = 35
        self.done_button = Button(700, 700, (175, 20, 0), 100, 50, "Done")
        self.clear_button = Button(700, 700, (175, 20, 0), 100, 50, "Clear")
        self.screen_dimensions = (self.block_size * self.number_of_blocks,
                                  self.block_size * self.number_of_blocks + 100)
        self.screen = pygame.display.set_mode(self.screen_dimensions)
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.startApp()

    def drawGrid(self):
        self.screen.fill((200, 200, 200))
        for i in range(0, self.number_of_blocks):
            for j in range(0, self.number_of_blocks):
                pygame.draw.rect(self.screen, (0, 0, 0), (self.block_size * j, self.block_size * i, self.block_size,
                                                          self.block_size), 1)

    def startApp(self):
        pygame.display.set_caption('A* Path Finder')
        drag = False
        run = True
        while run:
            mouse = pygame.mouse.get_pos()
            self.drawGrid()
            if self.done_button.isOverButton(mouse):
                self.done_button.colour = (255, 0, 0)
            else:
                self.done_button.colour = (175, 20, 0)

            if self.clear_button.isOverButton(mouse):
                self.clear_button.colour = (255, 0, 0)
            else:
                self.clear_button.colour = (175, 20, 0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.done_button.isOverButton(mouse):
                        self.draw_wall = False
                        drag = False
                        self.drawTexts()
                        self.searchPath()
                        break

                    if self.clear_button.isOverButton(mouse):
                        self.clear()
                        break

                    for i in range(0, self.number_of_blocks):
                        for j in range(0, self.number_of_blocks):
                            if self.isOver(self.block_size * j, self.block_size * i, mouse):
                                if not self.start:
                                    self.start_coordinates = (self.block_size * j, self.block_size * i)
                                    self.start = True

                                elif not self.destination and self.start:
                                    if (self.block_size * j, self.block_size * i) != self.start_coordinates:
                                        if (self.block_size * j, self.block_size * i) != self.destination_coordinates:
                                            self.destination_coordinates = (self.block_size * j, self.block_size * i)
                                            self.destination = True
                                            self.draw_wall = True

                                elif self.draw_wall:
                                    self.walls.append((self.block_size * j, self.block_size * i))
                                    drag = True

                if drag:
                    for i in range(0, self.number_of_blocks):
                        for j in range(0, self.number_of_blocks):
                            if self.isOver(self.block_size * j, self.block_size * i, mouse):
                                if (self.block_size * j, self.block_size * i) != self.start_coordinates and (
                                        self.block_size * j, self.block_size * i) != self.destination_coordinates:
                                    self.walls.append((self.block_size * j, self.block_size * i))

                if event.type == pygame.MOUSEBUTTONUP:
                    drag = False
                    break

            self.drawPoint()
            self.drawWalls()
            self.drawTexts()
            if self.start and self.destination and not self.draw_wall:
                self.drawExpandedNodes()
                self.drawFrontier()
                self.drawOptimal()
                self.drawPoint()
                self.drawTexts()

            if not (self.start and self.destination):
                for i in range(0, self.number_of_blocks):
                    for j in range(0, self.number_of_blocks):
                        if self.isOver(self.block_size * j, self.block_size * i, mouse):
                            if (self.block_size * j, self.block_size * i) != self.start_coordinates:
                                pygame.draw.rect(self.screen, (255, 255, 255),
                                                 (self.block_size * j, self.block_size * i, self.block_size,
                                                  self.block_size))

            elif self.draw_wall:
                for i in range(0, self.number_of_blocks):
                    for j in range(0, self.number_of_blocks):
                        if self.isOver(self.block_size * j, self.block_size * i, mouse):
                            if (self.block_size * j, self.block_size * i) != self.start_coordinates and \
                                    (self.block_size * j, self.block_size * i) != self.destination_coordinates:
                                pygame.draw.rect(self.screen, (0, 0, 0),
                                                 (self.block_size * j, self.block_size * i, self.block_size,
                                                  self.block_size))
            pygame.display.update()

    def isOver(self, x, y, mouse):
        if x < mouse[0] < x + self.block_size:
            if y < mouse[1] < y + self.block_size:
                return True
        return False

    def isOverDone(self, mouse):
        if self.done_button[0] < mouse[0] < self.done_button[0] + 100:
            if self.done_button[1] - 20 < mouse[1] < self.done_button[1] + 30:
                return True
        return False

    def isOverClear(self, mouse):
        if self.clear_button[0] < mouse[0] < self.clear_button[0] + 100:
            if self.clear_button[1] - 20 < mouse[1] < self.clear_button[1] + 30:
                return True
        return False

    def drawPoint(self):  # draw rectangle of start and destination
        if self.start == True:
            pygame.draw.rect(self.screen, (0, 105, 0),
                             (self.start_coordinates[0], self.start_coordinates[1], self.block_size,
                              self.block_size))

        if self.destination == True:
            if self.start == True:
                pygame.draw.rect(self.screen, (0, 0, 255),
                                 (self.destination_coordinates[0], self.destination_coordinates[1], self.block_size,
                                  self.block_size))

    def drawWalls(self):  # draw walls
        for i in range(len(self.walls)):
            pygame.draw.rect(self.screen, (0, 0, 0),
                             (self.walls[i][0], self.walls[i][1], self.block_size,
                              self.block_size))

    def drawTexts(self):  # display what to do
        if not self.start:
            text = self.font.render("Select The Starting Node", True, (0, 0, 0))
            self.screen.blit(text, (150, 600))

        elif not self.destination:
            text = self.font.render("Select The Destination Node", True, (0, 0, 0))
            self.screen.blit(text, (150, 600))

        elif self.draw_wall:
            self.done_button.x = 300
            self.done_button.y = 585
            text = self.font.render("Draw Walls", True, (0, 0, 0))
            self.screen.blit(text, (50, 600))

            pygame.draw.rect(self.screen, self.done_button.colour,
                             (self.done_button.x, self.done_button.y, self.done_button.width,
                              self.done_button.height))
            text = self.font.render(self.done_button.text, True, (0, 0, 0))
            self.screen.blit(text, (325, 600))

        elif self.found_path:
            self.done_button.x = 700
            self.done_button.y = 700
            self.clear_button.x = 300
            self.clear_button.y = 585
            text = self.font.render("Found Optimal Path !!", True, (0, 0, 0))
            self.screen.blit(text, (50, 600))
            pygame.draw.rect(self.screen, self.clear_button.colour,
                             (self.clear_button.x, self.clear_button.y, self.clear_button.width,
                              self.clear_button.height))
            text = self.font.render(self.clear_button.text, True, (0, 0, 0))
            self.screen.blit(text, (325, 600))

        elif self.failed:
            self.done_button.x = 700
            self.done_butoton.y = 700
            self.clear_button.x = 300
            self.clear_button.y = 585
            text = self.font.render("No Path Exists", True, (0, 0, 0))
            self.screen.blit(text, (50, 600))
            pygame.draw.rect(self.screen, self.clear_button.colour,
                             (self.clear_button.x, self.clear_button.y, self.clear_button.width,
                              self.clear_button.height))
            text = self.font.render(self.clear_button.text, True, (0, 0, 0))
            self.screen.blit(text, (325, 600))

        else:
            self.done_button.x = 700
            self.done_button.y = 700
            text = self.font.render("Finding Optimal Path", True, (0, 0, 0))
            self.screen.blit(text, (150, 600))

    def drawExpandedNodes(self):  # draw expanded nodes
        for node in self.expanded_nodes:
            pygame.draw.rect(self.screen, (255, 50, 0),
                             (node[0], node[1], self.block_size,
                              self.block_size))

    def drawFrontier(self):  # draw Frontier nodes
        for path in self.path:
            for node in path:
                if node not in self.expanded_nodes:
                    pygame.draw.rect(self.screen, (255, 180, 0),
                                     (node[0], node[1], self.block_size,
                                      self.block_size))

    def drawOptimal(self):  # draw the optimal path
        for node in self.optimal_path:
            pygame.draw.rect(self.screen, (175, 40, 205),
                             (node[0], node[1], self.block_size,
                              self.block_size))

    def searchPath(self):
        self.path = [[self.start_coordinates]]
        self.expandNode()
        while self.found_path == False and len(self.path) > 0:
            self.sort()
            self.expandNode()
            self.drawExpandedNodes()
            self.drawFrontier()
            self.drawPoint()
            self.drawWalls()
            pygame.display.update()
            time.sleep(0.0001)
        if len(self.path) == 0:
            self.failed = True
        else:
            self.drawOptimal()

    def expandNode(self):  # Expand the first element of self.paths_with_values
        required_path = self.path.pop()
        x = required_path[-1][0]
        y = required_path[-1][1]
        if (x, y) == self.destination_coordinates:
            self.found_path = True
            self.optimal_path = required_path
        else:
            if ((x + self.block_size, y) not in self.walls) and x < 544 and (x, y) not in self.expanded_nodes:
                copy_path = deepcopy(required_path)
                copy_path.append((x + self.block_size, y))
                self.path.append(copy_path)

            if ((x - self.block_size, y) not in self.walls) and x > 0 and (x, y) not in self.expanded_nodes:
                copy_path = deepcopy(required_path)
                copy_path.append((x - self.block_size, y))
                self.path.append(copy_path)

            if ((x, y + self.block_size) not in self.walls) and y < 544 and (x, y) not in self.expanded_nodes:
                copy_path = deepcopy(required_path)
                copy_path.append((x, y + self.block_size))
                self.path.append(copy_path)

            if ((x, y - self.block_size) not in self.walls) and y > 0 and (x, y) not in self.expanded_nodes:
                copy_path = deepcopy(required_path)
                copy_path.append((x, y - self.block_size))
                self.path.append(copy_path)

        self.expanded_nodes.append((x, y))

    def pathCost(self, path):  # f(n) = h(n) + g(n)
        x1 = path[-1][0]
        x2 = self.destination_coordinates[0]
        y1 = path[-1][1]
        y2 = self.destination_coordinates[1]
        return self.path_cost * (len(path) - 1) + (math.fabs(x1 - x2) + math.fabs(y1 - y2))

        # The heuristic chosen is the Manhattan distance because we don't traverse diagonally
        # otherwise change it to math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)) -> Euclidean distance

    def sort(self):
        for i in range(len(self.path) - 1):
            for j in range(len(self.path) - i - 1):
                try:
                    if self.pathCost(self.path[j]) < self.pathCost(self.path[j + 1]):
                        temp = deepcopy(self.path[j])
                        self.path[j] = deepcopy(self.path[j + 1])
                        self.path[j + 1] = deepcopy(temp)

                    """elif self.pathCost(self.path[j]) == self.pathCost(self.path[j + 1]):
                        rand = random.random()
                        if rand > 0.5:
                            temp = deepcopy(self.path[j])
                            self.path[j] = deepcopy(self.path[j + 1])
                            self.path[j + 1] = deepcopy(temp)
                        else:
                            continue
                            
                        The above block of code can be used to get a random optimal path which has the same path value
                        as the optimal path found without this block of code.
                    """
                except:
                    pass

    def clear(self):
        self.clear_button.x = 700
        self.clear_button.y = 700
        self.search = False
        self.draw_wall = False
        self.found_path = False
        self.start = False
        self.start_coordinates = (0, 0)
        self.destination = False
        self.failed = False
        self.destination_coordinates = (0, 0)
        self.walls = []
        self.optimal_path = []
        self.expanded_nodes = []
        self.path = []


g = Grid()
