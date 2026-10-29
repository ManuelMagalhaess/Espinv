from PPlay.window import *
from PPlay.gameimage import *
from PPlay.sprite import *
from PPlay.sound import *
from PPlay.mouse import *
import time
import random
import datetime
from PIL import Image

Image.open("nave.png").resize((84, 64)).save("nave.png")

# Janela
janela = Window(1000, 600)
janela.set_title("espace invaderrrs")

# Teclado e mouse
teclado = Window.get_keyboard()
mouse = Window.get_mouse()

# Botoes
jogar = Sprite("jogar.png")
jogar.set_position((janela.width - jogar.width)/2, (janela.height - jogar.height)/2 - jogar.width/2)
dif = Sprite("dif.png")
dif.set_position((janela.width - dif.width)/2, (janela.height - dif.height)/2)
rank = Sprite("rank.png")
rank.set_position((janela.width - rank.width)/2, (janela.height - rank.height)/2 + rank.width/2)
sair = Sprite("sair.png")
sair.set_position((janela.width - sair.width)/2, (janela.height - sair.height)/2 + sair.width)
facil = Sprite("facil.png")
medio = Sprite("medio.png")
dificil = Sprite("dificil.png")

nave = Sprite("nave.png")

difjogo = 0.4

def salvar_ranking(pontos):
    if pontos > 0:
        print(f"Sua Pontuação Final: {pontos}")
    
        janela.update() 
        
        nome = input("Insira seu nome para o Ranking (max 10 caracteres): ")
        nome = nome[:10].strip() # Limita o nome a 10 caracteres
        
        data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        linha = f"{nome};{pontos};{data_atual}\n"

        with open("ranking.txt", "a") as arquivo:
            arquivo.write(linha)

def mostrar_ranking(janela):

    dados_ranking = []
    try:
        with open("ranking.txt", "r") as arquivo:
            for linha in arquivo:
                partes = linha.strip().split(';')
                if len(partes) == 3:
                    nome, pontos_str, data = partes
                    try:
                        pontos = int(pontos_str)
                        dados_ranking.append({"nome": nome, "pontos": pontos, "data": data})
                    except ValueError:
                        continue
    except FileNotFoundError:
        pass
        
    # Ordenação do maior para o menor
    dados_ranking.sort(key=lambda item: item['pontos'], reverse=True)
    
    while not teclado.key_pressed("esc"):
        janela.set_background_color((0, 0, 0))
        janela.draw_text("TOP 5 RANKING", (janela.width - 150) / 2, 50, 30, (255, 255, 255))
        
        y_pos = 120
        
        if not dados_ranking:
            janela.draw_text("Nenhum registro encontrado.", (janela.width - 300) / 2, y_pos, 22, (255, 255, 0))
        else:
            # Exibe apenas o Top 5
            for i, jogador in enumerate(dados_ranking[:5]): 
                texto = f"{i + 1}. {jogador['nome']:<10} | PONTOS: {jogador['pontos']!s:<5} | DATA: {jogador['data']}"
                janela.draw_text(texto, 150, y_pos, 22, (255, 255, 255))
                y_pos += 40
                
        janela.draw_text("Pressione ESC para voltar ao Menu", (janela.width - 250) / 2, janela.height - 50, 20, (0, 255, 0))
        janela.update()


def menu():
    if mouse.is_over_object(jogar) and mouse.is_button_pressed(1):
        return "jogar"
    elif mouse.is_over_object(dif) and mouse.is_button_pressed(1):
        return "dificuldade"
    elif mouse.is_over_object(rank) and mouse.is_button_pressed(1):
        return "ranking"
    elif mouse.is_over_object(sair) and mouse.is_button_pressed(1):
        janela.close()
    return "menu"

