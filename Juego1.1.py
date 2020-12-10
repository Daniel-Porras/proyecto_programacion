import arcade
#Constantes de la pantalla 
anchoPantalla=1000
largoPantalla=500
tituloJuego="Juegazo"
#Constantes de los sprite
escalaJugador=1
escalaObstaculos=0.5
escalaMonedas=0.5
#Constanntes del juego
velocidad_personaje=5
velocidad_salto_personaje=15
gravedad=0.6
# Cuántos píxeles mantener como margen mínimo entre el carácter y el borde de la pantalla.
margen_lado_izquierda=250
margen_lado_derecha=250
margen_lado_arriba=64
margen_lado_abajo=64
#Constantes para la animación 
RIGHT_FACING = 0
LEFT_FACING = 1
#Leer archivos txt 
archivo = open("contra.txt","r")
leerTxt=archivo.read()
usuariosContraseñas=eval(leerTxt)
archivo.close()
#Pantalla de instrucciones 
class InstructionView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
        arcade.set_viewport(0, anchoPantalla - 1, 0, largoPantalla - 1)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Utilize las flechas para mover el personaje", anchoPantalla / 2, largoPantalla / 2,
                        arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click para iniciar", anchoPantalla / 2, largoPantalla / 2-75,
                        arcade.color.WHITE, font_size=20, anchor_x="center")

    # Si se da click en la pantalla el juego empieza   
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = Mygame()
        game_view.setup(game_view.nivel,0,3)
        self.window.show_view(game_view)

#Pantalla de game over 
class GameOverView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
        arcade.set_viewport(0, anchoPantalla - 1, 0, largoPantalla - 1)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("GAME OVER", anchoPantalla / 4, largoPantalla*1/2 ,
                        arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click para volver a jugar", anchoPantalla / 4, largoPantalla / 2-75,
                        arcade.color.WHITE, font_size=20, anchor_x="center")

    # Si se da click en la pantalla el juego empieza   
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = Mygame()
        game_view.setup(1,0,3)
        self.window.show_view(game_view)

#Pantalla de gansate
class WinView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
        arcade.set_viewport(0, anchoPantalla - 1, 0, largoPantalla - 1)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("¡Ganaste!", anchoPantalla *3 , largoPantalla*1.5,
                        arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click para volver a jugar", anchoPantalla / 2, largoPantalla / 2-75,
                        arcade.color.WHITE, font_size=20, anchor_x="center")

    # Si se da click en la pantalla el juego empieza   
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = Mygame()
        game_view.setup(1,0,3)
        self.window.show_view(game_view)

#Permite Cargar las texturas del personaje 
def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class PlayerCharacter(arcade.Sprite):
    #Jugador Sprite
    def __init__(self):

        super().__init__()

        # Miar hacia la derecha 
        self.character_face_direction = RIGHT_FACING

        # Usado para cambiar las texturas 
        self.cur_texture = 0
        self.scale = escalaJugador

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        #Cargar texturas 

        main_path = ":resources:images/animated_characters/robot/robot"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Cargar texturas de caminar 
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Cargar texturas de escalar 
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Poner la animación inicial 
        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

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

        # saltar animación 
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # animación de caminar 
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        

