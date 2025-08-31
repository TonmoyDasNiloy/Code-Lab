from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Arena configuration
ARENA_DIMENSIONS = 800
TILE_SIZE = 60
BARRIER_HEIGHT = 250
HOSTILE_COUNT = 5

# Player state variables
warrior_x = 0.0
warrior_y = 0.0
warrior_z = 0.0
warrior_orientation = 0.0
movement_velocity = 200.0
rotation_velocity = 45.0
collision_boundary = 35.0
life_count = 5
elimination_count = 0
wayward_shots = 0
match_ended = False

# Player model dimensions
skull_radius = 15.0
torso_width = 50.0
torso_depth = 25.0
torso_height = 60.0
limb_radius = 12.0
limb_length = 60.0
limb_spacing = 15.0
appendage_radius = 6.0
appendage_length = 50.0
appendage_height = 40.0
weapon_radius = 10.0
weapon_length = 70.0
weapon_elevation = 30.0

# Enemy configuration
adversary_body_size = 30.0
adversary_head_size = 20.0
pulsation_amplitude = 0.3
pulsation_frequency = 2.0
adversary_velocity = 6.0
threat_registry = []

# Projectile system
projectile_registry = []
shot_velocity = 400.0
shot_dimensions = 15.0
shot_hit_radius = 8.0
shot_altitude = 30.0
firing_interval = 0.05
previous_shot_time = 0.0

# Camera system
view_angle = math.pi / 4
view_distance = 700.0
view_elevation = 500.0
view_rotation_speed = 1.0
view_height_speed = 200.0
immersive_mode = False
field_of_view = 120
screen_ratio = 1.25

# Special abilities
super_mode = False
enhanced_vision = False
spin_velocity = 270.0

# Input tracking
input_states = {}
special_input_states = {}

# Timing
simulation_time = 0.0
frame_timestamp = time.time()

def initialize_threats():
    global threat_registry
    threat_registry = []
    for _ in range(HOSTILE_COUNT):
        spawn_threat()

def spawn_threat():
    safe_distance = 100.0
    while True:
        threat_x = random.uniform(-ARENA_DIMENSIONS * 0.9, ARENA_DIMENSIONS * 0.9)
        threat_y = random.uniform(-ARENA_DIMENSIONS * 0.9, ARENA_DIMENSIONS * 0.9)
        distance_check = math.sqrt((threat_x - warrior_x)**2 + (threat_y - warrior_y)**2)
        if distance_check > safe_distance:
            break
    phase_offset = random.uniform(0, 2 * math.pi)
    threat_registry.append({'x': threat_x, 'y': threat_y, 'z': adversary_body_size, 'phase': phase_offset})

def launch_projectile():
    global previous_shot_time
    direction_rad = math.radians(warrior_orientation)
    velocity_x = -math.sin(direction_rad)
    velocity_y = math.cos(direction_rad)
    spawn_x = warrior_x + velocity_x * weapon_length
    spawn_y = warrior_y + velocity_y * weapon_length
    spawn_z = shot_altitude
    projectile_registry.append({'x': spawn_x, 'y': spawn_y, 'z': spawn_z, 'dir_x': velocity_x, 'dir_y': velocity_y, 'enhanced': super_mode})
    previous_shot_time = time.time()

