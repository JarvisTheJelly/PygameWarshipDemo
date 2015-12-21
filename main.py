import pygame
import random
from Image_funcs import *

from vector2 import Vector2 as vec2
from math import cos, sin, pi, degrees,atan2, radians
import math
pygame.init()

w, h = screen_size = (1280, 720)
screen = pygame.display.set_mode(screen_size)

totalSurface = pygame.Surface((w+20, h+20))

from particle import *

pygame.mixer.init(channels=4)
pygame.font.init()

fontSml = pygame.font.Font("fonts/airborne.ttf", 12)
fontMed = pygame.font.Font("fonts/airborne.ttf", 25)
fontLrg = pygame.font.Font("fonts/airborne.ttf", 50)

fireSound1 = pygame.mixer.Sound("sounds/cannon2L.ogg")
splashSound1 = pygame.mixer.Sound("sounds/splash1.wav")

shakeTimer = 0.25
maxShakeTimer = shakeTimer

pygame.mouse.set_visible(0)

p1 = vec2(w/2, h/2)
p3 = vec2(w*.75, h/2)

img1 = pygame.image.load("images/warshipCannon.png").convert()
warshipImage = pygame.image.load("images/warshipsLarge.png").convert()

warshipImageFuncs = image_funcs(32, 32)
warshipImageCells = warshipImageFuncs.get_list(warshipImage)

warshipDestroyerImage = warshipImageFuncs.get_image(warshipImageCells, 5, 1, 0, 1, 1)
warshipDestroyerImage.set_colorkey((255, 0, 255))

warshipDestroyerShadow = warshipImageFuncs.get_image(warshipImageCells, 5, 1, 5, 1, 1)
warshipDestroyerShadow.set_colorkey((255, 0, 255))

carrierImage = warshipImageFuncs.get_image(warshipImageCells, 7, 2, 0, 3, 1)
carrierImage.set_colorkey((255, 0, 255))

carrierShadow = warshipImageFuncs.get_image(warshipImageCells, 7, 2, 7, 3, 1)
carrierShadow.set_colorkey((255, 0, 255))

red = warshipImageFuncs.get_image(warshipImageCells, 1, 1, 1, 2, 1)
red.set_colorkey((255, 0, 255))

yellow = warshipImageFuncs.get_image(warshipImageCells, 1, 1, 2, 2, 1)
yellow.set_colorkey((255, 0, 255))

green = warshipImageFuncs.get_image(warshipImageCells, 1, 1, 3, 2, 1)
green.set_colorkey((255, 0, 255))


# smaller stuff below here

warshipImageFuncs = image_funcs(16, 16)
warshipImageCells = warshipImageFuncs.get_list(warshipImage)

warshipGunImage = warshipImageFuncs.get_image(warshipImageCells, 1, 1, 0, 4, 1)
warshipGunImage.set_colorkey((255, 0, 255))

warshipGunShadow = warshipImageFuncs.get_image(warshipImageCells, 1, 1, 0, 5, 1)
warshipGunShadow.set_colorkey((255, 0, 255))

particles = []
shots = []

def elasticIn(k):
    """ This is a tweening function I was going to use for screen shake but never
        got it to work."""
    a, p = 0.1, 0.4
    if k == 0:
        return 0
    if k == 1:
        return 1
    if not a or a < 1:
        a = 1;
        s = p/4
    else:
        s = p*math.asin(1/a)/(2*math.pi)
    
    return - (a * math.pow(2, 10 * (k - 1)) * math.sin((k - s) * (2 * math.pi) / p))

def shake(k):
    """I ended up just using random movements for screen shake (which looks bad)."""
    try:
        if k == 0:
            return vec2(-10, -10)
        if k == 1:
            return vec2(random.randint(-20, 0), random.randint(-20, 0))
        else:
            return vec2(random.randint(-10 - int(10 * k), 0 - int(10 * k)),
                        random.randint(-10 - int(10 * k), 0 - int(10 * k)))
    except ValueError:
        print k

