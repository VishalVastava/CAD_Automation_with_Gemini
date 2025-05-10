import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Set up camera perspective
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -20)

# Room dimensions (scale to match the original code)
rooms = {
    "living_room": (5, 4, 3),  # width, height, depth (in meters)
    "bedroom1": (3.5, 3, 3),
    "bedroom2": (3.5, 3, 3),
    "kitchen": (5, 3, 3),
    "bathroom1": (1.5, 2, 3),
    "bathroom2": (1.5, 2, 3),
}

# Coordinates for the rooms
room_positions = {
    "living_room": (0, 0),
    "bedroom1": (5, 0),
    "bedroom2": (5, 4),
    "kitchen": (0, 4),
    "bathroom1": (8, 0),
    "bathroom2": (8, 4),
}

# Function to draw a cuboid (room)
def draw_cuboid(x, y, width, height, depth):
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(x, y, 0)
    glVertex3f(x + width, y, 0)
    glVertex3f(x + width, y + height, 0)
    glVertex3f(x, y + height, 0)
    
    # Back face
    glVertex3f(x, y, depth)
    glVertex3f(x + width, y, depth)
    glVertex3f(x + width, y + height, depth)
    glVertex3f(x, y + height, depth)
    
    # Left face
    glVertex3f(x, y, 0)
    glVertex3f(x, y, depth)
    glVertex3f(x, y + height, depth)
    glVertex3f(x, y + height, 0)
    
    # Right face
    glVertex3f(x + width, y, 0)
    glVertex3f(x + width, y, depth)
    glVertex3f(x + width, y + height, depth)
    glVertex3f(x + width, y + height, 0)
    
    # Top face
    glVertex3f(x, y + height, 0)
    glVertex3f(x + width, y + height, 0)
    glVertex3f(x + width, y + height, depth)
    glVertex3f(x, y + height, depth)
    
    # Bottom face
    glVertex3f(x, y, 0)
    glVertex3f(x + width, y, 0)
    glVertex3f(x + width, y, depth)
    glVertex3f(x, y, depth)
    
    glEnd()

# Function to add doors (simple line openings)
def draw_door(x, y, width, height, angle):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(angle, 0, 0, 1)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(width, 0, 0)
    glEnd()
    glPopMatrix()

# Main drawing function
def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Draw rooms (cuboids)
    for room, (width, height, depth) in rooms.items():
        x, y = room_positions[room]
        draw_cuboid(x, y, width, height, depth)

    # Draw doors (represented as simple lines for now)
    # Example door for living room
    draw_door(2.5, 0, 1, 0.3, 0)  # A door at the living room (center, horizontal)
    
    # More doors can be drawn based on room positions
    
    pygame.display.flip()

# Main loop to render the 3D scene
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        draw_scene()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
