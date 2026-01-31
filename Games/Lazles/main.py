from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader
import random
import math

app = Ursina()

# --- ZEGA SYSTEM CONFIG ---
window.title = 'ZEGA - Tactical Operative (Balanced)'
window.color = color.black
window.exit_button.visible = False
window.vsync = True

# Professional Brand Colors
ZEGA_GREEN = color.hex('#58f01b')
NEON_RED = color.hex('#ff0033')

# --- LIGHTING ---
AmbientLight(color=color.rgba(70, 70, 70, 255))
PointLight(y=20, color=color.white, range=100)

# --- ENVIRONMENT ---
ground = Entity(
    model='plane', collider='box', scale=400, 
    texture='white_cube', texture_scale=(200,200), 
    color=color.black, specular=1, shininess=120
)
sky_dome = Entity(model='sphere', scale=700, color=color.black, double_sided=True)

# --- PLAYER & HUMAN AVATAR ---
player = FirstPersonController(origin_y=-.5)
player.cursor.enabled = False
player.max_health = 200 # New baseline
player.health = 200
player.view_mode = '1st'
player.speed = 16 # Balanced speed (fast but controllable)

# Avatar Container
avatar = Entity(parent=player, enabled=False)

# Humanoid Body Construction
head = Entity(parent=avatar, model='cube', color=color.light_gray, scale=(.4, .4, .4), y=1.8, shader=basic_lighting_shader)
torso = Entity(parent=avatar, model='cube', color=color.dark_gray, scale=(.8, 1, .4), y=1.1, shader=basic_lighting_shader)
l_arm = Entity(parent=avatar, model='cube', color=color.gray, scale=(.15, .7, .15), x=-.45, y=1.2, shader=basic_lighting_shader)
r_arm = Entity(parent=avatar, model='cube', color=color.gray, scale=(.15, .7, .15), x=.45, y=1.2, shader=basic_lighting_shader)
l_leg = Entity(parent=avatar, model='cube', color=color.black, scale=(.25, .9, .25), x=-.25, y=.45, shader=basic_lighting_shader)
r_leg = Entity(parent=avatar, model='cube', color=color.black, scale=(.25, .9, .25), x=.25, y=.45, shader=basic_lighting_shader)
visor = Entity(parent=head, model='cube', color=ZEGA_GREEN, scale=(1.1, .15, .15), z=.45, y=.1)

# --- HUD ---
health_bar_bg = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(0.5, 0.02), position=(-0.55, 0.45))
health_bar = Entity(parent=camera.ui, model='quad', color=ZEGA_GREEN, scale=(0.5, 0.02), position=(-0.55, 0.45), origin_x=-.5)
crosshair = Entity(parent=camera.ui, model='circle', color=ZEGA_GREEN, scale=0.01, mode='line')
score_text = Text(text='SYSTEMS OPTIMIZED', color=ZEGA_GREEN, position=(0.5, 0.48), scale=1.5)

# --- GAME OBJECTS ---
enemies = []
enemies_destroyed = 0

class Laser(Entity):
    def __init__(self, position, rotation):
        super().__init__(model='sphere', scale=(.1, .1, 2.5), color=ZEGA_GREEN, 
                         position=position, rotation=rotation, collider='box', unlit=True)
        self.glow = PointLight(parent=self, color=ZEGA_GREEN, range=10)

    def update(self):
        self.position += self.forward * 180 * time.dt # Slightly faster laser
        hit_info = self.intersects()
        if hit_info.hit and hit_info.entity in enemies:
            global enemies_destroyed
            enemies_destroyed += 1
            score_text.text = f'Eliminated: {enemies_destroyed}'
            enemies.remove(hit_info.entity)
            destroy(hit_info.entity)
            destroy(self)
            return
        if self and distance(self.position, player.position) > 250:
            destroy(self)

class Enemy(Entity):
    def __init__(self, position):
        super().__init__(model='sphere', color=NEON_RED, scale=2.5, position=position, 
                         collider='sphere', shader=basic_lighting_shader)
        self.glow = PointLight(parent=self, color=NEON_RED, range=8)

    def update(self):
        self.look_at(player.position)
        # Enemies get slightly faster as you destroy more of them
        speed_boost = min(enemies_destroyed * 0.1, 5)
        self.position += self.forward * (5 + speed_boost) * time.dt
        
        if distance(self.position, player.position) < 2.2:
            player.health -= 25 * time.dt
            # Fixed health bar scaling for the new 200 HP limit
            health_bar.scale_x = (max(0, player.health) / player.max_health) * 0.5
            if player.health <= 0:
                print("ZEGA OPERATIVE RETIRED")
                application.quit()

# --- INPUT HANDLING ---
def input(key):
    if key == 'f5':
        if player.view_mode == '1st':
            camera.parent = player
            camera.position = (2.8, 4.0, -9) # Refined 3rd person angle
            camera.rotation_x = 10
            avatar.enabled = True
            player.view_mode = '3rd'
        else:
            camera.parent = player
            camera.position = (0, 2, 0)
            camera.rotation_x = 0
            avatar.enabled = False
            player.view_mode = '1st'

    if key == 'left mouse down':
        # Enhanced firing feel
        p = camera.world_position + camera.forward * 2
        r = camera.world_rotation
        Laser(position=p, rotation=r)

# --- MAIN UPDATE LOOP ---
def update():
    is_moving = held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']
    
    if is_moving:
        walking_speed = 10
        l_leg.rotation_x = math.sin(time.time() * walking_speed) * 35
        r_leg.rotation_x = math.sin(time.time() * walking_speed + math.pi) * 35
        l_arm.rotation_x = math.sin(time.time() * walking_speed + math.pi) * 30
        r_arm.rotation_x = math.sin(time.time() * walking_speed) * 30
    else:
        l_leg.rotation_x = lerp(l_leg.rotation_x, 0, time.dt * 10)
        r_leg.rotation_x = lerp(r_leg.rotation_x, 0, time.dt * 10)
        l_arm.rotation_x = lerp(l_arm.rotation_x, 0, time.dt * 10)
        r_arm.rotation_x = lerp(r_arm.rotation_x, 0, time.dt * 10)

    # Fair Spawning: Spawn limit increases slightly with your score
    max_enemies = 15 + (enemies_destroyed // 10)
    if len(enemies) < min(max_enemies, 30):
        spawn_pos = Vec3(random.randint(-100, 100), 1.25, random.randint(-100, 100))
        if distance(spawn_pos, player.position) > 45:
            enemies.append(Enemy(position=spawn_pos))

app.run()