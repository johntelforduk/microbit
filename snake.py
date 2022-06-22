from microbit import *
import random
import music

heartbeat = 50  # Number of miliseconds between each heartbeat.
edge_x, edge_y = 4, 4


class Snake:
    def __init__(self):

        self.speed = 4.0  # Do this many moves per second.
        self.wait = 1000 / self.speed  # How many ms before next step.

        self.segments = [(2, 2)]  # Start with just a head segment.

        # 0 = East, 1 = South, 2 = West, 3 = North.
        self.direction = random.randrange(4)

        self.eaten_egg = False
        self.eaten_itself = False

        self.deltas = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def head(self):
        return self.segments[-1]

    def render(self):
        # Skip last element of list (which is the head).
        for (x, y) in self.segments[:-1]:
            display.set_pixel(x, y, 7)
        # Set the head to max brightness.
        head_x, head_y = self.head()
        display.set_pixel(head_x, head_y, 9)

    def move(self):
        if button_a.was_pressed():
            self.anti_clockwise()
        if button_b.was_pressed():
            self.clockwise()

        head_x, head_y = self.head()

        # Check for head in corners.
        if (head_x, head_y) == (edge_x, 0):
            self.direction = 1
        elif (head_x, head_y) == (edge_x, edge_y):
            self.direction = 2
        elif (head_x, head_y) == (0, edge_y):
            self.direction = 3
        elif (head_x, head_y) == (0, 0):
            self.direction = 0

        elif head_x == edge_x and self.direction == 0:
            self.direction = 1
        elif head_y == edge_y and self.direction == 1:
            self.direction = 2
        elif head_x == 0 and self.direction == 2:
            self.direction = 3
        elif head_y == 0 and self.direction == 3:
            self.direction = 0

        dx, dy = self.deltas[self.direction]

        self.segments.append((head_x + dx, head_y + dy))
        if self.eaten_egg:
            self.eaten_egg = False
        else:
            del self.segments[0]
        self.check_eaten_itself()

    def check_eaten_itself(self):
        if self.segments.index(self.head()) != len(self.segments) - 1:
            self.eaten_itself = True

    def clockwise(self):
        self.direction = (self.direction + 1) % 4

    def anti_clockwise(self):
        self.direction = (self.direction - 1) % 4

    def tick(self):
        if self.wait <= 0:
            self.move()
            self.wait = 1000 / self.speed
        else:
            self.wait -= heartbeat


class Egg:
    def __init__(self):
        self.x = random.randrange(5)  # Between 0 and 4.
        self.y = random.randrange(5)

        self.brightness = 9.0
        self.steps = 20  # Number of steps in an eggs lifecycle.
        self.speed = 1.0  # seconds to go from dull to bright and back again.
        self.phase = "wane"

    def tick(self):
        if self.phase == "wane":
            self.brightness -= self.speed * heartbeat * self.steps / 1000
        else:
            self.brightness += self.speed * heartbeat * self.steps / 1000

        if self.brightness <= 0:
            self.phase = "wax"
            self.brightness = 0
        if self.brightness >= 9.0:
            self.phase = "wane"
            self.brightness = 9

    def render(self):
        display.set_pixel(self.x, self.y, int(self.brightness))


while True:
    snake = Snake()
    egg = Egg()

    while snake.eaten_itself is False:
        display.clear()
        snake.render()
        egg.render()

        if snake.head() == (egg.x, egg.y):
            snake.eaten_egg = True
            del egg
            egg = Egg()
            music.play(["C6:1"])

        snake.tick()
        egg.tick()
        sleep(heartbeat)

    while button_a.was_pressed() is False:
        display.scroll(str(len(snake.segments)))
        sleep(1000)

    del snake
    del egg