class test:
    """ This is my code for getting something to rotate AROUND a point. This is what the
        WHOLE program was created for."""
    def __init__(self, image, center, radius):
        self.pos = vec2(*center)
        
        self.img = pygame.Surface(image.get_size())
        self.img.set_colorkey((255, 0, 255))
        self.img.blit(image, (0, 0))

        self.rect = self.img.get_rect()
        # pygame.draw.rect(self.img, (128,128,128), self.rect)
        
        self.center = center
        self.radius = radius
        
        self.newImg = self.img
        self.angle = 0
        
    def update(self, pos, rotateImg = True, angle=None):
        
        if rotateImg:
            if angle is None:
                rise = pos.x - self.pos.x
                run = pos.y - self.pos.y
            
                self.angle = atan2(rise, run)
            else:
                self.angle = angle
            
            self.newImg = pygame.transform.rotate(self.img, degrees(self.angle))
        
        self.rect = self.newImg.get_rect()
            
        self.pos = vec2(self.center.x + sin(self.angle)*self.radius, self.center.y + cos(self.angle)*self.radius)
        self.rect.center = self.pos
            
    def render(self, surface, camera):
        temp_rect = self.rect
        temp_rect.center -= camera.pos
        surface.blit(self.newImg, temp_rect)


class gun:
    """Basically same code as above but tweaked and improved a bit."""

    def __init__(self, image, center, radius, warship, shadow=False):
        self.center = center
        self.radius = radius
        
        self.warship = warship
        self.warship.guns.append(self)
        self.angle = radians(self.warship.angle)+radians(90)

        self.imageRotater = test(image, center+vec2(sin(self.angle)*radius, cos(self.angle)*radius), 2)
        self.shadow = shadow
        
        self.reload = 0
        self.reloadMax = .5
        
    def update(self, pos, tp, angle=None):

        if self.reload >= 0:
            self.reload -= tp
            
        self.angle = radians(self.warship.angle)+radians(90)
        self.center = self.warship.normal_pos.copy()
        if self.shadow:
            self.center.y +=1
        self.imageRotater.center = self.center+vec2(sin(self.angle)*self.radius, cos(self.angle)*self.radius)
        self.imageRotater.update(pos, angle=angle)
        self.img = pygame.Surface(self.imageRotater.newImg.get_size())
        self.img.blit(self.imageRotater.newImg, (0,0))
        self.img.set_colorkey((0,0,0))
        
        self.rect = self.img.get_rect()
        self.pos = vec2(self.center.x + sin(self.angle)*self.radius, self.center.y + cos(self.angle)*self.radius)
        self.rect.center = self.pos
            
    def render(self, surface, camera):
        temp_rect = self.rect
        temp_rect.center -= camera.pos
        surface.blit(self.img, temp_rect)


class smoke:
    """The particles that come out of ships after you hit them is this"""

    def __init__(self, warship, radius, angle):
        self.warship = warship
        self.center = warship.pos
        self.radius = radius
        self.angle = angle
        self.particles = []
        self.pos = self.center + vec2(sin(self.angle+radians(self.warship.angle))*self.radius, cos(self.angle+radians(self.warship.angle))*self.radius)
        
    def update(self, tp):
        #print self.angle
        self.pos = self.center + vec2(sin(self.angle+radians(self.warship.angle))*self.radius, cos(self.angle+radians(self.warship.angle))*self.radius)
        if random.randint(1,5) == 1:
            p = particle(random.uniform(1,3), self.pos, vec2(random.randint(-10,10), random.randint(-10,10)))
            p.maxSize = 16
            
            p.grow = True
            p.colLifespan = 1
            self.particles.insert(0, p)
        
        to_delete = []
        
        for PARTICLE in self.particles:
            PARTICLE.update(tp)
            if PARTICLE.life >= PARTICLE.lifespan:
                to_delete.append(PARTICLE)
                
        for PARTICLE in to_delete:
            self.particles.remove(PARTICLE)
            
    def render(self, surface, camera):
        for PARTICLE in self.particles:
            PARTICLE.render(surface, camera)