def render_interface_text(x_position, y_position, message, typeface=GLUT_BITMAP_HELVETICA_18, color_rgb=(1, 1, 1), is_bold=False):
    glColor3f(color_rgb[0], color_rgb[1], color_rgb[2])
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    if is_bold:
        # Render text multiple times with slight offsets for bold effect
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                glRasterPos2f(x_position + offset_x, y_position + offset_y)
                for character in message:
                    glutBitmapCharacter(typeface, ord(character))
    else:
        glRasterPos2f(x_position, y_position)
        for character in message:
            glutBitmapCharacter(typeface, ord(character))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def render_warrior():
    glPushMatrix()
    glTranslatef(warrior_x, warrior_y, warrior_z)
    glRotatef(warrior_orientation, 0, 0, 1)
    if match_ended:
        glRotatef(90, 1, 0, 0)

    if not immersive_mode:
        # Legs
        glPushMatrix()
        glTranslatef(-limb_spacing / 2, 0, 0)
        glColor3f(0.5, 0.5, 0.5)
        quadric = gluNewQuadric()
        gluCylinder(quadric, limb_radius, limb_radius, limb_length, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(limb_spacing / 2, 0, 0)
        glColor3f(0.5, 0.5, 0.5)
        quadric = gluNewQuadric()
        gluCylinder(quadric, limb_radius, limb_radius, limb_length, 10, 10)
        glPopMatrix()

        # Torso
        glPushMatrix()
        glTranslatef(0, 0, limb_length + torso_height / 2)
        glScalef(torso_width, torso_depth, torso_height)
        glColor3f(0.8, 0.2, 0.2)
        glutSolidCube(1)
        glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(0, 0, limb_length + torso_height + skull_radius)
        glColor3f(0.9, 0.7, 0.5)
        quadric = gluNewQuadric()
        gluSphere(quadric, skull_radius, 10, 10)
        glPopMatrix()

    # Arms
    glPushMatrix()
    glTranslatef(-torso_width / 2 - appendage_radius, 0, limb_length + appendage_height)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.8)
    quadric = gluNewQuadric()
    gluCylinder(quadric, appendage_radius, appendage_radius, appendage_length, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(torso_width / 2 + appendage_radius, 0, limb_length + appendage_height)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.8)
    quadric = gluNewQuadric()
    gluCylinder(quadric, appendage_radius, appendage_radius, appendage_length, 10, 10)
    glPopMatrix()

    # Weapon
    glPushMatrix()
    glTranslatef(0, appendage_length / 2, limb_length + weapon_elevation)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.1, 0.1, 0.1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, weapon_radius, weapon_radius / 2, weapon_length, 10, 10)
    glPopMatrix()

    glPopMatrix()

def render_threat(threat_data):
    scale_factor = 1 + pulsation_amplitude * math.sin(simulation_time * pulsation_frequency + threat_data['phase'])
    glPushMatrix()
    glTranslatef(threat_data['x'], threat_data['y'], threat_data['z'])
    glColor3f(0.0, 1.0, 0.0)
    quadric = gluNewQuadric()
    gluSphere(quadric, adversary_body_size * scale_factor, 10, 10)
    glTranslatef(0, 0, adversary_body_size * scale_factor + adversary_head_size * scale_factor)
    glColor3f(0.6, 0.1, 0.8)
    quadric = gluNewQuadric()
    gluSphere(quadric, adversary_head_size * scale_factor, 10, 10)
    glPopMatrix()

def render_shot(shot_data):
    glPushMatrix()
    glTranslatef(shot_data['x'], shot_data['y'], shot_data['z'])
    glScalef(shot_dimensions, shot_dimensions, shot_dimensions)
    glColor3f(0.0, 1.0, 1.0)
    glutSolidCube(1)
    glPopMatrix()

