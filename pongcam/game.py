import sys
import cv2, cv
import numpy as np
import pyglet
from pyglet.gl import *
import graphics
import tracking
import camera

class Ball(object):
    def __init__(self, win_width, win_height, batch):
        self.win_width = win_width
        self.win_height = win_height

        # Create sprite
        ball_image = pyglet.image.load('images/ball.png')
        ball_image.anchor_x = 0
        ball_image.anchor_y = 0
        self.ball = pyglet.sprite.Sprite(ball_image, x=0, y=0, batch = batch)
        self.ball.scale = .3

        # Position / movement / collision information
        self.velocity = np.array([500,500])

    def update(self, dt):
        self.ball.x += self.velocity[0] * dt
        self.ball.y += self.velocity[1] * dt

        bottom = self.ball.y
        top = bottom + self.ball.height
        left = self.ball.x
        right = left + self.ball.width

        # Left right collision
        if left < 0:
            self.velocity[0] = abs(self.velocity[0])
        elif right > self.win_width:
            self.velocity[0] = -abs(self.velocity[0])

        # Top bottom collision
        if bottom < 0:
            self.velocity[1] = abs(self.velocity[1])
        elif top > self.win_height:
            self.velocity[1] = -abs(self.velocity[1])

    def draw(self):
        self.ball.draw()

class Paddle(object):
    def __init__(self, win_width, win_height, batch):
        # Create sprite
        paddle_image = pyglet.image.load('images/paddle.png')
        paddle_image.anchor_x = 0
        paddle_image.anchor_y = 100
        self.paddle = pyglet.sprite.Sprite(paddle_image, x=self.width-25, y=0, batch=batch)
        self.paddle.scale = .5

class GameWindow(pyglet.window.Window):
    def __init__(self):
        super(GameWindow, self).__init__(resizable=True)

        # Place holder until webcam feed starts
        self.current_frame = np.zeros((self.height,self.width,3), dtype=np.uint8)

        self.cam = camera.Camera()

        # Display debug image or webcam feed?
        self.debug = False

        # Image processing / ball tracking
        self.tracker = tracking.ThresholdTracker()
        #self.tracker = tracking.ColorTracker()
        #self.tracker = tracking.BackProjectTracker()
        #self.tracker = tracking.NormalizeRGB()

        # Game items
        self.batch = pyglet.graphics.Batch()
        self.selection = graphics.PygletRect()

        self.centroid = graphics.PygletRect(style='fill')

        paddle_image = pyglet.image.load('images/paddle.png')
        paddle_image.anchor_x = 0
        paddle_image.anchor_y = 100
        self.paddle = pyglet.sprite.Sprite(paddle_image, x=self.width-25, y=0, batch=self.batch)
        self.paddle.scale = .5
        self.ball = Ball(self.width, self.height, self.batch)

        #ball_image = pyglet.image.load('images/

    def on_draw(self):
        if self.debug:
            out = self.tracker.view()
        else:
            out = self.current_frame
            out = cv2.cvtColor(out, cv.CV_BGR2RGB)

        out = graphics.cv2pyglet(out)
        out.blit(0, 0, width=self.width, height=self.height)
        #self.clear()

        self.centroid.draw()
        self.selection.draw()
        self.batch.draw()

    def update(self, dt):
        # Grab image
        capture = self.cam.click()

        loc = self.tracker.track(capture)

        if loc != None:
            x,y = loc
            self.centroid.setrect(x-5,y-5,10,10)
            # TODO: Set to window width
            self.paddle.y = y

        self.current_frame = capture / 5
        self.ball.update(dt)

    def on_mouse_press(self, x, y, button, modifiers):
        self.selection.p1(x,y)
        self.selection.p2(x,y)

    def on_mouse_release(self, x, y, button, modifiers):
        x,y,w,h = self.selection.getrect()
        print x,y,w,h
        #pic = self.current_frame[ y:y+h,x:x+w]
        self.tracker.train(self.selection.getrect())
        #minbound, maxbound = learn_hist(pic)
        #cv2.imwrite("debug.jpg", pic)
        self.selection.p1(0,0)
        self.selection.p2(0,0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.selection.p2(x,y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.W:
            self.debug = not self.debug
        elif symbol == pyglet.window.key.S:
            # Start game
            pass

    def on_resize(self, width, height):
        # Boilerplate I don't understand
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