class shot:
    
    def __init__(self, pos, vel):
        self.pos = pos
        self.vel = vel
        self.past = []
        self.dead = False
        
    def update(self, tp):
        self.pos += self.vel*tp
        self.past.append(self.pos.copy())
        if len(self.past) > 50:
            self.past.pop(0)
            
        if self.pos.x < 0 or self.pos.x > 1600 or self.pos.y < 0 or self.pos.y > 900:
            self.dead = True
            
    def render(self, surface, camera):
        try:
            # pygame.draw.lines(surface, (128,128,128), False, self.past, 3)
            pass
        except ValueError:
            pass
        pygame.draw.circle(surface, (128, 128, 128), toInt(self.pos-camera.pos), 4)


class warship:
    """What you are and what you are shooting. I disabled moving for enemies."""

    def __init__(self, img, pos):
        self.img = img
        self.pos = self.normal_pos = pos
        self.rect =self.img.get_rect()
        self.rect.center = self.pos
        self.guns = []
        self.smoke = []
        self.angle = 0
        self.health = 100
        self.dead = False
        self.camera = None
        self.speed = 500
        
        self.aimAngle = 0
        self.firepower = 100
        
        self.mask = pygame.mask.from_surface(self.img)
        
    def readyToFire(self):
        for GUN in self.guns:
            if GUN.reload<=0:
                return True
        return False

    def update(self, pos, tp, rot, mov, camera):
        self.fired = False
        
        for SMOKE in self.smoke:
            SMOKE.update(tp)

        self.hitPos = self.pos + vec2(sin(radians(self.aimAngle))*self.firepower,
                                      cos(radians(self.aimAngle))*self.firepower)

        self.angle += rot*tp*45
        dxy = dx, dy = vec2(cos(radians(self.angle))*mov*tp*self.speed, sin(radians(self.angle))*-mov*tp*self.speed)
        self.normal_pos += dxy

        for GUN in self.guns:
            GUN.update(pos, tp)

        if self.camera is not None:
            self.camera.update(dx, dy)
            self.pos = self.normal_pos
        else:    
            self.pos = self.normal_pos
        
        self.newImg = pygame.transform.rotate(self.img, self.angle)
        
        self.rect = self.newImg.get_rect()
        self.rect.center = self.normal_pos
        
        self.mask = pygame.mask.from_surface(self.newImg)
        
        if self.health <= 0:
            self.dead = True
            return
        
    def fire(self, group):
        self.fired = False
        for GUN in self.guns:
            if GUN.reload <= 0:
                fireSound1.play()
                for i in range(10):
                    # The smoke that comes out when you fire
                    group.append(particle(random.uniform(2, 5),
                                          GUN.pos+vec2(sin(GUN.imageRotater.angle)*40, cos(GUN.imageRotater.angle)*40),
                                          vec2(sin(GUN.imageRotater.angle)*10+random.uniform(-15, 15),
                                               cos(GUN.imageRotater.angle)*10+random.uniform(-15, 15))))

                Cshot = shot(GUN.pos, vec2(sin(GUN.imageRotater.angle)*1000, cos(GUN.imageRotater.angle)*1000))
                shots.append(Cshot)
                GUN.reload = GUN.reloadMax
                
                self.fired = True
                return
            
    def hit(self, pos):
        if self.dead:
            return
        dist = vec2().from_points(pos, self.pos).get_magnitude()
        rise = pos.y - self.pos.y
        run = pos.x - self.pos.x
        angle = atan2(run, rise) - radians(self.angle)

        self.health -= 20
        
        for SMOKE in self.smoke:
            if getDistance(SMOKE.pos, pos) < 25:
                return
        self.smoke.append(smoke(self, dist, angle))
        
    def render(self, surface, camera):
        temp_rect = self.rect
        temp_rect.center -= camera.pos
        surface.blit(self.newImg, temp_rect)
        for GUN in self.guns:
            GUN.render(surface, camera)
            
        for SMOKE in self.smoke:
            SMOKE.render(surface, camera)

class enemy(warship):
    
    def __init__(self, img, pos):
        warship.__init__(self, img, pos)