def render_battlefield():
    grid_count = int(2 * ARENA_DIMENSIONS / TILE_SIZE)
    for i in range(-grid_count // 2, grid_count // 2 + 1):
        for j in range(-grid_count // 2, grid_count // 2 + 1):
            x1 = i * TILE_SIZE
            y1 = j * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            boundary_x1 = max(x1, -ARENA_DIMENSIONS)
            boundary_y1 = max(y1, -ARENA_DIMENSIONS)
            boundary_x2 = min(x2, ARENA_DIMENSIONS)
            boundary_y2 = min(y2, ARENA_DIMENSIONS)
            if boundary_x1 >= boundary_x2 or boundary_y1 >= boundary_y2:
                continue
            glBegin(GL_QUADS)
            if (i + j) % 2 == 0:
                glColor3f(0.9, 0.5, 0.0)
            else:
                glColor3f(0.6, 0.3, 0.0)
            glVertex3f(boundary_x1, boundary_y1, 0)
            glVertex3f(boundary_x2, boundary_y1, 0)
            glVertex3f(boundary_x2, boundary_y2, 0)
            glVertex3f(boundary_x1, boundary_y2, 0)
            glEnd()

def render_perimeter():
    glColor3f(0.0, 0.0, 0.8)
    glBegin(GL_QUADS)
    # Front wall
    glVertex3f(-ARENA_DIMENSIONS, ARENA_DIMENSIONS, 0)
    glVertex3f(ARENA_DIMENSIONS, ARENA_DIMENSIONS, 0)
    glVertex3f(ARENA_DIMENSIONS, ARENA_DIMENSIONS, BARRIER_HEIGHT)
    glVertex3f(-ARENA_DIMENSIONS, ARENA_DIMENSIONS, BARRIER_HEIGHT)
    # Back wall
    glVertex3f(-ARENA_DIMENSIONS, -ARENA_DIMENSIONS, 0)
    glVertex3f(ARENA_DIMENSIONS, -ARENA_DIMENSIONS, 0)
    glVertex3f(ARENA_DIMENSIONS, -ARENA_DIMENSIONS, BARRIER_HEIGHT)
    glVertex3f(-ARENA_DIMENSIONS, -ARENA_DIMENSIONS, BARRIER_HEIGHT)
    # Right wall
    glVertex3f(ARENA_DIMENSIONS, -ARENA_DIMENSIONS, 0)
    glVertex3f(ARENA_DIMENSIONS, ARENA_DIMENSIONS, 0)
    glVertex3f(ARENA_DIMENSIONS, ARENA_DIMENSIONS, BARRIER_HEIGHT)
    glVertex3f(ARENA_DIMENSIONS, -ARENA_DIMENSIONS, BARRIER_HEIGHT)
    # Left wall
    glVertex3f(-ARENA_DIMENSIONS, -ARENA_DIMENSIONS, 0)
    glVertex3f(-ARENA_DIMENSIONS, ARENA_DIMENSIONS, 0)
    glVertex3f(-ARENA_DIMENSIONS, ARENA_DIMENSIONS, BARRIER_HEIGHT)
    glVertex3f(-ARENA_DIMENSIONS, -ARENA_DIMENSIONS, BARRIER_HEIGHT)
    glEnd()

def constrain_position(x, y, radius):
    x = max(-ARENA_DIMENSIONS + radius, min(ARENA_DIMENSIONS - radius, x))
    y = max(-ARENA_DIMENSIONS + radius, min(ARENA_DIMENSIONS - radius, y))
    return x, y

def handle_input(key, x, y):
    global super_mode, enhanced_vision, immersive_mode
    input_states[key] = True
    if key == b'r':
        reset_simulation()
        return
    if match_ended:
        return
    if key == b'c':
        super_mode = not super_mode
    elif key == b'v' and super_mode:
        enhanced_vision = not enhanced_vision
        if enhanced_vision and not immersive_mode:
            immersive_mode = True

def handle_key_release(key, x, y):
    input_states[key] = False

def handle_special_input(key, x, y):
    special_input_states[key] = True

def handle_special_release(key, x, y):
    special_input_states[key] = False

def handle_mouse_action(button, state, x, y):
    global immersive_mode
    if match_ended:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        launch_projectile()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        immersive_mode = not immersive_mode

def configure_viewport():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(field_of_view, screen_ratio, 1.0, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def configure_viewpoint():
    if immersive_mode:
        eye_height = limb_length + torso_height + skull_radius
        eye_x = warrior_x
        eye_y = warrior_y
        direction_rad = math.radians(warrior_orientation)
        look_distance = 1.0
        look_direction_x = -math.sin(direction_rad)
        look_direction_y = math.cos(direction_rad)
        look_x = warrior_x + look_direction_x * look_distance
        look_y = warrior_y + look_direction_y * look_distance
        look_z = eye_height
        up_x = 0.0
        up_y = 0.0
        up_z = 1.0
        gluLookAt(eye_x, eye_y, eye_height, look_x, look_y, look_z, up_x, up_y, up_z)
    else:
        cam_x = view_distance * math.sin(view_angle)
        cam_y = view_distance * math.cos(view_angle)
        cam_z = view_elevation
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)

def update_simulation(time_delta):
    global simulation_time, life_count, elimination_count, wayward_shots, match_ended, previous_shot_time, warrior_x, warrior_y, warrior_orientation, view_elevation, view_angle

    simulation_time += time_delta

    if match_ended:
        return

    direction_rad = math.radians(warrior_orientation)
    forward_x = -math.sin(direction_rad)
    forward_y = math.cos(direction_rad)
    if b'w' in input_states and input_states[b'w']:
        warrior_x += forward_x * movement_velocity * time_delta
        warrior_y += forward_y * movement_velocity * time_delta
    if b's' in input_states and input_states[b's']:
        warrior_x -= forward_x * movement_velocity * time_delta
        warrior_y -= forward_y * movement_velocity * time_delta
    if b'a' in input_states and input_states[b'a']:
        warrior_orientation = (warrior_orientation + rotation_velocity * time_delta) % 360
    if b'd' in input_states and input_states[b'd']:
        warrior_orientation = (warrior_orientation - rotation_velocity * time_delta) % 360

    warrior_x, warrior_y = constrain_position(warrior_x, warrior_y, collision_boundary)

    if GLUT_KEY_UP in special_input_states and special_input_states[GLUT_KEY_UP]:
        view_elevation += view_height_speed * time_delta
    if GLUT_KEY_DOWN in special_input_states and special_input_states[GLUT_KEY_DOWN]:
        view_elevation -= view_height_speed * time_delta
    view_elevation = max(50.0, view_elevation)
    if GLUT_KEY_LEFT in special_input_states and special_input_states[GLUT_KEY_LEFT]:
        view_angle += view_rotation_speed * time_delta
    if GLUT_KEY_RIGHT in special_input_states and special_input_states[GLUT_KEY_RIGHT]:
        view_angle -= view_rotation_speed * time_delta

    for threat in threat_registry:
        dx = warrior_x - threat['x']
        dy = warrior_y - threat['y']
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            threat['x'] += (dx / distance) * adversary_velocity * time_delta
            threat['y'] += (dy / distance) * adversary_velocity * time_delta
        threat['x'], threat['y'] = constrain_position(threat['x'], threat['y'], adversary_body_size)

    active_shots = []
    for shot in projectile_registry:
        shot['x'] += shot['dir_x'] * shot_velocity * time_delta
        shot['y'] += shot['dir_y'] * shot_velocity * time_delta
        if abs(shot['x']) > ARENA_DIMENSIONS or abs(shot['y']) > ARENA_DIMENSIONS:
            if not shot['enhanced']:
                wayward_shots += 1
            continue
        collision = False
        for threat_idx in range(len(threat_registry) - 1, -1, -1):
            threat = threat_registry[threat_idx]
            scale_factor = 1 + pulsation_amplitude * math.sin(simulation_time * pulsation_frequency + threat['phase'])
            dx = shot['x'] - threat['x']
            dy = shot['y'] - threat['y']
            dz_body = shot['z'] - threat['z']
            body_distance = math.sqrt(dx**2 + dy**2 + dz_body**2)
            if body_distance < shot_hit_radius + adversary_body_size * scale_factor:
                collision = True
            head_z = threat['z'] + adversary_body_size * scale_factor + adversary_head_size * scale_factor
            dz_head = shot['z'] - head_z
            head_distance = math.sqrt(dx**2 + dy**2 + dz_head**2)
            if head_distance < shot_hit_radius + adversary_head_size * scale_factor:
                collision = True
            if collision:
                elimination_count += 1
                del threat_registry[threat_idx]
                spawn_threat()
                break
        if not collision:
            active_shots.append(shot)
    projectile_registry[:] = active_shots

    collision_detected = False
    warrior_center_z = limb_length + torso_height / 2
    for threat_idx in range(len(threat_registry) - 1, -1, -1):
        threat = threat_registry[threat_idx]
        dx = warrior_x - threat['x']
        dy = warrior_y - threat['y']
        dz = warrior_center_z - threat['z']
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        scale_factor = 1 + pulsation_amplitude * math.sin(simulation_time * pulsation_frequency + threat['phase'])
        if distance < collision_boundary + adversary_body_size * scale_factor:
            collision_detected = True
            del threat_registry[threat_idx]
            spawn_threat()
            break
    if collision_detected:
        life_count -= 1
        if life_count <= 0:
            life_count = 0

    if super_mode:
        warrior_orientation = (warrior_orientation + spin_velocity * time_delta) % 360
        current_time = time.time()
        aim_direction = (warrior_orientation + 90) % 360
        for threat in threat_registry:
            dx = threat['x'] - warrior_x
            dy = threat['y'] - warrior_y
            threat_direction = math.degrees(math.atan2(dy, dx)) % 360
            direction_difference = min(abs(threat_direction - aim_direction), 360 - abs(threat_direction - aim_direction))
            if direction_difference < 5 and current_time - previous_shot_time > firing_interval:
                launch_projectile()
                break

    if life_count <= 0 or wayward_shots >= 10:
        match_ended = True

def animation_cycle():
    global frame_timestamp
    current_time = time.time()
    time_delta = current_time - frame_timestamp
    frame_timestamp = current_time
    update_simulation(time_delta)
    glutPostRedisplay()

def render_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    configure_viewport()
    configure_viewpoint()
    render_battlefield()
    render_perimeter()
    if not match_ended:
        render_warrior()
        for threat in threat_registry:
            render_threat(threat)
        for shot in projectile_registry:
            render_shot(shot)
    else:
        render_warrior()
        threat_registry.clear()
    
    render_interface_text(10, 770, f"Life Remaining: {life_count}")
    render_interface_text(10, 740, f"Game Score: {elimination_count}")
    render_interface_text(10, 710, f"Bullets Missed: {wayward_shots}")
    
    if match_ended:
        render_interface_text(300, 450, "GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24, (1, 1, 0), True)
        render_interface_text(300, 400, "Press R to Restart", GLUT_BITMAP_HELVETICA_18, (1, 1, 0), True)
        render_interface_text(300, 380, f"Final Score: {elimination_count}", GLUT_BITMAP_HELVETICA_18, (1, 1, 0), True)
    
    glutSwapBuffers()

def reset_simulation():
    global warrior_x, warrior_y, warrior_z, warrior_orientation, life_count, elimination_count, wayward_shots, match_ended, projectile_registry, super_mode, enhanced_vision, immersive_mode, simulation_time, input_states, special_input_states, frame_timestamp, previous_shot_time, view_elevation, view_angle
    warrior_x = 0.0
    warrior_y = 0.0
    warrior_z = 0.0
    warrior_orientation = 0.0
    life_count = 5
    elimination_count = 0
    wayward_shots = 0
    match_ended = False
    projectile_registry = []
    initialize_threats()
    super_mode = False
    enhanced_vision = False
    immersive_mode = False
    simulation_time = 0.0
    input_states = {}
    special_input_states = {}
    frame_timestamp = time.time()
    previous_shot_time = 0.0
    view_elevation = 500.0
    view_angle = math.pi / 4
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy Ultimate")
    glEnable(GL_DEPTH_TEST)
    initialize_threats()
    glutDisplayFunc(render_scene)
    glutKeyboardFunc(handle_input)
    glutKeyboardUpFunc(handle_key_release)
    glutSpecialFunc(handle_special_input)
    glutSpecialUpFunc(handle_special_release)
    glutMouseFunc(handle_mouse_action)
    glutIdleFunc(animation_cycle)
    glutMainLoop()

if __name__ == "__main__":
    main()