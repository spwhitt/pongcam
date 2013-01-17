# Pongcam

This game allows you to play pong with your webcam. You control your paddle by waving a colored object in front of the camera. You can put spin on the ball by moving your paddle rapidly just as the ball hits it.

I don't have time to polish it, so it is very rough around the edges, but still fun.

Installation and running
-------------------------

In order for pyglet to play sounds, you must install libav:

    sudo apt-get install libavbin0

Of course, don't forget opencv:
    
    sudo apt-get install python-opencv

Once everything is installed, simply run:
    
    ./bin/pongcam

Gameplay
---------

1. Select a region of the screen with your mouse to train the color tracker
2. To start the game, press s
3. To pause the game, press p
4. To end the game and start a new one, press n
5. To toggle the color tracker's debug screen, press d

Media
-----
All sounds are Creative Commons licensed, from FreeSound.org
http://www.freesound.org/people/Matias.Reccius/sounds/50985/
http://www.freesound.org/people/Splashdust/sounds/84327/
http://www.freesound.org/people/TicTacShutUp/sounds/428/

The ball image is from http://commons.wikimedia.org/wiki/File:Pok%C3%A9_Ball.svg
