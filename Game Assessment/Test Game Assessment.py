# Import variables
import math
import arcade
import os

# Window variables
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Game Assessment"

# Sprite scaling constants
SPRITE_SCALING = 0.3
PLAYER_SCALING = 0.25
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING / 100)
SPRITE_SCALING_LASER = 0.5
TILE_SCALING = (SPRITE_SCALING / 1.6)

# Player movement speed (pixels per frame)
PLAYER_MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5
GRAVITY = 1.5
BULLET_SPEED = 10

# Boundaries of the scrolling screen
LEFT_VIEWPORT_MARGIN = 680
RIGHT_VIEWPORT_MARGIN = 680
BOTTOM_VIEWPORT_MARGIN = 360
TOP_VIEWPORT_MARGIN = 360

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """ Load a texture pair, with the second being a mirror image """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    """ Player Sprite """
    def __init__(self):
        # Set up parent class
        super().__init__()

        # Sets variables
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.player_damage = False

        # Set the players ammo
        self.player_ammo = 3
        self.player_jump = 20

        # Default to face-right
        self.character_face_direction = RIGHT_FACING
        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = PLAYER_SCALING
        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        # --- Load Textures ---
        main_path = "images/player_1/water_player"

        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):

        # Scale the players size by amount of ammo
        self.scale = PLAYER_SCALING + self.player_ammo / 18

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return


