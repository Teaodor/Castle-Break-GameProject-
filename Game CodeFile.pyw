import pygame
import pymunk as pm
from pymunk.vec2d import Vec2d

#Game states 
MAIN_MENU = 0   #game state for main menu
SETTINGS = 1    #game state for settings menu
GAME = 2    #game state for main game
WINNER = 3  #game state for winner screen
HELP = 4  # game state for help menu

#Constants used for categorize different types of objects for collision handling
COLLTYPE_DEFAULT = 0   
COLLTYPE_MOUSE = 1      
COLLTYPE_BALL = 2
COLLTYPE_POLYGON = 3
COLLTYPE_STATIC = 4

#Initialize pygame and create screen
pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font_large = pygame.font.SysFont('Arial', 50)
font_medium = pygame.font.SysFont('Arial', 36)

#Game settings (can be modified in settings menu)
settings = {
    "gravity": 900,
    "ball_radius": 15,
    "wall_break_threshold": 400
}

class BreakableBlocks:  #Class for dynamic walls 
    def __init__(self, pos, length, height, space, movable=True, breakable=True, mass=10.0):   #sets up wall properties 
        self.breakable = breakable 
        self.destruction_threshold = settings["wall_break_threshold"]

        if movable:
            moment = pm.moment_for_box(mass, (length, height))
            self.body = pm.Body(mass, moment)
        else:
            self.body = pm.Body(body_type=pm.Body.STATIC)

        self.body.position = Vec2d(*pos) #sets the position of the wall
        self.shape = pm.Poly.create_box(self.body, (length, height)) #sets the shape of the wall
        self.shape.friction = 0.4 #friction of the wall
        self.shape.elasticity = 0.5 #bounciness of the wall
        self.shape.collision_type = COLLTYPE_POLYGON #collision type of the wall
        space.add(self.body, self.shape) #adds the wall to the space in pymunk

    def draw(self, screen, flip_func):  #function to draw the wall
        ps = [self.body.local_to_world(v) for v in self.shape.get_vertices()]
        ps = [flip_func(p) for p in ps]
        pygame.draw.lines(screen, pygame.Color("black"), True, ps, 3)

def create_ball(point, space, mass=1.0): #function to create a ball
    radius = settings["ball_radius"]    #sets the radius of the ball
    moment = pm.moment_for_circle(mass, 0, radius) #sets the moment of inertia of the ball
    ball_body = pm.Body(mass, moment)   #ets the mass of the ball
    ball_body.position = Vec2d(*point) #sets the position of the ball
    ball_shape = pm.Circle(ball_body, radius) #sets the shape of the ball
    ball_shape.friction = 1.5 #ball friction
    ball_shape.elasticity = 0.9 #ball bounciness
    ball_shape.collision_type = COLLTYPE_BALL
    space.add(ball_body, ball_shape) #adds the ball to the space in pymunk
    return ball_shape

def draw_ball(ball, screen, flip_func): #function to draw the ball
    body = ball.body #sets the body of the ball
    p = flip_func(body.position) #sets the position of the ball
    r = ball.radius #sets the radius of the ball
    pygame.draw.circle(screen, pygame.Color("black"), p, int(r), 2) #draws the ball

def flipyv(v, screen_height): #function to flip the y coordinate of the ball
    # This is used to convert pymunk coordinates to pygame coordinates
    return int(v.x), int(-v.y + screen_height) #returns the flipped coordinates



def handle_Polygon_collision(arbiter, space, data): #function to handle wall collision
    if (arbiter.shapes[0].collision_type == COLLTYPE_BALL and  #checks if the first shape is a ball
        arbiter.shapes[1].collision_type == COLLTYPE_POLYGON): #checks if the second shape is a polygon
        
        impulse = arbiter.total_impulse.length #gets the impulse of the collision (impolse is the force of the collision)
        wall_shape = arbiter.shapes[1] #gets the shape of the wall
        
        for wall in polygons: #loops through all the polygons in order to check if the wall is breakable and if the impulse is greater than the destruction threshold
            if hasattr(wall, 'shape') and wall.shape == wall_shape and wall.breakable:
                if impulse > wall.destruction_threshold:
                    space.remove(wall.shape, wall.body)
                    polygons.remove(wall)
                    break