class Mygame(arcade.View):
    #Configuración de la pantalla
    def __init__(self):
        
        super().__init__()
            
        #Iniciar las listas
        self.jugador_lista =None
        self.obstaculos_lista=None
        self.monedas_lista=None
        self.fondo_lista=None
        #Iniciar lista sprite del jugador
        self.jugador_sprite=None
        #Iniciar lista de físcas del juego
        self.motor_fisica = None
        #Iniciar lista de físcas del juego
        self.muerte_lista = None
        # Usados para el desplazamiento de la "camara"
        self.vista_abajo = 0
        self.vista_izquierda = 0
        # Puntaje del juego
        self.puntaje = 0
        # Vidas
        self.vidas = 0
        #Nivel
        self.nivel=1
        # Cargar sonidos 
        self.coger_monedas_sonido = arcade.load_sound(":resources:sounds/coin1.wav")
        self.salto_sonido= arcade.load_sound(":resources:sounds/jump2.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover3.wav")



    def setup(self,nivel,puntaje,vida):

        #Listas  del juego
        self.jugador_lista = arcade.SpriteList()
        self.obstaculos_lista = arcade.SpriteList(use_spatial_hash=True)
        self.monedas_lista = arcade.SpriteList(use_spatial_hash=True)
        self.muerte_lista = arcade.SpriteList(use_spatial_hash=True)
        self.fondo_lista = arcade.SpriteList(use_spatial_hash=True)
        self.banderas_lista=arcade.SpriteList(use_spatial_hash=True)
       # Usados para el desplazamiento de la "camara"
        self.vista_abajo = 0
        self.vista_izquierda = 0
        # Puntaje del juego
        self.puntaje = puntaje
        # Vidas
        self.vidas = vida
        #Animar el presonaje 
        self.jugador_sprite = PlayerCharacter()
        self.jugador_sprite.center_x = 32
        self.jugador_sprite.center_y = 200
        self.jugador_lista.append(self.jugador_sprite)
        """
        #Crear el suelo
        for x in range(0,1500,64):
            suelo=arcade.Sprite(":resources:images/tiles/stoneMid.png", escalaObstaculos)
            suelo.center_x=x
            suelo.center_y=32
            self.obstaculos_lista.append(suelo)
        

        #Crear plataformas
        for x in range(500,565,64):
            suelo=arcade.Sprite(":resources:images/tiles/stoneMid.png", escalaObstaculos)
            suelo.center_x=x
            suelo.center_y=253
            self.obstaculos_lista.append(suelo)
        """      
        """
        #Crear lava
        for x in range(532,600,64):
            suelo=arcade.Sprite(":resources:images/tiles/lavaTop_high.png", escalaObstaculos)
            suelo.center_x=x
            suelo.center_y=37
            self.lava_lista.append(suelo)   

        """
        """
        #Lista con la posicion de las cajas 
        posicionCajas_lista=[[512, 96],[256, 96],[768, 96]]
        #Poner cajas en el juego
        for coordenadas in posicionCajas_lista:
            cajas=arcade.Sprite(":resources:images/tiles/boxCrate_double.png", escalaObstaculos)
            cajas.position=coordenadas
            self.obstaculos_lista.append(cajas)
        """    
        """

        # Monedas en el juego
        for x in range(128, 1250, 256):
            moneda = arcade.Sprite(":resources:images/items/coinGold.png", escalaMonedas)
            moneda.center_x = x
            moneda.center_y = 96
            self.monedas_lista.append(moneda)

        """
        

        #Cargar plataformas del mapa tmx
        if nivel==1:
            map_name = "mapa_1.tmx"
            arcade.set_background_color(arcade.csscolor.DARK_SLATE_GREY)
        elif nivel==2:
            map_name = "mapa_2.tmx"
            arcade.set_background_color(arcade.csscolor.DARK_SALMON)
        elif nivel==3:
            map_name = "mapa_3.tmx"
            arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        
        
        platforms_layer_name1 = 'plataform'
        mi_mapa=arcade.read_tmx(map_name)
        self.obstaculos_lista=arcade.tilemap.process_layer(map_object=mi_mapa,
                                                      layer_name=platforms_layer_name1,
                                                      scaling=escalaObstaculos,
                                                      use_spatial_hash=True)
        
        #Cargar las monedas del mapa tmx
        monedas_layer_name = 'monedas'
        self.monedas_lista=arcade.tilemap.process_layer(map_object=mi_mapa,
                                                      layer_name=monedas_layer_name,
                                                      scaling=escalaMonedas,
                                                      use_spatial_hash=True)

        #Cargar elemento instakill del mapa tmx
        lava_layer_name = 'kill'
        self.muerte_lista=arcade.tilemap.process_layer(map_object=mi_mapa,
                                                      layer_name=lava_layer_name,
                                                      scaling=escalaObstaculos,
                                                      use_spatial_hash=True)      

        #Cargar bandera del mapa tmx
        bandera_layer_name = 'Terminar'
        self.banderas_lista=arcade.tilemap.process_layer(map_object=mi_mapa,
                                                      layer_name=bandera_layer_name,
                                                      scaling=escalaObstaculos,
                                                      use_spatial_hash=True)  

        #Cargar elementos del fondo  del mapa tmx
        fondo_layer_name = 'fondo'
        self.fondo_lista=arcade.tilemap.process_layer(mi_mapa,fondo_layer_name,escalaObstaculos)                                       

        #Iniciar las físicas del juego 
        self.motor_fisica = arcade.PhysicsEnginePlatformer(self.jugador_sprite,self.obstaculos_lista,gravedad)


       
                
    #Dibujar en la pantalla  
    def on_draw(self):
        arcade.start_render()
        self.jugador_lista.draw()
        self.obstaculos_lista.draw()
        self.monedas_lista.draw()
        self.muerte_lista.draw()
        self.fondo_lista.draw()
        self.banderas_lista.draw()
        #Puntaje de la lista 
        puntaje_txt= f"Puntaje: {self.puntaje}"
        arcade.draw_text(puntaje_txt, 10 + self.vista_izquierda, 10 + self.vista_abajo,
                         arcade.csscolor.WHITE, 18)

        vida_txt= f"Vidas: {self.vidas}"
        arcade.draw_text(vida_txt, 150 + self.vista_izquierda, 10 + self.vista_abajo,
                         arcade.csscolor.WHITE, 18)


    #Mirar si el usuario oprime una tecla 
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            if self.motor_fisica.can_jump():
                self.jugador_sprite.change_y = velocidad_salto_personaje
                #Sonido de salto
                arcade.play_sound(self.salto_sonido)
        elif key == arcade.key.LEFT:
            self.jugador_sprite.change_x = -velocidad_personaje
        elif key == arcade.key.RIGHT:
            self.jugador_sprite.change_x = velocidad_personaje
    

    #Realizar movimiento cuando la tecla es oprimida y no sea infinito
    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.jugador_sprite.change_x = 0
    

    #Movimiento y fisicas del juego 
    def on_update(self, delta_time):
        #Cargar físicas
        self.motor_fisica.update()
        
        #Recragra las animaciones del personaje 
        if self.motor_fisica.can_jump():

            self.jugador_sprite.can_jump = False
        else:
            self.jugador_sprite.can_jump = True

        self.jugador_lista.update_animation(delta_time)

        #Recolectar monedas 
        moneda_lista_colision= arcade.check_for_collision_with_list(self.jugador_sprite,self.monedas_lista)
        
        for moneda in moneda_lista_colision:
            # Quitar la moneda 
            moneda.remove_from_sprite_lists()
            # Sonido 
            arcade.play_sound(self.coger_monedas_sonido)
            self.puntaje+=1
        
        #Siguiente mapa 
        bandera_lista_colision= arcade.check_for_collision_with_list(self.jugador_sprite,self.banderas_lista)
        for bandera in bandera_lista_colision:
            bandera.remove_from_sprite_lists()
            self.nivel +=1
            if self.nivel!=4:
                self.setup(self.nivel,self.puntaje,self.vidas)
                # Poner la cámara en el inicio 
                self.vista_izquierda = 0
                self.vista_abajo= 0
            else:
                view = WinView()
                self.window.show_view(view)


        #Reiniciar el jugador si el jugador toca la lava o pinchos 
        if arcade.check_for_collision_with_list(self.jugador_sprite,self.muerte_lista):
            self.jugador_sprite.change_x = 0
            self.jugador_sprite.change_y = 0
            self.jugador_sprite.center_x = 32
            self.jugador_sprite.center_y = 200

            # Poner la cámara en el inicio 
            self.vista_izquierda = 0
            self.vista_abajo= 0
            arcade.play_sound(self.game_over)
            self.vidas=self.vidas-1
        
        
        #Reiniciar el jugador  si el jugador se cae del mapa 
        if self.jugador_sprite.center_y < -100:
            self.jugador_sprite.change_x = 0
            self.jugador_sprite.change_y = 0
            self.jugador_sprite.center_x = 32
            self.jugador_sprite.center_y = 200

            # Poner la cámara en el inicio 
            self.vista_izquierda= 0
            self.vista_abajo= 0
            arcade.play_sound(self.game_over)
            self.vidas=self.vidas-1

        #Poner pantalla de Game over 
        if self.vidas ==0:
            view = GameOverView()
            self.window.show_view(view) 
            
    
        # Movimiento de la pantalla 
        cambios = False

        # Mover Izquierda
        limite_izquierda = self.vista_izquierda + margen_lado_izquierda
        if self.jugador_sprite.left < limite_izquierda:
            self.vista_izquierda -= limite_izquierda - self.jugador_sprite.left
            cambios = True

        # Mover derecha 
        limite_derecha = self.vista_izquierda + anchoPantalla- margen_lado_derecha
        if self.jugador_sprite.right > limite_derecha:
            self.vista_izquierda += self.jugador_sprite.right - limite_derecha
            cambios = True

        # Mover arriba 
        limite_arriba = self.vista_abajo+ largoPantalla- margen_lado_arriba
        if self.jugador_sprite.top > limite_arriba:
            self.vista_abajo += self.jugador_sprite.top - limite_arriba
            cambios = True

        # Mover abajo
        limite_abajo = self.vista_abajo + margen_lado_abajo
        if self.jugador_sprite.bottom < limite_abajo:
            self.vista_abajo -= limite_abajo - self.jugador_sprite.bottom
            cambios = True

        if cambios:
            
            self.vista_abajo = int(self.vista_abajo)
            self.vista_izquierda = int(self.vista_izquierda)

            # Hacer el movimiento 
            arcade.set_viewport(self.vista_izquierda,anchoPantalla + self.vista_izquierda,self.vista_abajo,largoPantalla + self.vista_abajo)
                                


def main():
    window = arcade.Window(anchoPantalla, largoPantalla, tituloJuego)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()

if __name__=="__main__":
    main()

