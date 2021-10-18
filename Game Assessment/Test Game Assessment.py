# Import variables
import math
import arcade
import os

# Window variables how big the window is
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Sets the windows name
SCREEN_TITLE = "Game Assessment"

# Sprite scaling constants control how big sprite are
SPRITE_SCALING = 0.3
PLAYER_SCALING = 0.25
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING / 100)
SPRITE_SCALING_LASER = 0.5
TILE_SCALING = (SPRITE_SCALING / 1.6)

# Player/bullet movement speed pixels per frame
PLAYER_MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5
BULLET_SPEED = 10

# Sets the strength of gravity/jump speed
GRAVITY = 1.5
JUMP_SPEED = 20

# Boundaries of the scrolling screen controls if the player reach these position on screen the camera will move
LEFT_VIEWPORT_MARGIN = 700
RIGHT_VIEWPORT_MARGIN = 700
BOTTOM_VIEWPORT_MARGIN = 400
TOP_VIEWPORT_MARGIN = 400

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
    """ --- THIS CLASS CONTAINS EVERYTHING ABOUT THE PLAYER --- """
    def __init__(self):
        """ --- THIS IS THE MAIN FUNCTION WHERE EVERYTHING GETS SETUP --- """
        # Set up parent class
        super().__init__()

        # Sets variables (to state what the player is doing)
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # Sets the amount of ammo the player starts with
        self.player_ammo = 3
        self.player_jump = 20

        # Sets the player default facing direction (Right)
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Sets the default scale of the player
        self.scale = PLAYER_SCALING

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        # --- Load Textures --- #
        # Sets the player default file path
        main_path = "images/player_1/water_player"

        # --- Loads the player files to the right action --- #
        # Loads the jump textures

        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        # Loads the falling textures

        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")
        # Loads the idle textures

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        # Load the walking textures

        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load the climbing textures
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):
        """ --- UPDATES THE PLAYERS ANIMATIONS EVERY 60 SECONDS --- """
        # This resizes the players scale by how much ammo they have
        self.scale = PLAYER_SCALING + self.player_ammo / 18

        # Decide if the player needs to face left or right (if so the player will be flipped)
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # --- IDLE ANIMATION --- #
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # --- WALKING ANIMATION --- #
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

        # --- JUMPING ANIMATION --- #
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
    """ --- THIS IS THE VIEW TO SHOW THE GAMEOVER SCREEN --- """
    def __init__(self, game_view):
        """ --- THIS IS THE MAIN FUNCTION WHERE EVERYTHING GETS SETUP --- """
        # Set up parent class
        super().__init__()

        # Sets the game view
        self.game_view = game_view

        # Sets the default selected to 0 so no button will be highlighted when the game starts
        self.selected = 0

        # Sets up the picture for the background of the gameover screen
        self.texture = arcade.load_texture("images/Game Over.png")

        # Loads the sound for the button selection noise
        self.button_sound = arcade.load_sound("sounds/Button select.wav")

        # Resets the viewport back to where the gameover screen is (this is needed other wise the camera wont be looking
        # at the game over screen)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        """ --- EVERYTHING INSIDE THIS WILL BE DRAWN OF THE SCREEN --- """

        # Everything between this will be drawn on the screen
        arcade.start_render()

        # Resets the viewport again to make sure the camera is looking at the viewport
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Draws the picture in the background of the gameover screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- Draws the CONTINUE button --- #
        # If selected is == 1 then the continue button will be drawn slightly larger
        if self.selected == 1:
            arcade.draw_text("Continue", 225, 285,
                             arcade.color.WHITE, font_size=60, anchor_x="center")

        # If selected is not == 1 then the button will be drawn at its normal smaller size
        else:
            arcade.draw_text("Continue", 225, 285,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # --- Draws the MENU button --- #
        # If selected is == 2 then the menu button will be drawn slightly larger
        if self.selected == 2:
            arcade.draw_text("Menu", 225, 180,
                             arcade.color.WHITE, font_size=60, anchor_x="center")

        # If selected is not == 2 then the normal version of the button will be shown
        else:
            arcade.draw_text("Menu", 225, 180,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # --- Draws the QUIT button --- #
        # If selected is == 3 then the QUIT button will be drawn slightly larger
        if self.selected == 3:
            arcade.draw_text("Quit", 225, 75,
                             arcade.color.WHITE, font_size=60, anchor_x="center")

        # If selected is not == 3 then the QUIT version of the button will be shown
        else:
            arcade.draw_text("Quit", 225, 75,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # Draws the title text for the gameover screen
        arcade.draw_text("LOL you died", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.4,
                         arcade.color.WHITE, font_size=70, anchor_x="center")

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ --- TRACKS WHERE THE MOUSE IS ON SCREEN --- """

        # --- Tracking for CONTINUE --- #
        # If the mouse is inside these points then then selected will be set to 1
        if 80 < x < 370 and 275 < y < 365:
            # If selected is not already set to 1 then selected will be set to 1
            if self.selected != 1:
                # --- Continue --- #
                # Sets selected to 1
                self.selected = 1
                # Plays the player feedback sound when the player hovers over the CONTINUE button
                arcade.play_sound(self.button_sound)

        # --- Tracking for SELECTED --- #
        # If the mouse is inside these points then then selected will be set to 2
        elif 100 < x < 320 and 170 < y < 270:
            if self.selected != 2:
                # --- MENU --- #
                # Sets selected to 2
                self.selected = 2
                # Plays the player feedback sound when the player hovers over the MENU button
                arcade.play_sound(self.button_sound)

        # --- Tracking for QUIT --- #
        # If the mouse is inside these points then then selected will be set to 3
        elif 150 < x < 300 and 75 < y < 180:
            if self.selected != 3:
                # --- CONTINUE --- #
                # Sets selected to 3
                self.selected = 3
                # Plays the player feedback sound when the player hovers over the MENU button
                arcade.play_sound(self.button_sound)
        # If the player is not hovering over any button then selected will be set to 0 so no button will be highlighted
        else:
            self.selected = 0

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ --- TRACKS IF THE PLAYER CLICKS SOMEWHERE ON SCREEN --- """

        # --- Tracking for CONTINUE --- #
        # If the mouse is clicked inside these points then these action will happen
        if 150 < _x < 300 and 275 < _y < 365:
            # --- CONTINUE --- #
            # Sets the view back to the game view
            game_view = LevelSelect()
            self.window.show_view(game_view)

        # --- Tracking for MENU --- #
        # If the mouse is clicked inside these points then these action will happen
        if 100 < _x < 320 and 170 < _y < 270:
            # --- MENU --- #
            # Sets the view back to the instruction view
            game_view = InstructionView()
            self.window.show_view(game_view)

        # --- Tracking for QUIT --- #
        # If the mouse is clicked inside these points then these action will happen
        if 150 < _x < 300 and 75 < _y < 180:
            # --- QUIT --- #
            # Quits out of the window
            arcade.close_window()


class InstructionView(arcade.View):
    """ --- THIS IS THE VIEW TO SHOW THE instruction SCREEN --- """
    def __init__(self):
        """ --- THIS IS THE MAIN FUNCTION WHERE EVERYTHING GETS SETUP --- """
        # Set up parent class
        super().__init__()

        # Sets the default selected to 0 so no button will be highlighted when the game starts
        self.selected = 0

        # Sets up the picture for the background of the instruction screen
        self.texture = arcade.load_texture("images/Title.png")

        # Loads the sound for the button selection noise
        self.button_sound = arcade.load_sound("sounds/Button select.wav")

        # Resets the viewport back to where the gameover screen is (this is needed other wise the camera wont be looking
        # at the game over screen)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        """ --- EVERYTHING INSIDE THIS WILL BE DRAWN ON THE SCREEN --- """
        # Everything between this will be drawn on the screen
        arcade.start_render()

        # Resets the viewport again to make sure the camera is looking at the viewport
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Draws the picture in the background of the gameover screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- DRAWS THE PLAY BUTTON --- #
        # If selected is == 1 then the play button will be drawn slightly larger
        if self.selected == 1:
            arcade.draw_text("Play", 225, 370,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        # If selected is not == 1 then the button will be drawn at its normal smaller size
        else:
            arcade.draw_text("Play", 225, 370,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # --- DRAWS THE LEVEL SELECT BUTTON --- #
        # If selected is == 2 then the quit button will be drawn slightly larger
        if self.selected == 2:
            arcade.draw_text("Level Select", 225, 235,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        # If selected is not == 2 then the button will be drawn at its normal smaller size
        else:
            arcade.draw_text("Level Select", 225, 235,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # --- DRAWS THE QUIT BUTTON --- #
        # If selected is == 3 then the quit button will be drawn slightly larger
        if self.selected == 3:
            arcade.draw_text("Quit", 225, 125,
                             arcade.color.WHITE, font_size=60, anchor_x="center")

        # If selected is not == 3 then the button will be drawn at its normal smaller size
        else:
            arcade.draw_text("Quit", 225, 125,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # Draws the title text for the title screen
        arcade.draw_text("Water Drop", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.4,
                         arcade.color.WHITE, font_size=70, anchor_x="center")

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ --- TRACKS WHERE THE MOUSE IS --- """
        # --- TRACKING FOR PLAY --- #
        # If the mouse is hovering on these points then selected will be set the 1
        if 150 < x < 300 and 350 < y < 450:
            # If selected is already 1 then the sound wont play again
            if self.selected != 1:
                # Play
                self.selected = 1
                arcade.play_sound(self.button_sound)

        # --- TRACKING FOR LEVEL SELECT --- #
        # If the mouse is hovering on these points then selected will be set the 2
        elif 50 < x < 400 and 240 < y < 325:
            # If selected is already 2 then the sound wont play again
            if self.selected != 2:
                # Level Select
                self.selected = 2
                arcade.play_sound(self.button_sound)

        # --- TRACKING FOR QUIT --- #
        # If the mouse is hovering on these points then selected will be set the 3
        elif 150 < x < 300 and 125 < y < 225:
            # If selected is already 3 then the sound wont play again
            if self.selected != 3:
                # Quit
                self.selected = 3
                arcade.play_sound(self.button_sound)

        else:
            # If player is not hovering any button it will make all of them small
            self.selected = 0

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ --- TRACKS IF THE PLAYER CLICKS SOMEWHERE ON SCREEN --- """
        # --- TRACKING FOR CONTINUE --- #
        if 150 < _x < 300 and 350 < _y < 450:
            # --- PLAY --- #
            # If the mouse is clicked inside these point then selected will be set to 1 and theres actions will happen
            self.selected = 1
            game_view = GameView()
            game_view.setup(1)
            self.window.show_view(game_view)

        # --- TRACKING FOR LEVEL SELECT --- #
        if 50 < _x < 400 and 240 < _y < 325:
            # --- LEVEL SELECT --- #
            # If the mouse is clicked inside these points then selected will be set to 2 and these actions will happen
            self.selected = 2
            game_view = LevelSelect()
            self.window.show_view(game_view)

        # --- TRACKING FOR QUIT --- #
        if 150 < _x < 300 and 125 < _y < 230:
            # --- QUIT --- #
            # If the mouse is clicked inside these points then selected will be set to 3 and these actions will happen
            self.selected = 3
            game_view = GameView()
            self.window.show_view(game_view)


class LevelSelect(arcade.View):
    """ --- THIS IS THE VIEW TO SHOW THE LEVEL SELECT VIEW --- """
    def __init__(self):
        """ --- THIS IS THE MAIN FUNCTION WHERE EVERYTHING GETS SETUP --- """
        # Set up parent class
        super().__init__()

        # Sets the default selected to 0 so no button will be highlighted when the game starts
        self.selected = 0

        # Sets what level will be shown
        self.show_level = 1

        # Sets button selector to 0
        self.button_selector = 0

        # Sets up the picture for the background of the instruction screen
        self.texture = arcade.load_texture("images/Title.png")

        # Loads the sound for the button selection noise
        self.button_sound = arcade.load_sound("sounds/Button select.wav")

        # Resets the viewport back to where the gameover screen is (this is needed other wise the camera wont be looking
        # at the game over screen)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        """ --- EVERYTHING INSIDE THIS WILL BE DRAWN OF THE SCREEN --- """
        # Everything between this will be drawn on the screen
        arcade.start_render()

        # Resets the viewport again to make sure the camera is looking at the viewport
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Draws the picture in the background of the gameover screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- DRAWS THE QUIT BUTTON --- #
        # If selected is == 1 then the quit button will be drawn slightly larger
        if self.selected == 3:
            arcade.draw_text("Back", 225, 125,
                             arcade.color.WHITE, font_size=60, anchor_x="center")
        # If selected is not == 3 then the button will be drawn at its normal smaller size
        else:
            arcade.draw_text("Back", 225, 125,
                             arcade.color.WHITE, font_size=50, anchor_x="center")

        # --- DRAWS THE LEVELS --- #
        # If the player has scrolled through to this level then it will show level 1
        if self.show_level == 1:
            # If selected is == 4 then the quit button will be drawn slightly larger
            if self.selected == 4:
                arcade.draw_text("Level 1", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=60, anchor_x="center")
            # If selected is not == 4 then the button will be drawn at its normal smaller size
            else:
                arcade.draw_text("Level 1", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=50, anchor_x="center")

        # If the player has scrolled through to this level then it will show level 2
        if self.show_level == 2:
            # If selected is == 5 then the quit button will be drawn slightly larger
            if self.selected == 5:
                arcade.draw_text("Level 2", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=60, anchor_x="center")
            # If selected is not == 5 then the button will be drawn at its normal smaller size
            else:
                arcade.draw_text("Level 2", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=50, anchor_x="center")

        # If the player has scrolled through to this level then it will show level 3
        if self.show_level == 3:
            # If selected is == 6 then the quit button will be drawn slightly larger
            if self.selected == 6:
                arcade.draw_text("Level 3", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=60, anchor_x="center")
            # If selected is not == 6 then the button will be drawn at its normal smaller size
            else:
                arcade.draw_text("Level 3", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=50, anchor_x="center")

        # If the player has scrolled through to this level then it will show level 4
        if self.show_level == 4:
            # If selected is == 7 then the quit button will be drawn slightly larger
            if self.selected == 7:
                arcade.draw_text("Level 4", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=60, anchor_x="center")
            # If selected is not == 7 then the button will be drawn at its normal smaller size
            else:
                arcade.draw_text("Level 4", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=50, anchor_x="center")

        # If the player has scrolled through to this level then it will show level 5
        if self.show_level == 5:
            # If selected is == 8 then the quit button will be drawn slightly larger
            if self.selected == 8:
                arcade.draw_text("Level 5", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=60, anchor_x="center")
            # If selected is not == 8 then the button will be drawn at its normal smaller size
            else:
                arcade.draw_text("Level 5", SCREEN_WIDTH / 2, 270,
                                 arcade.color.WHITE, font_size=50, anchor_x="center")

        # Draws the title text for the title screen
        arcade.draw_text("Select Level", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.4,
                         arcade.color.WHITE, font_size=70, anchor_x="center")

        # Draws the arrows to change the level select
        if self.button_selector == 1:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, 370, 25, 25, arcade.csscolor.GRAY)
        else:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, 370, 25, 25, arcade.csscolor.WHITE)

        # Draws the arrows to change the level select
        if self.button_selector == 2:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, 230, 25, 25, arcade.csscolor.GRAY)
        else:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, 230, 25, 25, arcade.csscolor.WHITE)

        print(self.show_level)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ Contains where the mouse is """
        if 150 < x < 300 and 125 < y < 230:
            if self.selected != 3:
                # Quit
                self.selected = 3
                arcade.play_sound(self.button_sound)

        elif self.show_level == 1:
            if 540 < x < 740 and 265 < y < 335:
                if self.selected != 4:
                    # Level 1
                    self.selected = 4
                    arcade.play_sound(self.button_sound)

            else:
                # If player is not hovering any button it will make all of them small
                self.selected = 0

        elif self.show_level == 2:
            if 540 < x < 740 and 265 < y < 335:
                if self.selected != 5:
                    # Level 1
                    self.selected = 5
                    arcade.play_sound(self.button_sound)

            else:
                # If player is not hovering any button it will make all of them small
                self.selected = 0

        elif self.show_level == 3:
            if 540 < x < 740 and 265 < y < 335:
                if self.selected != 6:
                    # Level 1
                    self.selected = 6
                    arcade.play_sound(self.button_sound)

            else:
                # If player is not hovering any button it will make all of them small
                self.selected = 0

        elif self.show_level == 4:
            if 540 < x < 740 and 265 < y < 335:
                if self.selected != 7:
                    # Level 1
                    self.selected = 7
                    arcade.play_sound(self.button_sound)

            else:
                # If player is not hovering any button it will make all of them small
                self.selected = 0

        elif self.show_level == 5:
            if 540 < x < 740 and 265 < y < 335:
                if self.selected != 8:
                    # Level 1
                    self.selected = 8
                    arcade.play_sound(self.button_sound)

            else:
                # If player is not hovering any button it will make all of them small
                self.selected = 0

        else:
            # If player is not hovering any button it will make all of them small
            self.selected = 0

        if 615 < x < 665 and 345 < y < 395:
            self.button_selector = 1

        elif 615 < x < 665 and 205 < y < 255:
            self.button_selector = 2

        else:
            self.button_selector = 0

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ --- TRACKS IF THE PLAYER CLICKS SOMEWHERE ON SCREEN --- """
        # --- Tracking for QUIT --- #
        # If the mouse is inside these points then then selected will be set to 3
        if 150 < _x < 300 and 125 < _y < 230:
            # --- Tracking for QUIT --- #
            # If the mouse is clicked inside these points then these action will happen
            print("Quit")
            game_view = InstructionView()
            self.window.show_view(game_view)
            self.selected = 3

        # If the player clicked where the level selector is than check what level they should be taken to
        if self.show_level == 1:
            if 540 < _x < 740 and 265 < _y < 335:
                game_view = GameView()
                game_view.setup(1)
                self.window.show_view(game_view)

        if self.show_level == 2:
            if 540 < _x < 740 and 265 < _y < 335:
                game_view = GameView()
                game_view.setup(2)
                self.window.show_view(game_view)

        if self.show_level == 3:
            if 540 < _x < 740 and 265 < _y < 335:
                game_view = GameView()
                game_view.setup(3)
                self.window.show_view(game_view)

        if self.show_level == 4:
            if 540 < _x < 740 and 265 < _y < 335:
                game_view = GameView()
                game_view.setup(4)
                self.window.show_view(game_view)

        if self.show_level == 5:
            if 540 < _x < 740 and 265 < _y < 335:
                game_view = GameView()
                game_view.setup(5)
                self.window.show_view(game_view)

        # --- CHOOSE A LEVEL BUTTONS --- #
        if 615 < _x < 665 and 345 < _y < 395:
            if self.show_level == 5:
                arcade.play_sound(self.button_sound)

            elif self.show_level < 5:
                self.show_level += 1
                arcade.play_sound(self.button_sound)

        if 615 < _x < 665 and 205 < _y < 255:
            if self.show_level == 1:
                arcade.play_sound(self.button_sound)

            elif self.show_level > 1:
                self.show_level -= 1
                arcade.play_sound(self.button_sound)


class GameView(arcade.View):
    """ --- MAIN VIEW FOR THE GAME VIEW --- """
    def __init__(self):
        """ --- SETS EVERYTHING UP FOR THE GAME --- """
        # Call the parent class and set up the window
        super().__init__()

        # Makes the mouse visible while hovering over the window
        self.window.set_mouse_visible(True)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Tracks the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # --- LISTS --- #
        # Creates lists for all of our sprites
        self.wall_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.start_list = None
        self.do_touch_list = None
        self.player_list = None
        self.enemy_list = None
        self.text_list = None
        self.bullet_list = None
        self.water_list = None

        # --- SETS WHERE THE PLAYER STARTS --- #
        # Set the point where the player will start
        self.PLAYER_START_X = 700
        self.PLAYER_START_Y = 550

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our 'physics' engine
        self.physics_engine = None

        # Set the reset variable to False
        self.reset = False

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Sets the end of the map
        self.end_of_map = 0

        # This sets the first level that the player will start on
        self.level = 1

        # --- LOAD SOUNDS --- #
        # Hurt sound
        self.hurt = arcade.load_sound("sounds/hurt.wav")

        # Bullet wall
        self.bullet_hit = arcade.load_sound("sounds/Bullet Hit.wav")

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game """
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # --- CREATE SPRITE PLAYER LIST --- #
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()

        # -- DRAWS ENEMY ON THE GROUND --- #
        # Sets up the enemy to be drawn in the game
        enemy = arcade.Sprite(":resources:images/enemies/ladybug.png", SPRITE_SCALING)

        # --- WHERE THE ENEMY WILL BE DRAWN --- #
        # If level == 1 then draw the enemy here
        if self.level == 1:
            # Point where the enemy will be drawn
            enemy.bottom = 505
            enemy.left = 1400

        if self.level == 2:
            # Point where the enemy will be drawn
            enemy.bottom = 505
            enemy.left = 1400

        # --- SETS THE BOUNDARIES ENEMIES CANT CROSS --- #
        enemy.change_x = 2
        self.enemy_list.append(enemy)

        # --- Sets the player up at these points --- #
        self.player_sprite = PlayerCharacter()

        # Set the players ammo
        self.player_sprite.player_ammo = 3

        # --- LOAD IN THE TILES FORM THE MAP --- #
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"
        # Name of the layer that has items the player has to touch to win
        do_touch_layer_name = "Do Touch"
        # Name of the layer that has text in it
        text_layer_name = "Text"
        # Name of the layer that has water in it.
        water_name = "Water"

        # --- RESETS THE PLAYER LOCATION --- #
        # Resets the player to the starting location to make sure the player starts at the right position
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- LOADS THE MAP NAME --- #
        # Loads map file
        map_name = f"maps/level{level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculates the right edge(end) of the my_map in pixels
        self.end_of_map = my_map.map_size.width * SPRITE_SCALING - 185

        # --- DRAWS EVERYTHING ON THE MAP --- #
        # --- Background objects --- #
        self.background_list = arcade.tilemap.process_layer(my_map, "Background", TILE_SCALING)

        # --- Platforms --- #
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      platforms_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Don't Touch Layer --- #
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)

        # --- Do Touch Layer --- #
        self.do_touch_list = arcade.tilemap.process_layer(my_map,
                                                          do_touch_layer_name,
                                                          TILE_SCALING,
                                                          use_spatial_hash=True)

        # --- Water --- #
        self.water_list = arcade.tilemap.process_layer(my_map, water_name, TILE_SCALING)

        # --- Text --- #
        self.text_list = arcade.tilemap.process_layer(my_map,
                                                      text_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Other stuff --- #
        # Set the maps background colour
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # --- Physics Engine --- #
        # Creates the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)

    def on_draw(self):
        """ Render the screen """
        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.background_list.draw()
        self.water_list.draw()
        self.dont_touch_list.draw()
        self.do_touch_list.draw()
        self.bullet_list.draw()
        self.wall_list.draw()

        # Draw tutorials
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
                # arcade.play_sound(self.jump_sound)
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
            # arcade.play_sound(self.gun_sound)

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
                arcade.play_sound(self.bullet_hit)

            if len(wall_hit_list) > 0:
                arcade.play_sound(self.bullet_hit)
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
            arcade.play_sound(self.hurt)

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
            arcade.play_sound(self.hurt)

        # Did the player touch a enemy?
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.enemy_list):
            enemy.remove_from_sprite_lists()
            self.player_sprite.player_ammo -= 2
            arcade.play_sound(self.hurt)

        # See if the user got to the end of the level
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.do_touch_list):
            # Advance to the next level
            self.level += 1

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

            # Change to the next level
            view = LevelSelect()
            self.window.show_view(view)

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
            self.reset = True
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
