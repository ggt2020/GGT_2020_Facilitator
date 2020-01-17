from matplotlib.patches import Rectangle
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
from random import randint
import matplotlib.pyplot as plt

class Brick(Rectangle):
    def __init__(self, xy, width, height, angle=0.0, **kwargs):
        Rectangle.__init__(self, xy, width, height, angle=0.0, **kwargs)

class Racket(Rectangle):
    def __init__(self, xy, width, height, angle=0.0, **kwargs):
        Rectangle.__init__(self, xy, width, height, angle=0.0, **kwargs)
        
    def move(self, offset):
        # Racket only moves horizontally
        self.set_x(self.get_x() + offset)

class Ball(Circle):
    def __init__(self, xy, radius, **kwargs):
        Circle.__init__(self, xy, radius, **kwargs)
        self.speed = (0,0)
        
    def hit_wall_sides(self, game):
        # check if the ball hits the left/ right wall
        if self.get_center()[0] - self.get_radius() < 0:
            return True
        elif self.get_center()[0] + self.get_radius() > game.width:
            return True
        return False
        
    def hit_wall_top(self, game):
        # check if the ball hits the top
        if self.get_center()[1] + self.get_radius() > game.height:
            return True
        return False
        
    def hit_racket(self, game):
        # check if the ball hits the racket
        if self.speed[1] < -1:
            ball_bottom = self.get_center()[1] - self.get_radius()
            racket_bottom = game.racket.get_y()
            racket_top = racket_bottom + game.racket.get_height()
        
            if ball_bottom >= racket_bottom and ball_bottom <= racket_top:
                ball_right = self.get_center()[0] + self.get_radius()
                ball_left = self.get_center()[0] - self.get_radius()
                
                racket_left = game.racket.get_x()
                racket_right = game.racket.get_x() + game.racket_width
                
                if ball_right >= racket_left and ball_left <= racket_right:
                    return True
            return False
        
    def hit_bottom(self, game):
        # check if the ball hits the bottom
        if self.get_center()[1] - self.get_radius() <= 0:
            return True
        return False
    
    def circle_in_rect(self, point, rect):
        if point[0] + self.get_radius() >= rect.get_x() and point[0] - self.get_radius() <= rect.get_x() + rect.get_width() and \
           point[1] + self.get_radius() >= rect.get_y() and point[1] - self.get_radius() <= rect.get_y() + rect.get_height():
            return True

    def circle_in_rect_vertical_bounds(self, point, rect):
        if point[1] + self.get_radius() >= rect.get_y() and point[1] - self.get_radius() <= rect.get_y() + rect.get_height():
            return True
    
    def hit_brick(self, brick):
        if not self.circle_in_rect(self.get_center(), brick):
            return 0
            
        prev_center = (self.get_center()[0] - self.speed[0], self.get_center()[1] - self.speed[1])
        if brick.get_visible() and self.circle_in_rect_vertical_bounds(prev_center, brick) :
            return 1 # hit brick side
        return 2
        
    def end_game(self, game):
        self.set_visible(False)
        for b in game.bricks:
            b.set_visible(False)
        game.bricks.clear()
        game.racket.set_visible(False)
        game.state = 'Off'
   
    def on_speed_change(self):
        # set the center of the ball when its speed changes
        new_center = (self.get_center()[0] + self.speed[0], self.get_center()[1] + self.speed[1])
        self.set_center(new_center)
        
    def toggle_dir_y(self):
        # toggle the y direction of the ball
        self.speed = (self.speed[0], self.speed[1] * -1)
    
    def move(self, game):
        self.on_speed_change()
        # check if ball hits the wall or the racket
        # and act accordingly
        if self.hit_wall_sides(game):
            self.speed = (self.speed[0] * -1, self.speed[1])
            self.on_speed_change()
        elif self.hit_wall_top(game):
            self.toggle_dir_y()
            self.on_speed_change()
        elif self.hit_racket(game):
            self.toggle_dir_y()
            self.on_speed_change()
        elif self.hit_bottom(game):
            self.end_game(game)
        else:
            for b in game.bricks:
                if not b.get_visible():
                    continue
                ret = self.hit_brick(b)
                if ret != 0:
                    b.set_visible(False)
                    if ret == 1:
                        self.speed = (self.speed[0] * -1, self.speed[1])
                        self.on_speed_change()
                    if ret == 2:
                        self.toggle_dir_y()
                        self.on_speed_change()
                    break
                    
        