class camera:
    
    def __init__(self, player):
        self.pos = vec2()
        player.camera = self
        
    def update(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy
        

def toInt(vec):
    return int(vec.x), int(vec.y)

def getDistance(potato, eisenhower):
    return vec2().from_points(potato, eisenhower).get_magnitude()

def detectHit(point, list,camera):
    pointMask = pygame.mask.from_surface(pygame.Surface((1,1)))
    pointMask.set_at((0,0), True)
    for ENWARSHIP in list:
        difference = toInt(point-(vec2(ENWARSHIP.rect.topleft)+camera.pos))
        intersect = ENWARSHIP.mask.overlap(pointMask, difference)
        if intersect is not None:
            return ENWARSHIP
        
    return False

class Map:
    
    def __init__(self, player, enemies, camera):
        self.w, self.h = screen_size
        self.player = player
        self.enemies = enemies
        self.camera = camera
        self.mapSurface = pygame.Surface((201,201))

    def render(self, surface):
        self.mapSurface.fill((65, 105, 225))
        for y in xrange(11):
            pygame.draw.line(self.mapSurface, (255, 255, 255), (y*20, 0), (y*20, 200))
            pygame.draw.line(self.mapSurface, (255, 255, 255), (0, y*20), (200, y*20))
            
        pygame.draw.circle(self.mapSurface, (0, 0, 255), (100, 100), 5)
        
        for ENEMY in self.enemies:
            if not ENEMY.dead:
                pos = toInt((ENEMY.pos-self.camera.pos)/10+vec2(0, 50))
                pygame.draw.circle(self.mapSurface, (255, 0, 0), pos, 5)
            
        surface.blit(self.mapSurface, (self.w-220, 20))
                

x = 0

war1 = warship(warshipDestroyerImage, p1)
war1S = warship(warshipDestroyerShadow, vec2(p1.x, p1.y+1))
can1S = gun(warshipGunShadow, vec2(p1.x, p1.y+1), 64, war1, True)
can1 = gun(warshipGunImage, p1, 64, war1)

can2S = gun(warshipGunShadow, vec2(p1.x, p1.y+1), -45, war1, True)
can2 = gun(warshipGunImage, p1, -45, war1)

can3S = gun(warshipGunShadow, vec2(p1.x, p1.y+1), -60, war1, True)
can3 = gun(warshipGunImage, p1, -60, war1)

can4s = gun(warshipGunShadow, vec2(p1.x, p1.y+1), -75, war1, True)
can4 = gun(warshipGunImage, p1, -75, war1)

enemies = []

for i in range(10):
    enemies.append(enemy(carrierImage, vec2(random.randint(-1000,2600), random.randint(-1000,1900))))
globalCamera = camera(war1)

globalMap = Map(war1, enemies, globalCamera)

mouse_pos = vec2()

clock = pygame.time.Clock()

draw_pos = (-10, -10)
shaking = False

firePower = 10

total_time = 0

aim_angle = 0

done = False
while not done:
    time_passed = clock.tick(60)
    time_passed_seconds = time_passed/1000.0
    
    total_time += time_passed_seconds
    
    mouse_pos.x, mouse_pos.y = pygame.mouse.get_pos()
    mouse_pos+=globalCamera.pos
    
    #INPUT BELOW
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
            pygame.image.save(screen, "SCREENSHOT.png")
            
        if event.type == pygame.MOUSEBUTTONDOWN and distance > 200:
            war1.fire(particles)
            if war1.fired:
                shaking = True
                shakeTimer = maxShakeTimer
                hit = detectHit(mouse_pos.copy(), enemies, globalCamera)
                for i in xrange(100):
                    a = random.randint(0,1)
                    
                    #Create a particle with a lifespan between 1 and 2 seconds, and give it a random offset
                    boost = 25
                    p = particle(random.uniform(.5,2), mouse_pos.copy(), vec2(random.uniform(-boost,boost),random.uniform(-boost,boost)))
                    
                    #vary the starting color a little
                    p.col1 = p.varyCol(p.col1)
                    
                    #If the shot misses, make the water effect
                    if not hit:
                        p.col2 = (65, 105, 225) #fade to the water color
                        p.colLifespan = p.lifespan
                        a = True
                        
                    #randomly make the color it fades from to white
                    if a:
                        p.col1 = (225,225,225)
                    particles.append(p)
                    
                #if the shot hit the enemy ship:
                if hit:
                    hit.hit(mouse_pos)
                
    #set rotation and movement to zero so we don't have to access the variables here, just in the update function
    rot = 0
    mov = 0
    
    #get all the keys currently pressed, this is for events that happen every frame (i.e. if you hold down
    #the 'w' key you should keep going forward, not just a pixel forward every time you hit it.
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_d]:
        rot -= 1
    if pressed_keys[pygame.K_a]:
        rot += 1
    if pressed_keys[pygame.K_w]:
        mov -= 1
    if pressed_keys[pygame.K_s]:
        mov += 1
        
    #INPUT ABOVE
    #UPDATING BELOW HERE
    
    #This is for determining what color the aim reticle should be.
    distance = vec2().from_points(war1.pos, mouse_pos).get_magnitude()
    rtf = war1.readyToFire()
    hit = detectHit(mouse_pos.copy(), enemies, globalCamera)
    #if a gun is ready to fire, it is an appropriate distance away, and the cursor is over an enemy, make the reticle green
    if hit and distance > 200 and rtf:
        mouse_img = green
    #if everything from before, but it is not over an enemy, make the reticle yellow
    elif not hit and distance > 200 and rtf:
        mouse_img = yellow
    #if a gun is not ready to fire or if you are aiming too close, make the reticle red.
    else:
        mouse_img = red
       
    #need to combine shadows and ships into the same class, this is annoying.
    war1.update(mouse_pos, time_passed_seconds, rot, mov, globalCamera)
    war1S.update(mouse_pos, time_passed_seconds, rot, mov, globalCamera)

    for ENEMY in enemies:
        ENEMY.update(mouse_pos, time_passed_seconds, 0, 0, globalCamera)

    #SCREENSHAKE BELOW
    if shaking:
        draw_pos = shake(elasticIn(shakeTimer/maxShakeTimer))
        shakeTimer -= time_passed_seconds
        if shakeTimer <= 0:
            shaking = False
            draw_pos = (-10,-10)
            shakeTimer = maxShakeTimer
    #SCREENSHAKE ABOVE
    
    #To remove for particles
    to_remove = []
    for EXP in particles:
        EXP.update(time_passed_seconds)
        if EXP.life >= EXP.lifespan:
            to_remove.append(EXP)
    for EXP in to_remove:
        particles.remove(EXP)
        
    #to remove for shots
    to_remove = []
    for SHOT in shots:
        SHOT.update(time_passed_seconds)
        if SHOT.dead:
            to_remove.append(SHOT)
    for SHOT in to_remove:
        shots.remove(SHOT)
    
    #UPDATING ABOVE HERE
    #RENDERING BELOW HERE
    
    totalSurface.fill((65, 105, 225))
    #pygame.draw.circle(screen, (255,0,0), toInt(p1), 32)
    war1S.render(totalSurface, globalCamera)
    war1.render(totalSurface, globalCamera)
    
    for ENEMY in enemies:
        ENEMY.render(totalSurface, globalCamera)
    
    for EXP in particles:
        EXP.render(totalSurface, globalCamera)
        
    for SHOT in shots:
        SHOT.render(totalSurface, globalCamera)
        
    mouse_rect = mouse_img.get_rect()
    mouse_rect.center = pygame.mouse.get_pos()
    totalSurface.blit(mouse_img, mouse_rect)
        
    #FONT BELOW
    dead = 0
    for i in enemies:
        if i.dead:
            dead += 1
    fpsTextRender = fontMed.render("Ships sunk: %d, FPS: %.2f" % (dead, clock.get_fps()), True, (255, 255, 255))
    fpsTextRenderBox = fpsTextRender.get_rect()
    fpsTextRenderBox.center = (w/2, 40)
    totalSurface.blit(fpsTextRender, fpsTextRenderBox)
    
    time_render = fontMed.render("%.2f" % total_time, True, (255, 255, 255))
    time_render_box = time_render.get_rect()
    time_render_box.center = (64, 32)
    totalSurface.blit(time_render, time_render_box)
    
    globalMap.render(totalSurface)
    
    #FONT ABOVE
    screen.blit(totalSurface, draw_pos)
    
    #RENDERING ABOVE HERE
    
    pygame.display.update()
    
pygame.quit()
