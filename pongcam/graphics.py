import pyglet

def cv2pyglet(img):
    # Convert to pyglet image
    x,y,_ = img.shape
    image_data = img.data.__str__()
    return pyglet.image.ImageData(y, x, 'RGB', image_data, y*3)

class PygletRect(object):
    def __init__(self, style='stroke', fill=(255,0,0)):
        self.rect = (0,0,0,0)
        numv = 4

        if style=='stroke':
            self.style = pyglet.gl.GL_LINE_LOOP
            fill = ('c3B', fill*numv)
        elif style=='fill':
            self.style = pyglet.gl.GL_TRIANGLE_FAN
            fill = ('c3B', fill*numv)
        elif style=='texture':
            self.style = pyglet.gl.GL_LINE_LOOP
            fill = ('t2f', [0,0, 1,0, 1,1, 0,1])
        else:
            print "Unknown style in PygletRect"

        self.vlist = pyglet.graphics.vertex_list(numv,
            ('v2f', [0]*2*numv), fill)

    def getrect(self):
        return self.rect
    
    def setrect(self, x, y, w, h):
        self.rect = (x,y,w,h)
        self.update()

    def p1(self, x, y):
        _,_,w,h = self.rect
        self.rect = (x,y,w,h)
        self.update()

    def p2(self, a, b):
        x,y,_,_ = self.rect
        self.rect = (x,y,a-x,b-y)
        self.update()

    def update(self):
        x,y,w,h = self.rect
        a,b = (x,y)
        c,d = (x+w, y+h)
        self.vlist.vertices = [a,b,c,b,c,d,a,d]

    def draw(self):
        self.vlist.draw(self.style)
