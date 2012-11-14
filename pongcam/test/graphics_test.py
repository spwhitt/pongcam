import unittest
import graphics

class GraphicsTest(unittest.TestCase):
    def setUp(self):
        self.rect = graphics.PygletRect()

    def testSetRect(self):
        rect = (400,221,12,243)
        self.rect.setrect(*rect)
        self.assertEqual(self.rect.getrect(), rect)

    def testSetP1P2(self):
        self.rect.p1(20,10)
        self.rect.p2(40,90)
        w = 40-20
        h = 90-10
        self.assertEqual(self.rect.getrect(), (20,10,w,h))

    def testNegativeWidth(self):
        rect = (20,40,-200,200)
        self.rect.setrect(*rect)
        self.assertEqual(self.rect.getrect(), rect)

if __name__ == "__main__":
    unittest.main()