class Game():
    def animate(self,i):
        self.ball.move(self)
        self.fig.canvas.draw()
    
    def create_bricks(self):
        for i in range(1,randint(4, 6)):
            numBricksInRow = randint(1,8)
            x = self.width / 2 - numBricksInRow * (self.brick_width + self.margin * 3) / 2 + self.margin * 3
            y = self.height - self.height / 12 * i
            for j in range(numBricksInRow):
                brick = Brick((x, y), self.brick_width, self.brick_height, color='yellow')
                self.gamePlot.add_patch(brick)
                self.bricks.append(brick)
                x += (self.brick_width + self.margin * 3)
    
    def start_game(self):
        # create bricks
        if len(self.bricks) == 0:
            self.create_bricks()
            # make racket visible
            self.racket.set_visible(True)
        # create a ball
        self.gamePlot.set_visible(True)
        self.ball = Ball((randint(1, 1000), 100), 10)
        self.ball.speed = (-(randint(5, 8)),randint(5, 8))  
        self.gamePlot.add_patch(self.ball)
        anim = FuncAnimation(self.fig, self.animate, frames=10000000000,interval=25)
        self.fig.canvas.draw()
        self.state = 'Running'
            
    def resume_game(self):
        self.ball.speed = self.prev_speed
        self.state = 'Running'
    
    def pause_game(self):
        self.prev_speed = self.ball.speed
        self.ball.speed = (0, 0);
        self.state = 'Paused'

    def racket_move(self, offset):
        offset = offset * self.move_unit
        new_x = self.racket.get_x() + offset
        
        if new_x < 0:
            new_x = 0
        elif new_x > self.width - self.racket_width:
            new_x = self.width - self.racket_width
            
        self.racket.set_x(new_x)
        self.fig.canvas.draw()
            
    def press(self, event):
        if event.key == 'enter':
            if self.state == 'Off':
                self.start_game()
            elif self.state == 'Running':
                self.pause_game()
            elif self.state == 'Paused':
                self.resume_game()
        elif event.key == 'left':
            self.racket_move(-1)
        elif event.key == 'right':
            self.racket_move(1)
        elif event.key == 'up':
            self.ball.speed = (self.ball.speed[0] * 1.1, self.ball.speed[1] * 1.1)
        elif event.key == 'down':
            self.ball.speed = (self.ball.speed[0] * 0.9, self.ball.speed[1] * 0.9)

    def __init__(self):
        self.state = 'Off'
    
        self.fig = plt.figure(figsize=(6, 6))
        self.gamePlot = self.fig.add_subplot(111)
        self.gamePlot.axis('OFF')
        
        # declare canvas size
        self.margin = 10
        self.width = 1000
        self.height = 1000
        
        ggt_title = 'Girls Go Tech 2020'
        
        # put text in the middle of the canvas
        self.gamePlot.text(0.5*self.width, self.height + 20, ggt_title, 
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=10, color='black')
        
        # create white background with black edge
        background_rect = Rectangle((0, 0), self.width, self.height, color='white')
        background_rect.set_edgecolor('black')
        self.gamePlot.add_patch(background_rect)
        
        # create bricks
        self.brick_width = 80
        self.brick_height = 40
        self.bricks = []
        self.create_bricks()
        
        # create racket
        self.racket_width = self.brick_width + 10
        self.racket_height = self.brick_height / 2
        self.move_unit = 10
        self.racket_pos_y = 20
        self.racket = Racket((self.width / 2 - self.racket_width / 2, self.racket_pos_y), self.racket_width, self.racket_height, color='blue')
        self.gamePlot.add_patch(self.racket)
        
        self.gamePlot.set_xlim(0,self.width + self.margin)
        self.gamePlot.set_ylim(-self.margin, self.height)
        
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        
    def draw(self):
        plt.show()
        
if __name__ == "__main__":
    game = Game()
    game.draw()