def run_main_menu(): #function to run the main menu and what happens when the user presses a specific button
    while True:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:   #
                return False, None
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE: 
                    return True, GAME
                elif event.key == pygame.K_s:
                    return True, SETTINGS
                elif event.key == pygame.K_ESCAPE:
                    return False, None
                elif event.key == pygame.K_h:
                    return True, HELP

        screen.fill(pygame.Color("black")) 
        #draws the main menu
        title = font_large.render("Castle break", True, (255, 255, 255))
        start_text = font_medium.render("Press SPACE to Start", True, (255, 255, 255))
        settings_text = font_medium.render("Press S for Settings", True, (255, 255, 255))
        quit_text = font_medium.render("Press ESC to Quit", True, (255, 255, 255))
        help_text = font_medium.render("Press H for help", True, (255, 255, 255))
        #draws the text on the screen
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
        screen.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, HEIGHT//2 + 50))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 100))
        screen.blit(help_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 150))
        
        pygame.display.flip()
        clock.tick(60)

def run_help_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True, MAIN_MENU
                elif event.key == pygame.K_BACKSPACE:
                    return True, GAME  # Return to game if BACKSPACE pressed

        screen.fill(pygame.Color("black"))

        # Draw help content
        title = font_large.render("Help", True, (255, 255, 255))
        lines = [
            "Left Click & Drag on Ball to Shoot",
            "Break the red walls by hitting them",
            "Yellow text in Settings = currently selected option",
            "Press TAB to open Settings during the game",
            "Press ESC to return to Menu",
            "Press BACKSPACE to return to Game"
        ]
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//6))
        for i, line in enumerate(lines):
            text = font_medium.render(line, True, (200, 200, 200))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3 + i * 40))

        pygame.display.flip()
        clock.tick(60)

def run_settings(): #function to run the settings menu
    selected_setting = 0
    settings_options = list(settings.keys())
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True, MAIN_MENU
                elif event.key == pygame.K_UP:
                    selected_setting = (selected_setting - 1) % len(settings_options)
                elif event.key == pygame.K_DOWN:
                    selected_setting = (selected_setting + 1) % len(settings_options)
                elif event.key == pygame.K_LEFT:
                    settings[settings_options[selected_setting]] = max(10, settings[settings_options[selected_setting]] - 20)
                elif event.key == pygame.K_RIGHT:
                    settings[settings_options[selected_setting]] = min(1000, settings[settings_options[selected_setting]] + 20)
                elif event.key == pygame.K_h:
                    return True, HELP


        screen.fill(pygame.Color("black"))
        #draws the settings menu
        title = font_large.render("Settings", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//6))
        #draws the title of the settings menu
        for i, (key, value) in enumerate(settings.items()):
            color = (255, 255, 0) if i == selected_setting else (255, 255, 255)
            text = font_medium.render(f"{key}: {value}", True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3 + i*40))
        #draws the settings options on the screen
        help_text = font_medium.render("UP/DOWN: Select setting | LEFT/RIGHT: Change value", True, (200, 200, 200))
        back_text = font_medium.render("Press ESC to return to menu", True, (200, 200, 200))
        #draws the help text and back text on the screen
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT - 100))
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        clock.tick(60) #sets the frame rate to 60 FPS

def run_winner_menu(): #creats the winner menu
    #this function is called when the player wins the game
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True, GAME
                elif event.key == pygame.K_ESCAPE:
                    return True, MAIN_MENU

        screen.fill(pygame.Color("black"))
        #draws the winner menu
        title = font_large.render("You Win!", True, (255, 255, 0))
        restart_text = font_medium.render("Press SPACE to Play Again", True, (255, 255, 255))
        menu_text = font_medium.render("Press ESC to Return to Menu", True, (255, 255, 255))
        #draws the title and text on the screen
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(60) #sets the frame rate to 60 FPS