def jogo():
    global difjogo

    nave.set_position((janela.width - nave.width)/2, (janela.height - nave.height))

    pontos = 0
    vidas = 3
    
    fase = 0 
    vel_monstro = 200 
    recarga_inimigo_base = 1.3 
    variacao = 0.8 
    
    monstros = []
    
    def cria_horda(fase_atual):
        L_base = 3
        C_base = 5

        L = L_base + (fase_atual - 1)
        max_linhas = 6
        if L > max_linhas:
            L = max_linhas
            
        C = C_base
        
        vel_monstro_novo = 200 * (1 + (fase_atual - 1) * 0.2) 
        
        recarga_inimigo_nova = 1.3 - (fase_atual - 1) * 0.15 
        if recarga_inimigo_nova < 0.3:
            recarga_inimigo_nova = 0.3
            
        nova_horda = []
        for i in range(C * L):
            alien = Sprite("alien.png")
            alien.set_position(alien.width * (i % C), alien.width * (i // C))
            nova_horda.append(alien)
            
        return nova_horda, vel_monstro_novo, recarga_inimigo_nova

    fps = 0
    tempo = 0
    frames = 0
    tiros = []
    tiros_inimigos = []
    tempo_recarga = difjogo 
    ultimo_tiro = time.time()
    vel_tiro = 500
    ultimo_tiro_inimigo = time.time()
    invencivel = False
    tempo_invencivel = 0
    
    fase = 1
    monstros, vel_monstro, recarga_inimigo_base = cria_horda(fase)

    while True:
        janela.set_background_color((0,0,0))

        if not monstros:
            fase += 1
            
            tiros = [] 
            tiros_inimigos = []
            nave.set_position((janela.width - nave.width)/2, (janela.height - nave.height))
            
            # Gera nova horda e atualiza a dificuldade
            monstros, vel_monstro, recarga_inimigo_base = cria_horda(fase)
            janela.update()
            time.sleep(1.5)

        if teclado.key_pressed("right") and nave.x <= janela.width - nave.width:
            nave.move_key_x(300 * janela.delta_time())
        if teclado.key_pressed("left") and nave.x >= 0:
            nave.move_key_x(300 * janela.delta_time())


        # Tiro do Player
        if teclado.key_pressed("space"):
            tempo_atual = time.time()
            if tempo_atual - ultimo_tiro >= tempo_recarga:
                tiro = Sprite("tiro.png")
                tiro.set_position(nave.x + nave.width / 2 - tiro.width / 2, nave.y - tiro.height)
                tiros.append(tiro)
                ultimo_tiro = tempo_atual

        # Atualizar tiros do player
        for tiro in tiros[:]:
            tiro.y -= vel_tiro * janela.delta_time()
            tiro.draw()

            if tiro.y + tiro.height < 0:
                tiros.remove(tiro)

        tempo_atual = time.time()
        intervalo_randomizado = recarga_inimigo_base + random.uniform(-variacao, variacao) 

        if monstros and tempo_atual - ultimo_tiro_inimigo >= intervalo_randomizado:

            alien = random.choice(monstros)
            tiro_i = Sprite("tiro.png")
            tiro_i.set_position(alien.x + alien.width//2, alien.y + alien.height)
            tiros_inimigos.append(tiro_i)
            ultimo_tiro_inimigo = tempo_atual


        for tiro in tiros_inimigos[:]:
            tiro.y += vel_tiro * janela.delta_time()
            tiro.draw()
            if tiro.y > janela.height:
                tiros_inimigos.remove(tiro)

            if not invencivel and tiro.collided(nave):
                tiros_inimigos.remove(tiro)
                vidas -= 1
                
                nave.set_position((janela.width - nave.width)/2, (janela.height - nave.height))

                # Ativa invencibilidade
                invencivel = True
                tempo_invencivel = time.time()

                # Game Over por vidas
                if vidas <= 0:
                    salvar_ranking(pontos)
                    return "menu" 

        # Desliga invencibilidade após 2s
        if invencivel and time.time() - tempo_invencivel >= 2:
            invencivel = False

        moveu_borda = False
        for alien in monstros[:]:
            alien.x += vel_monstro * janela.delta_time()
            alien.draw()

            if alien.x + alien.width >= janela.width or alien.x <= 0:
                moveu_borda = True
        
        if moveu_borda:
            vel_monstro *= -1 
            for alien in monstros:
                alien.y += alien.width

        aliens_a_remover = []
        tiros_a_remover = []

        for tiro in tiros:
            for alien in monstros:
                if tiro.collided(alien):
                    aliens_a_remover.append(alien)
                    tiros_a_remover.append(tiro)
                    pontos += 5
                    break

        for tiro in tiros_a_remover:
            if tiro in tiros:
                tiros.remove(tiro)
        for alien in aliens_a_remover:
            if alien in monstros:
                monstros.remove(alien)
        
        if monstros and min(a.y + a.height for a in monstros) >= nave.y:
            salvar_ranking(pontos)
            return "menu" 

        # Cálculo do FPS
        tempo += janela.delta_time()
        frames += 1
        if tempo >= 1:
            fps = frames
            frames = 0
            tempo = 0

        janela.draw_text(f"FPS: {fps}", 10, 10, 20, (255,255,255))
        janela.draw_text(f"PONTOS: {pontos}", 850, 10, 20, (255,255,255))
        janela.draw_text(f"VIDAS: {vidas}", 10, 40, 22, (255, 0, 0))
        janela.draw_text(f"FASE: {fase}", 450, 10, 22, (255, 255, 255))

        # Player pisca quando invencível
        if not invencivel or int(time.time()*10) % 2 == 0:
            nave.draw()

        janela.update()
    
    return

def dificuldade():
    global difjogo
    
    while True:
        janela.set_background_color((0,0,0))
        
        facil.set_position((janela.width - facil.width)/2, (janela.height - facil.height)/2 - facil.width/2)
        medio.set_position((janela.width - medio.width)/2, (janela.height - medio.height)/2)
        dificil.set_position((janela.width - dificil.width)/2, (janela.height - dificil.height)/2 + dificil.width/2)

        facil.draw()
        medio.draw()
        dificil.draw()
        janela.update()

        if mouse.is_over_object(facil) and mouse.is_button_pressed(1):
            difjogo = 0.7
            break
        elif mouse.is_over_object(medio) and mouse.is_button_pressed(1):
            difjogo = 0.4
            break
        elif mouse.is_over_object(dificil) and mouse.is_button_pressed(1):
            difjogo = 0.3
            break

        if teclado.key_pressed("esc"):
            break


estado_jogo = "menu"
while True:
    janela.set_background_color((0,0,0))
    
    if estado_jogo == "menu":
        jogar.draw()
        dif.draw()
        rank.draw()
        sair.draw()

        estado_jogo = menu()
        
    elif estado_jogo == "jogar":
        estado_jogo = jogo()
        
    elif estado_jogo == "dificuldade":
        dificuldade()
        estado_jogo = "menu"

    elif estado_jogo == "ranking":
        mostrar_ranking(janela)
        estado_jogo = "menu"
        
    janela.update()