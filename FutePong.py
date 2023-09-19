from PPlay.window import *
from PPlay.gameimage import *
from PPlay.sprite import *
import random

janela = Window(900, 600)
janela.set_title("FutePong!")
teclado = Window.get_keyboard()

fundo = GameImage("Futepong/fundo.png")
brasil = GameImage("Futepong/brasil.png")
argentina = GameImage("Futepong/argentina.png")

#Posição das bandeiras
brasil.x = 350
brasil.y = 5
argentina.x = 500
argentina.y = 5

#Posição da bola
bola = Sprite("Futepong/bola.png",1)
bola.x = (janela.width/2)-(bola.width/2)
bola.y = (janela.height/2)-(bola.height/2)

#Posição dos jogadores
messi = Sprite("Futepong/messi.png",1)
neymar = Sprite("Futepong/neymar.png",1)
neymar.x = 5
neymar.y = (janela.height/2)-(neymar.height/2)
messi.x = (janela.width)-(messi.width) - 5
messi.y = (janela.height/2)-(messi.height/2)

#Velocidades de cada sprite
velocidade_neymar = 300
velocidade_messi = 300
velocidade_x = 300
velocidade_y = 300

#Gols
ponto_neymar = 0
ponto_messi = 0

#FPS
relogio = 0
contador = 0
fps = 0

#Boost
boost = Sprite("Futepong/boost.png",1)
boost.x = random.randint(200, 500)
boost.y = random.randint(100, 500)

while True:
#Entrada de Dados

    #Movimentação do jogador
    if (teclado.key_pressed("W")):
        if (neymar.y >= 0):
            neymar.y = neymar.y - velocidade_neymar * janela.delta_time()

    if (teclado.key_pressed("S")):
        if ((neymar.y + neymar.height) <= janela.height):
            neymar.y = neymar.y + velocidade_neymar * janela.delta_time()

    #Movimentação da IA
    messi.y += (velocidade_y * 0.6) * janela.delta_time()

#Uptade dos Game Objects e Física do jogo

    #Gol do Neymar
    bola.x = bola.x + velocidade_x * janela.delta_time()
    if((bola.x + bola.width) >= janela.width):
        ponto_neymar += 1 #Soma 1 gol
        #Reinicialização da velocidade e posição da bola e dos jogadores
        velocidade_x = 300
        velocidade_y = 300
        bola.x = (janela.width/2) - (bola.width/2)
        bola.y = (janela.height/2) - (bola.height/2)
        neymar.x = 5
        neymar.y = (janela.height/2)-(neymar.height/2)
        messi.x = (janela.width)-(messi.width) - 5
        messi.y = (janela.height/2)-(messi.height/2)
        
    # Gol do Messi
    if (bola.x < 0):
        ponto_messi += 1 #Soma 1 gol
        #Reinicialização da velocidade e posição da bola e dos jogadores
        velocidade_x = -300
        velocidade_y = 300
        bola.x = (janela.width/2) - (bola.width/2)
        bola.y = (janela.height/2) - (bola.height/2)
        neymar.x = 5
        neymar.y = (janela.height/2)-(neymar.height/2)
        messi.x = (janela.width)-(messi.width) - 5
        messi.y = (janela.height/2)-(messi.height/2)


    bola.y = bola.y + velocidade_y * janela.delta_time()

    #Utilizações do boost
    if(boost.collided(bola)):
        velocidade_x = velocidade_x * 1.1 #Aumenta a velocidade da bola e da IA
        velocidade_y = velocidade_y * 1.1 #Aumenta a velocidade da bola e da IA
        boost.x = random.randint(200, 500)
        boost.y = random.randint(100, 500)

    #Jogador chuta a bola
    if(neymar.collided(bola)):
        bola.x = neymar.width + bola.width
        velocidade_x = velocidade_x * -1

    if(messi.collided(bola)):
        bola.x = janela.width - messi.width - (2*bola.width)
        velocidade_x = velocidade_x * -1

    #Bola batendo nas laterais do campo
        #Em baixo
    if(bola.y > (janela.height - bola.height)):
        velocidade_y = velocidade_y*(-1)
        bola.y = (janela.height - bola.height)

        #Em cima
    if(bola.y <= 0):
        velocidade_y = velocidade_y*(-1)
        bola.y = 0
        
    #Calculo FPS
    relogio += janela.delta_time()
    contador += 1  
    if relogio >= 1:
        relogio = 0
        fps = contador
        contador = 0
        
#Desenho dos Game Objects
    fundo.draw()
    bola.draw()
    neymar.draw()
    messi.draw()
    boost.draw()
    brasil.draw()
    argentina.draw()
    janela.draw_text("FPS: "+str(fps)+"",(janela.width - 90), 5, size=20, color=(0,0,0), font_name="Arial", bold=True, italic=False)
    janela.draw_text(""+str(ponto_neymar)+" X "+str(ponto_messi)+"", (janela.height/2)+115, 5, size=30, color=(0,0,0), font_name="Arial", bold=True, italic=False)
    
    janela.update()