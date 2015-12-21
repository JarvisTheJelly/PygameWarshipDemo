import pygame
from vector2 import Vector2 as vec2
import random

class particle:
    
    def __init__(self, life, pos, vel, gravity=False):
        self.life = 0
        self.lifespan = life
        self.colLifespan = .25
        self.maxLifespan = life
        self.pos = pos
        self.vel = vel
        self.gravity = gravity #If the particle is affected by gravity
        self.col1 = (255,140,0)
        self.col2 = (20,20,20)
        self.maxSize = 32
        self.grow = False
        
    def lerp(self, col1, col2, a):
        return col1 + (col2-col1)*a
    
    def lerpCol(self, col1, col2, a):
        r = self.lerp(col1[0], col2[0],a)
        g = self.lerp(col1[1], col2[1],a)
        b = self.lerp(col1[2], col2[2],a)
        return (r,g,b)
    
    def varyCol(self, col):
        offset = random.randint(-10,10)
        r = col[0]+offset
        g = col[1]+offset
        b = col[2]+offset
        return self.fixCol((r,g,b))
    
    def fixCol(self, col):
        r = max(0, min(255,col[0]))
        g = max(0, min(255,col[1]))
        b = max(0, min(255,col[2]))
        return (r,g,b)
    
    def update(self, delta):
        self.pos+=self.vel*delta
        #self.lifespan-=delta
        self.life+=delta
        ratio = min(self.life/self.colLifespan,1)
        self.size = -(self.life/self.lifespan)*self.maxSize+self.maxSize
        if self.grow:
            self.size = -abs(((self.life/self.lifespan)-.5)*2)*self.maxSize+self.maxSize
        
        self.color = self.lerpCol(self.col1, self.col2, ratio)
        
    def toInt(self, vec):
        return (int(vec.x), int(vec.y))
        
    def render(self, surface, camera):
        pygame.draw.circle(surface, self.color, self.toInt(self.pos-camera.pos), int(self.size))