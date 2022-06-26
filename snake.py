# Snake.
# June 2022.

import microbit
import random
import music

heartbeat = 50  # Number of milliseconds between each heartbeat.
edge_x, edge_y = 4, 4  # Edges of the screen.


class Snake:
    def __init__(self):

        self.speed = 4.0  # Do this many moves per second.
        self.wait = 1000 / self.speed  # How many ms before next step.

        self.segments = [(2, 2)]  # Start with just a head segment.

        # 0 = East, 1 = South, 2 = West, 3 = North.
        self.deltas = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.direction = random.randrange(4)

        self.eaten_egg = False
        self.dead = False

    @staticmethod
    def clockwise(d: int) -> int:
        return (d + 1) % 4

    @staticmethod
    def anti_clockwise(d: int) -> int:
        return (d - 1) % 4

    def head(self):
        """Return coords of the head of the snake."""
        # Last item in the segment list is the head of the snake.
        return self.segments[-1]

    @staticmethod
    def in_grid(x: int, y: int) -> bool:
        """Return True if the parm coords are in the game grid. False otherwise."""
        return 0 <= x <= edge_x and 0 <= y <= edge_y

    def next(self, x: int, y: int, d: int) -> (int, int):
        """Return coords of next move for parm coords and direction."""
        dx, dy = self.deltas[d]
        return x + dx, y + dy

    def eaten_itself(self, x: int, y: int) -> bool:
        if (x, y) not in self.segments:
            return False
        if self.segments.index((x, y)) == len(self.segments) - 1:
            return False
        return True

    def render(self, f):
        """Draw the snake on the parm image frame."""
        # Set the head to max brightness.
        x, y = self.head()
        f.set_pixel(x, y, 9)

        # Skip the last element of list (which is the head).
        # Make the body of the snake a little less bright than the head.
        for (x, y) in self.segments[:-1]:
            frame.set_pixel(x, y, 7)

    def move(self):
        if microbit.button_a.was_pressed():
            self.direction = self.anti_clockwise(self.direction)
        if microbit.button_b.was_pressed():
            self.direction = self.clockwise(self.direction)
        # First, try heading straight ahead.
        x, y = self.head()
        d = self.direction
        px, py = self.next(x, y, d)

        # If that's no good...
        if not self.in_grid(px, py) or self.eaten_itself(x, y):
            # ... next, find out what Clockwise is like.
            d_cw = self.clockwise(d)
            x_cw, y_cw = self.next(x, y, d_cw)

            if not self.in_grid(x_cw, y_cw) or self.eaten_itself(x_cw, y_cw):
                # If still no good, try anticlockwise.
                d_acw = self.anti_clockwise(d)
                x_acw, y_acw = self.next(x, y, d_acw)

                if not self.in_grid(x_acw, y_acw) or self.eaten_itself(x_acw, y_acw):
                    # If still no good, then we're dead :(
                    self.dead = True
                else:
                    x, y, self.direction = x_acw, y_acw, d_acw
            else:
                x, y, self.direction = x_cw, y_cw, d_cw
        else:
            x, y = px, py

        if self.dead is False:
            self.segments.append((x, y))
            if self.eaten_egg:
                self.eaten_egg = False
            else:
                del self.segments[0]

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

    def render(self, f):
        f.set_pixel(self.x, self.y, int(self.brightness))


while True:
    snake = Snake()
    egg = Egg()

    while snake.dead is False:
        frame = microbit.Image()
        snake.render(frame)
        egg.render(frame)
        microbit.display.show(frame)

        if snake.head() == (egg.x, egg.y):
            snake.eaten_egg = True
            del egg
            egg = Egg()
            music.play(["C6:1"])

        snake.tick()
        egg.tick()
        microbit.sleep(heartbeat)

    music.play(music.POWER_DOWN)
    while microbit.button_a.was_pressed() is False:
        microbit.display.scroll(str(len(snake.segments)))
        microbit.sleep(1000)

    del snake
    del egg