class GameOverView(arcade.View):
    """ View to show instructions """

    def __init__(self, game_view):
        # Set up parent class
        super().__init__()

        self.game_view = game_view

        # Variables
        self.selected = 0

        # Draw picture for background of the view port
        self.texture = arcade.load_texture("images/Title.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()

        # Reset viewport
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Draw text/buttons on title screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

        # if variables is == 1 then the continue button will be bigger to show the player is hovering over the button
        if self.selected == 1:
            arcade.draw_text("Continue", 225, 285,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        # If selected is not == 1 then the normal version of the button will be shown
        else:
            arcade.draw_text("Continue", 225, 285,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # if variables is == 2 then the menu button will be bigger to show the player is hovering over the button
        if self.selected == 2:
            arcade.draw_text("Menu", 225, 180,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        # If selected is not == 1 then the normal version of the button will be shown
        else:
            arcade.draw_text("Menu", 225, 180,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # if variables is == 3 then the quit button will be bigger to show the player is hovering over the button
        if self.selected == 3:
            arcade.draw_text("Quit", 225, 75,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        # If selected is not == 1 then the normal version of the button will be shown
        else:
            arcade.draw_text("Quit", 225, 75,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # Draw the title of the game over screen
        arcade.draw_text("Lol you died", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.4,
                         arcade.color.WHITE, font_size=70, anchor_x="center")

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ Contains where the mouse is """
        if 80 < x < 370 and 275 < y < 365:
            # Continue
            self.selected = 1

        if 100 < x < 320 and 170 < y < 270:
            # Menu
            self.selected = 2

        if 150 < x < 300 and 75 < y < 180:
            # Quit
            self.selected = 3

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user clicks on a button, this is called """
        if 150 < _x < 300 and 275 < _y < 365:
            # Continue
            self.window.show_view(self.game_view)

        if 100 < _x < 320 and 170 < _y < 270:
            # Menu
            game_view = InstructionView()
            self.window.show_view(game_view)
            self.selected = 2

        if 150 < _x < 300 and 75 < _y < 180:
            # Quit
            arcade.close_window()
            self.selected = 3


class InstructionView(arcade.View):
    """ View to show instructions """

    def __init__(self):
        # Set up parent class
        super().__init__()

        # Variables
        self.selected = 0

        # Draw picture for background of the view port
        self.texture = arcade.load_texture("images/Title.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()

        # Reset viewport
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Draw text on title screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

        arcade.draw_rectangle_filled(225, 320, 150, 90, (255, 255, 255, 50), 0)

        if self.selected == 1:
            arcade.draw_text("Play", 225, 285,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        else:
            arcade.draw_text("Play", 225, 285,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        if self.selected == 3:
            arcade.draw_text("Quit", 225, 75,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        else:
            arcade.draw_text("Quit", 225, 75,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        arcade.draw_text("Yep This is a Game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.4,
                         arcade.color.WHITE, font_size=70, anchor_x="center")

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ Contains where the mouse is """
        if 150 < x < 300 and 275 < y < 365:
            # Play
            self.selected = 1

        if 150 < x < 300 and 75 < y < 180:
            # Quit
            self.selected = 3

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user clicks on a button, this is called """
        if 150 < _x < 300 and 275 < _y < 365:
            # Play
            print("Play")
            game_view = GameView()
            game_view.setup(1)
            self.window.show_view(game_view)

        if 150 < _x < 300 and 75 < _y < 180:
            # Quit
            print("Quit")
            arcade.close_window()
            self.selected = 3


class GameView(arcade.View):
    """ Main application class """
    def __init__(self):
        """ Initializer for the game """

        # Call the parent class and set up the window
        super().__init__()

        # Set the mouse to visible
        self.window.set_mouse_visible(True)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.slime_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.start_list = None
        self.do_touch_list = None
        self.ladder_list = None
        self.player_list = None
        self.enemy_list = None
        self.text_list = None
        self.bullet_list = None
        self.enemy_turn_list = None
        self.water_list = None

        # Where the player starts
        self.PLAYER_START_X = 500
        self.PLAYER_START_Y = 700

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our 'physics' engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # End of map
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds
        # Jump sound
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        # Death noise
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        # Gun sound
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        # Hit sound
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game """
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.slime_list = arcade.SpriteList()
        self.text_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemy_turn_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()

        # -- Draw an enemy on the ground
        enemy = arcade.Sprite(":resources:images/enemies/ladybug.png", SPRITE_SCALING)

        if self.level == 1:
            # Where the enemy starts
            enemy.bottom = 505
            enemy.left = 1400

        # Set boundaries on the left/right the enemy can't cross
        enemy.change_x = 2
        self.enemy_list.append(enemy)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()

        # Set up the sprite center
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the moving platforms layer
        # moving_platforms_layer_name = 'Moving Platforms'
        # Name of the layer with the items in the foreground
        foreground_layer_name = "Foreground"
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"
        # Name of the layer that has items the player has to touch to win
        do_touch_layer_name = "Do Touch"
        # Name of the layer that has items the player will spawn at
        start_layer_name = "Start Block"
        # Name of the layer that has text in it
        text_layer_name = "Text"
        # Name of the layer that turns a enemy when it hits it.
        enemy_turn_name = "Enemy Turn"
        # Name of the layer that has water in it.
        water_name = "Water"

        # Map name
        map_name = f"maps/level{level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * SPRITE_SCALING - 185

        # -- Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        # -- Background objects
        self.background_list = arcade.tilemap.process_layer(my_map, "Background", TILE_SCALING)

        # -- Background objects
        self.ladder_list = arcade.tilemap.process_layer(my_map, "Ladders",
                                                        TILE_SCALING,
                                                        use_spatial_hash=True)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      platforms_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Enemy Turn Blocks
        self.enemy_turn_list = arcade.tilemap.process_layer(my_map,
                                                            enemy_turn_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)

        # -- Don't Touch Layer
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)

        # -- Do Touch Layer
        self.do_touch_list = arcade.tilemap.process_layer(my_map,
                                                          do_touch_layer_name,
                                                          TILE_SCALING,
                                                          use_spatial_hash=True)

        # -- Water
        self.water_list = arcade.tilemap.process_layer(my_map, water_name, TILE_SCALING)

        # -- Start Layer
        self.start_list = arcade.tilemap.process_layer(my_map,
                                                       start_layer_name,
                                                       TILE_SCALING,
                                                       use_spatial_hash=True)

        # -- Text
        self.text_list = arcade.tilemap.process_layer(my_map,
                                                      text_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)

    def on_draw(self):
        """ Render the screen """
        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.background_list.draw()
        self.text_list.draw()
        self.water_list.draw()
        self.dont_touch_list.draw()
        self.do_touch_list.draw()
        self.start_list.draw()
        self.bullet_list.draw()
        self.wall_list.draw()
        self.ladder_list.draw()

        # Draw tutorials
        if self.level == 1:
            # Draw text for the movement tutorial
            arcade.draw_text("Use A and D to move", 600, 650,
                             arcade.csscolor.WHITE, 20)
            # Draw text for the jump tutorial
            arcade.draw_text("Use W to jump", 975, 550,
                             arcade.csscolor.WHITE, 20)
            # Draw text for the shooting tutorial
            arcade.draw_text("Click to shoot a bullet to kill an enemy\n     but be careful shooting uses lives",
                             1220, 580, arcade.csscolor.WHITE, 20)
            # Draw text for the water tutorial
            arcade.draw_text("Suck up water to gain lives\n     back and grow bigger", 1460, 950,
                             arcade.csscolor.WHITE, 20)
            # Draw text for shrinking tutorial
            arcade.draw_text("                   Maybe if you were a little smaller?\n "
                             "(shoot to shrink but watch your lives in the bottom left)", 625, 1010,
                             arcade.csscolor.WHITE, 20)

        self.player_list.draw()
        self.foreground_list.draw()
        self.enemy_list.draw()

        # Draw the players ammo/lives on the screen, scrolling it with the viewport
        ammo_text = f"Lives : {self.player_sprite.player_ammo}"
        arcade.draw_text(ammo_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

    def process_keychange(self):
        """ Called when we change a key up/down or we move on/off a ladder """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = self.player_sprite.player_jump
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when the mouse is clicked """

        if self.player_sprite.player_ammo > -2:
            # Gunshot sound
            arcade.play_sound(self.gun_sound)

            # Create a bullet
            bullet = arcade.Sprite("images/player_1/water_bullet.png", SPRITE_SCALING_LASER)

            # Lose 1 ammo
            self.player_sprite.player_ammo -= 1

            # Position the bullet
            start_x = self.player_sprite.center_x
            start_y = self.player_sprite.center_y
            bullet.center_x = start_x
            bullet.center_y = start_y

            # Get the position for mouse
            dest_x = self.view_left + x
            dest_y = self.view_bottom + y

            # Math to get bullet to location
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Angle for the bullet to fly
            bullet.angle = math.degrees(angle)
            print(f"Bullet angle: {bullet.angle:2f}")

            # Taking into account bullet angle
            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            # Add the bullet to appropriate lists
            self.bullet_list.append(bullet)

        elif self.player_sprite.player_ammo < 0:
            # If the player has no ammo then they cant shoot
            print("No ammo")

    def on_key_press(self, key, modifiers):
        """ Called whenever a key is pressed """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """ Called when the user releases a key """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        """ Movement and game logic """
        # Move the enemy
        self.bullet_list.update()

        # Moves the enemy
        self.enemy_list.update()

        # Check each enemy
        for enemy in self.enemy_list:

            # If the enemy hit a wall, reverse
            if len(arcade.check_for_collision_with_list(enemy, self.wall_list)) > 0:
                enemy.change_x *= -1
            # If the enemy hit the left boundary, reverse
            elif enemy.boundary_left is not None and enemy.left < enemy.boundary_left:
                enemy.change_x *= -1
            # If the enemy hit the right boundary, reverse
            elif enemy.boundary_right is not None and enemy.right > enemy.boundary_right:
                enemy.change_x *= -1
            # Checks if enemy is hit by bullet
            hit_list = arcade.check_for_collision_with_list(enemy, self.bullet_list)

            # If enemy is hit by a bullet, delete the enemy
            if len(hit_list) > 0:
                enemy.remove_from_sprite_lists()

        # Loops through each bullet
        for bullet in self.bullet_list:

            # Check if bullet hit a wall
            enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)

            # If bullet did hit then remove from list
            if len(enemy_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if len(wall_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # If bullet flies off screen remove it
            if bullet.bottom > SCREEN_WIDTH:
                bullet.remove_from_sprite_lists()

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.slime_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)
        self.player_list.update_animation(delta_time)

        # Update walls, used with moving platforms
        self.wall_list.update()

        # See if the moving wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # Track if we need to change the viewport
        changed_viewport = False

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = self.PLAYER_START_X
            self.player_sprite.center_y = self.PLAYER_START_Y
            self.player_sprite.player_ammo -= 1

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

        # Did the player touch a spike?
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.dont_touch_list):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = self.PLAYER_START_X
            self.player_sprite.center_y = self.PLAYER_START_Y
            self.player_sprite.player_ammo -= 1

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

        # Did the player touch a enemy?
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.enemy_list):
            enemy.remove_from_sprite_lists()
            self.player_sprite.player_ammo -= 1

        # See if the user got to the end of the level
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.do_touch_list):
            # Advance to the next level
            self.level += 1

            # Load the next level
            self.setup(self.level)

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # Check if the player touches water
        water_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                              self.water_list)

        for water in water_hit_list:
            # Remove the water block from list. We touched the water so the water will disappear
            water.remove_from_sprite_lists()

            # Add more ammo.
            self.player_sprite.player_ammo += 1
        # If ammo drops bellow zero player dies
        if self.player_sprite.player_ammo < 0:
            # Switch to game over view
            view = GameOverView(self)
            self.window.show_view(view)

        # --- Manage Scrolling ---
        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