def run_game():
    # Initialize physics space with current settings
    space = pm.Space()
    space.gravity = (0.0, -settings["gravity"])
    
    # Create static walls
    walls = [
        pm.Segment(space.static_body, (0, 0), (0, HEIGHT), 5),
        pm.Segment(space.static_body, (0, 0), (WIDTH, 0), 5),
        pm.Segment(space.static_body, (WIDTH, 0), (WIDTH, HEIGHT), 5),
        pm.Segment(space.static_body, (0, HEIGHT), (WIDTH, HEIGHT), 5),
    ]
    for wall in walls: #sets the properties of the walls
        wall.friction = 1.0 #friction of the wall
        wall.elasticity = 0.9 #bounciness of the wall
        wall.collision_type = COLLTYPE_STATIC #collision type of the wall
        space.add(wall)
    
    # Game objects
    global polygons
    polygons = []
    balls = []
    
    # Collision handler
    handler = space.add_collision_handler(COLLTYPE_BALL, COLLTYPE_POLYGON)
    handler.post_solve = handle_Polygon_collision
     
    # Create initial objects and if any are breakable and movable 
    polygons.append(BreakableBlocks((650, 605), 100, 50, space, movable=True, breakable=True))
    polygons.append(BreakableBlocks((500, 85), 200, 50, space, movable=True, breakable=True))
    polygons.append(BreakableBlocks((500, 95), 200, 50, space, movable=True, breakable=True))
    polygons.append(BreakableBlocks((500, 125), 200, 50, space, movable=True, breakable=True))
    balls.append(create_ball((1100, 100), space))
    
    # Game state for running the game 
    mouse_contact = None
    selected_ball = None
    mouse_start_pos = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True, MAIN_MENU
                elif event.key == pygame.K_TAB:
                    return True, SETTINGS
                elif event.key == pygame.K_h:
                    return True, HELP
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                p = Vec2d(event.pos[0], HEIGHT - event.pos[1])
                for ball in balls:
                    if ball.point_query(p).distance < 0:
                        selected_ball = ball
                        mouse_start_pos = p
                        break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if selected_ball:
                    p = Vec2d(event.pos[0], HEIGHT - event.pos[1])
                    impulse = (mouse_start_pos - p) * 10
                    max_impulse = 1000
                    if impulse.length > max_impulse:
                        impulse = impulse.normalized() * max_impulse
                    selected_ball.body.apply_impulse_at_local_point(impulse)
                    selected_ball = None
                    mouse_start_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if selected_ball:
                    mouse_contact = Vec2d(event.pos[0], HEIGHT - event.pos[1])
        
        # Check win condition - no breakable polygons left
        if not any(poly.breakable for poly in polygons):
            return True, WINNER
        
        # Physics step
        space.step(1/60.0)
        
        # Drawing
        screen.fill(pygame.Color("white"))
        
        # Draw polygons
        for polygon in polygons:
            polygon.draw(screen, lambda v: flipyv(v, HEIGHT))
        
        # Draw walls
        for wall in walls:
            p1 = flipyv(wall.a, HEIGHT)
            p2 = flipyv(wall.b, HEIGHT)
            pygame.draw.lines(screen, pygame.Color("black"), False, [p1, p2], 5)
        
        # Draw balls
        for ball in balls:
            draw_ball(ball, screen, lambda v: flipyv(v, HEIGHT))
        
        # Draw mouse contact
        if mouse_contact:
            p = flipyv(mouse_contact, HEIGHT)
            pygame.draw.circle(screen, pygame.Color("red"), p, 3)
        
        # Draw help text
        help_text = font_medium.render("ESC: Menu | TAB: Settings", True, (100, 100, 100))
        screen.blit(help_text, (10, 10))
                #Draw remaining breakable polygons counter
        breakable_left = sum(1 for poly in polygons if poly.breakable)
        breakable_text = font_medium.render(f"Breakable Walls Left: {breakable_left}", True, (200, 0, 0))
        screen.blit(breakable_text, (10, 50))

        
        pygame.display.flip()
        clock.tick(60) #sets the frame rate to 60 FPS

def main(): #main function to run the game
    current_state = MAIN_MENU
    running = True
    # Main game loop
    while running:
        if current_state == MAIN_MENU:
            running, next_state = run_main_menu()
            current_state = next_state if next_state is not None else current_state
        elif current_state == SETTINGS:
            running, next_state = run_settings()
            current_state = next_state if next_state is not None else current_state
        elif current_state == GAME:
            running, next_state = run_game()
            current_state = next_state if next_state is not None else current_state
        elif current_state == WINNER:
            running, next_state = run_winner_menu()
            current_state = next_state if next_state is not None else current_state
        elif current_state == HELP:
            running, next_state = run_help_menu()
            current_state = next_state if next_state is not None else current_state

    pygame.quit()

if __name__ == "__main__": #created to run the game and start from a specific function
    main()
