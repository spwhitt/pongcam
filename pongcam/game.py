import sys
import cv2, cv
import numpy as np
import pyglet
from pyglet.gl import *
import pongcam.graphics as graphics
import pongcam.tracking as tracking
import pongcam.camera as camera


score = [0,0]
aispeed = 10

def collision(obj1, obj2):
    """Detect a collision between two objects by looking at their bounds"""
    (top1, right1, bottom1, left1) = obj1.bounds()
    (top2, right2, bottom2, left2) = obj2.bounds()

    return bottom1 <= top2 and top1 >= bottom2 and (left2 <= right1 <= right2 or left2 <= left1 <= right2)

class Ball(object):
    def __init__(self, win_width, win_height, paddle1, paddle2, batch):
        self.win_width = win_width
        self.win_height = win_height
        self.paddle1 = paddle1
        self.paddle2 = paddle2

        # Create sprite
        ball_image = pyglet.image.load('images/ball.png')
        #ball_image = resource_stream(__name__, 'images/ball.png');
        ball_image.anchor_x = ball_image.width/2
        ball_image.anchor_y = ball_image.height/2
        self.ball = pyglet.sprite.Sprite(ball_image, batch = batch)
        self.ball.scale = .3

        self.bounceSound = pyglet.media.load('./sounds/kick.wav', streaming=False)
        self.dieSound = pyglet.media.load('./sounds/sadwhistle.wav', streaming=False)
        self.scoreSound = pyglet.media.load('./sounds/crash.wav', streaming=False)

        self.start()


    def start(self):
        """Send the ball back to its starting location and configuration"""
        self.spin = 10
        self.ball.x = self.win_width/2
        self.ball.y = self.win_height/2
        self.velocity = np.array([-400,400])

    def right_paddle(self):
        """Bounce off the right paddle"""
        self.velocity[0] = -abs(self.velocity[0])

    def left_paddle(self):
        """Bounce off the left paddle"""
        self.velocity[0] = abs(self.velocity[0])

    def pos(self):
        """Get the ball position"""
        return (self.ball.x, self.ball.y)

    def bounds(self):
        """Get the ball boundaries"""
        xoff = self.ball.width/2
        yoff = self.ball.height/2
        bottom = self.ball.y - yoff
        top = self.ball.y + yoff
        left = self.ball.x - xoff
        right = self.ball.x + xoff
        return (top, right, bottom, left)

    def update(self, dt):
        global score, aispeed
        # Accelerate by spin
        self.velocity[1] += self.spin

        # Increment ball position
        self.ball.x += self.velocity[0] * dt
        self.ball.y += self.velocity[1] * dt
        self.ball.rotation += self.spin

        (top, right, bottom, left) = self.bounds()

        # Check collision
        if collision(self, self.paddle1):
            self.right_paddle()
            self.spin = self.spin/2 - self.paddle1.velocity/2
            self.bounceSound.play()
        elif collision(self, self.paddle2):
            self.left_paddle()
            self.spin = self.spin/2 + self.paddle2.velocity/2
            self.bounceSound.play()

        # Check out of bounds
        # Left right collision
        if left < 0:
            self.scoreSound.play()
            score[1]+=1;
            self.start()
            aispeed+=1
        elif right > self.win_width:
            self.dieSound.play()
            score[0]+=1;
            self.start()
            aispeed-=1

        # Top bottom collision
        if bottom < 0:
            self.velocity[1] = abs(self.velocity[1])
            self.bounceSound.play()
        elif top > self.win_height:
            self.velocity[1] = -abs(self.velocity[1])
            self.bounceSound.play()

    def draw(self):
        self.ball.draw()

class Paddle(object):
    def __init__(self, xpos, batch, flipimg=False):
        self.x = xpos
        self.y = 0
        self.velocity = 0
        # Create sprite
        paddle_image = pyglet.image.load('images/paddle.png')

        if flipimg:
            t = paddle_image.texture.tex_coords
            paddle_image.texture.tex_coords = t[3:6] + t[:3] + t[9:] + t[6:9]

        #paddle_image = resource_stream(__name__, 'images/paddle.png');
        #paddle_image.anchor_x = 0
        #paddle_image.anchor_y = 100
        self.paddle = pyglet.sprite.Sprite(paddle_image, x=self.x, y=self.y, batch=batch)
        self.paddle.scale = .7

    def move(self, y, dt):
        """Moves the paddle to the given y coordinate"""

        # Velocity, used to put spin on the ball
        self.velocity = y - self.y

        # Update position
        self.y = y

        # Offset by 50 to make the paddle centered on the pointer
        self.paddle.y = y-self.paddle.height/2

    def ai(self, y):
        # If we're moving down...
        if y - self.y < 0:
            self.move(self.y-aispeed, 0)
        else:
            self.move(self.y+aispeed,0)

    def bounds(self):
        """Get the ball boundaries"""
        bottom = self.paddle.y
        top = bottom + self.paddle.height
        left = self.paddle.x
        right = left + self.paddle.width
        return (top, right, bottom, left)
    
class GameWindow(pyglet.window.Window):
    def __init__(self):
        super(GameWindow, self).__init__(resizable=True)

        # Is the game started?
        self.game = False

        # Place holder until webcam feed starts
        self.current_frame = np.zeros((self.height,self.width,3), dtype=np.uint8)

        # Connect to camera
        self.cam = camera.Camera()

        # Display debug image or webcam feed?
        self.debug = False

        # Image processing / ball tracking
        #self.tracker = tracking.ThresholdTracker()
        #self.tracker = tracking.ColorTracker()
        self.tracker = tracking.BackProjectTracker()
        #self.tracker = tracking.NormalizeRGB()

        # All the sprites
        self.batch = pyglet.graphics.Batch()
        # The rectangle which is drawn when you click and drag
        self.selection = graphics.PygletRect()
        # The location the tracker has detected
        self.centroid = graphics.PygletRect(style='fill')

        # The game objects
        self.paddle1 = Paddle(self.width-25, self.batch)
        self.paddle2 = Paddle(5, self.batch, flipimg=True)
        self.ball = Ball(self.width, self.height, self.paddle1, self.paddle2, self.batch)

        # Text
        self.starttext = pyglet.text.Label("Press 's' to start.",
                                font_name='Times New Roman',
                                font_size=40,
                                x=20, y=self.height-60)

        self.p1score = pyglet.text.Label("P1",
                                font_name='Times New Roman',
                                font_size=40,
                                x=20, y=self.height-60)

        self.p2score = pyglet.text.Label("P2",
                                font_name='Times New Roman',
                                font_size=40,
                                x=self.width-60, y=self.height-60)



    def on_draw(self):
        # Figure out which webcam image to display
        if self.debug:
            out = self.tracker.view()
        else:
            out = self.current_frame
            out = cv2.cvtColor(out, cv.CV_BGR2RGB)

        # Display the webcam image on the screen
        out = graphics.cv2pyglet(out)
        out.blit(0, 0, width=self.width, height=self.height)

        # Draw everything else
        self.centroid.draw()
        self.selection.draw()
        self.batch.draw()

        # Texual feedback
        if self.game:
            self.p1score.draw()
            self.p2score.draw()
        else:
            self.starttext.draw()

    def update(self, dt):
        self.p1score.text = str(score[0])
        self.p2score.text = str(score[1])
        # Grab image
        capture = self.cam.click()

        loc = self.tracker.track(capture)

        if loc != None:
            x,y = loc
            # Draw a centroid at loc
            self.centroid.setrect(x-5,y-5,10,10)
            # Move the paddle to loc
            self.paddle1.move(y, dt)

        # Dim the screen
        self.current_frame = capture

        if self.game:
            # Move the ball
            self.ball.update(dt)
            # The computer player simpily tracks the ball's y coordinate
            x,y = self.ball.pos()
            self.paddle2.ai(y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.selection.p1(x,y)
        self.selection.p2(x,y)

    def on_mouse_release(self, x, y, button, modifiers):
        x,y,w,h = self.selection.getrect()
        self.tracker.train(self.selection.getrect())
        self.selection.p1(0,0)
        self.selection.p2(0,0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.selection.p2(x,y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.D:
            self.debug = not self.debug
        elif symbol == pyglet.window.key.S:
            self.game = True
        elif symbol == pyglet.window.key.P:
            self.game = False
        elif symbol == pyglet.window.key.N:
            global score
            # Stop game
            self.game = False
            # Reset score
            score = [0,0]
            # Send ball back to start
            self.ball.start()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        # Reposition paddle
        #self.paddle.x = width - 25

        # Change scale factors
        scalex = width / float(self.cam.width)
        scaley = height / float(self.cam.height)
        #glScalef(scalex, scaley, 1);


def run():
    window = GameWindow()
    pyglet.clock.schedule_interval(window.update, 1/30.0)
    #pyglet.clock.set_fps_limit(30)
    pyglet.app.run()
    window.cam.done()

if __name__ == "__main__":
    run()
