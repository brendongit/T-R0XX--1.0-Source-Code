import json
import math
import os
import time
import multiprocessing
from typing import Callable
import cv2
import numpy as np
import win32con
import win32gui
import win32ui
import win32api
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from keyboard import send
from mouse import *
from pointers import Pointers
import ctypes

cords_team = {
    "yourself": [0, 0],
    "member_1": [0, 0],
    "member_2": [0, 0],
    "member_3": [0, 0],
    "member_4": [0, 0],
}

cords_move = {
    "stop": [0, 0],
    "right": [0, 0],
    "left": [0, 0],
    "up": [0, 0],
    "down": [0, 0],
    "minimize": [0, 0],
    "mouse_reset": [0, 0],
}

cords_game = {
    "deleter_ok": [0, 0],
    "jackstraw_ok": [0, 0],
    "revive_ok": [0, 0],
    "pick_up_all": [0, 0]
}


def set_coords_by_resolution(resolution):
    global cords_team, cords_move, cords_game

    if resolution == "1024*768":
        cords_move.update({
            "stop": [919, 115],
            "right": [920, 115],
            "left": [918, 115],
            "up": [919, 114],
            "down": [919, 116],
            "minimize": [995, 126],
            "mouse_reset": [900, 182],
        })

        cords_team.update({
            "yourself": [45, 45],
            "member_1": [30, 210],
            "member_2": [30, 285],
            "member_3": [30, 365],
            "member_4": [30, 445],
        })

        cords_game.update({
            "deleter_ok": [439, 335],
            "jackstraw_ok": [439, 336],
            "revive_ok": [515, 469],
            "pick_up_all": [400, 400],
        })

    else:
        raise ValueError(f"Resolução não suportada: {resolution}")


def start_game_process(config, stop_event):
    set_coords_by_resolution(config.resolution)

    if config.minimized_mode == "ON" and config.deleter_bot == "OFF":
        hwnd = win32gui.FindWindow(None, config.char_name)
        if hwnd:
            placement = win32gui.GetWindowPlacement(hwnd)
            if not placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    if config.minimized_mode == "OFF":
        hwnd = win32gui.FindWindow(None, config.char_name)
        if hwnd:
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(1)

    while not stop_event.is_set():
        try:
            bot(config)
        except Exception as e:
            print(f"Erro no subprocesso PID={config.pid}: {e}")
            break


def bot(config):
    global safe_spot, get_back_enable

    get_back_enable = 0
    x, y = Pointers(config.pid).get_x(), Pointers(config.pid).get_y()
    safe_spot = [x, y]
    print(f"Start = {safe_spot}")

    manager = CycleManager()
    if config.deleter_bot == "ON":
        manager.add_cycle(deleter(config), config.deleter_delay, "Ciclo de Deleter")

    if config.get_back == "ON":
        for _ in range(5):
            left(config.hwnd, int(cords_move["minimize"][0]), int(cords_move["minimize"][1]))
            time.sleep(0.1)

    manager.add_cycle(use_pet_food(config), config.pet_food_delay, "Ciclo de Pet Food")

    if config.get_back == "ON":
        get_back_enable = 1

    while True:
        if config.get_back == "ON":
            check_distance(config, safe_spot)
        manager.execute_cycles()

        if config.char_type == "Stamina":
            tab(config)
            kill(config)
            stamina_cure(config)
            dead(config)


def tab_santa(config):
    if config.kill_santa == "OFF":
        while True:
            if Pointers(config.pid).get_target_name() == "Santa Mushroom":
                send(config.hwnd, "TAB")
            else:
                break


def check_distance(config, xY):
    while True:
        get_x = Pointers(config.pid).get_x()
        get_y = Pointers(config.pid).get_y()
        print(f"Posição inicial: {xY}, Posição atual: ({get_x}, {get_y})")

        current_distance = math.sqrt((get_x - xY[0]) ** 2 + (get_y - xY[1]) ** 2)
        print(f"Distância atual: {current_distance:.2f} m, Limite: {config.distance} m")

        if current_distance >= config.distance:
            print(f"Distância {current_distance} excede o limite! Reposicionando...")
            if current_distance >= 50:
                go_to_spot(config)
            safe_spot_back(config, xY)

        if current_distance <= config.distance:
            print("Dentro do limite, sem movimentação.")
            time.sleep(0.1)
            return


def safe_spot_back(config, xY, tolerance=2):
    while True:
        dead(config)
        get_x = Pointers(config.pid).get_x()
        get_y = Pointers(config.pid).get_y()
        time.sleep(0.1)

        if abs(get_x - xY[0]) <= tolerance and abs(get_y - xY[1]) <= tolerance:
            break

        x, y = get_x, get_y
        via = [cords_move["stop"][0], cords_move["stop"][1]]
        repos = [x - xY[0], y - xY[1]]
        time.sleep(0.1)

        if repos[0] != 0 or repos[1] != 0:
            if repos[0] != 0:
                via[0] -= repos[0]
                time.sleep(0.1)
            if repos[1] != 0:
                via[1] += repos[1]
                time.sleep(0.1)

            right(config.hwnd, int(via[0]), int(via[1]))
            wait_while_moving(config)

    left(config.hwnd, int(cords_move["mouse_reset"][0]), int(cords_move["mouse_reset"][1]))
    time.sleep(0.1)


def wait_while_moving(config):
    countspot = 0
    prevX, prevY = None, None

    while True:
        x = Pointers(config.pid).get_x()
        y = Pointers(config.pid).get_y()
        if prevX == x and prevY == y:
            countspot += 1
            if countspot >= 4:
                tab(config)
                time.sleep(0.1)
                break
        else:
            countspot = 0

        prevX, prevY = x, y
        time.sleep(0.2)


def buff_up(config):
    def inner():
        print("Using Buff")
        if config.char_type == "Stamina":
            send(config.hwnd, config.buff_1), time.sleep(1)
            send(config.hwnd, config.buff_2), time.sleep(1)
    return inner


def use_pet_food(config):
    def inner():
        time.sleep(1)
        print("Using Pet Food")
        send(config.hwnd, config.pet_food), time.sleep(0.1)
    return inner


def kill(config):
    stickness = 0
    stuck_count = 0
    stuck = config.unstuck_speed

    while not Pointers(config.pid).is_target_dead():
        if Pointers(config.pid).target_hp() >= target_hp_percentage(45):
            send(config.hwnd, config.skill_1), time.sleep(0.2)
            send(config.hwnd, config.skill_2), time.sleep(0.2)
            send(config.hwnd, config.skill_3), time.sleep(0.2)
        else:
            send(config.hwnd, config.skill_4), time.sleep(0.2)
            send(config.hwnd, config.skill_5), time.sleep(0.2)
            send(config.hwnd, config.skill_6), time.sleep(0.2)

        if stickness >= stuck:
            print(f"Unstuck count: {stuck_count}:")
            if stuck_count == 2:
                go_to_spot(config)
                stuck_count = 0
            else:
                stuck_count = stuck_count + 1
                send(config.hwnd, "TAB")
                tab_santa(config)
                time.sleep(0.2)
            stickness = 0

        if Pointers(config.pid).target_hp_full() or not Pointers(config.pid).is_target_selected():
            stickness = stickness + 1

        dead(config)

    # 🎯 SISTEMA OTIMIZADO DE LOOT PULL
    if config.autopick_enabled == "ON":
        try:
            print("\n🔥 MOB MORREU - SISTEMA DE LOOT PULL RÁPIDO 🔥")
            
            # Aguarda loot aparecer (tempo reduzido)
            print("⏳ Aguardando loot...")
            time.sleep(0.6)  # Reduzido de 0.8 para 0.6
            
            # Sistema principal mais rápido e confiável
            success = False
            
            # Tenta o sistema de empilhamento otimizado primeiro
            try:
                print("🎯 Executando sistema otimizado...")
                success = stack_loot_on_player(config)
            except Exception as e:
                print(f"⚠️ Sistema principal falhou: {e}")
                success = False
            
            # Se falhar, tenta sistema direto como backup
            if not success:
                try:
                    print("🔄 Tentando sistema backup...")
                    success = direct_loot_pull(config)
                except Exception as e:
                    print(f"⚠️ Sistema backup falhou: {e}")
                    success = False
            
            # Se ambos falharam, pelo menos executa o autopick básico
            if not success:
                try:
                    print("🆘 Executando autopick básico...")
                    quick_autopick_system(config)
                except Exception as e:
                    print(f"❌ Autopick básico falhou: {e}")
            
            print("🏁 Sistema de loot concluído\n")
            
        except Exception as e:
            print(f"❌ Erro geral no sistema de loot: {e}")


def emergency_autopick(config):
    """
    Sistema de emergência para autopick quando tudo mais falha
    """
    try:
        print("🆘 AUTOPICK DE EMERGÊNCIA")
        hwnd = config.hwnd
        
        # Usa posição configurada pelo usuário como fallback
        pick_x = config.autopick_x
        pick_y = config.autopick_y
        
        print(f"🎯 Posição de emergência: ({pick_x}, {pick_y})")
        
        lParam = (pick_y << 16) | (pick_x & 0xFFFF)
        
        # Execução simples e direta
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.1)
        
        for i in range(3):
            win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
            time.sleep(0.05)
            win32api.SendMessage(hwnd, 0x0205, 0, lParam)
            time.sleep(0.1)
        
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ Autopick de emergência concluído")
        return True
        
    except Exception as e:
        print(f"❌ Falha no autopick de emergência: {e}")
        return False


def optimized_loot_detection(config):
    """
    Sistema otimizado para detectar e processar loot rapidamente
    """
    try:
        pointers = Pointers(config.pid)
        
        # Detecção rápida de objetos próximos
        objects_found = 0
        
        for quick_scan in range(5):  # Scan rápido
            try:
                obj_x, obj_y, obj_pointer = pointers.search_id()
                
                if obj_pointer is not None:
                    player_x = pointers.get_x()
                    player_y = pointers.get_y()
                    
                    if player_x and player_y:
                        distance = math.sqrt((obj_x - player_x) ** 2 + (obj_y - player_y) ** 2)
                        
                        if distance <= 10:  # Objeto próximo
                            objects_found += 1
                
            except Exception:
                continue
        
        print(f"🔍 Detecção rápida: {objects_found} objetos próximos encontrados")
        return objects_found > 0
        
    except Exception as e:
        print(f"Erro na detecção: {e}")
        return False
    
def tab(config):
    if Pointers(config.pid).is_target_dead():
        send(config.hwnd, "TAB")
        tab_santa(config)
        print(Pointers(config.pid).get_target_name())
        time.sleep(0.2)

    if not Pointers(config.pid).is_target_selected():
        send(config.hwnd, "TAB")
        tab_santa(config)
        time.sleep(0.2)


def stamina_cure(config):
    low_hp = config.low_hp
    hp_p = hp_percentage(config)

    if hp_p <= low_hp:
        print("HP is Bellow the Percentage", low_hp, hp_p)
        if Pointers(config.pid).is_in_battle():
            while not Pointers(config.pid).is_target_dead():
                kill(config)
            print("Waiting 2 seconds to leave battle")
            if Pointers(config.pid).is_target_selected() and Pointers(config.pid).is_target_dead():
                send(config.hwnd, "ESC")
            time.sleep(0.2)

        if config.get_back == "ON" and Pointers(config.pid).get_team_size() >= 2:
            safe_spot_back(config, safe_spot)
            print("Safe Spot Back")

        print("Sitting to recover HP")
        sit(config), time.sleep(2)
        send(config.hwnd, config.potion_hp)
        dead(config)

        timer = QTimer()
        timer.setInterval(15000)
        timer.start()
        start_time = time.time()

        while Pointers(config.pid).get_hp() < Pointers(config.pid).get_max_hp() - 10:
            time.sleep(1)
            elapsed_time = time.time() - start_time
            if elapsed_time >= 15 and Pointers(config.pid).get_hp() < Pointers(config.pid).get_max_hp() - 10:
                send(config.hwnd, config.potion_hp)
                print("Timer expired: sent potion command")
                start_time = time.time()
            if Pointers(config.pid).is_in_battle():
                print("Someone is hitting me!")
                kill(config)
            sit(config)
            dead(config)


def hp_percentage(config):
    max_hp = Pointers(config.pid).get_max_hp()
    current_hp = Pointers(config.pid).get_hp()
    percentage = (current_hp / max_hp) * 100
    rounded_percentage = round(percentage, 2)
    return rounded_percentage


def target_hp_percentage(pct):
    hp_min = 460
    hp_max = 137
    return hp_min + hp_max * (pct / 100)


def sit(config):
    if not Pointers(config.pid).is_sitting():
        send(config.hwnd, config.sit), time.sleep(0.1)


def dead(config):
    if Pointers(config.pid).get_hp() == 0:
        if get_back_enable == 1:
            print("Setting Get Back OFF")
            config.get_back = "OFF"

        print(f"Char {Pointers(config.pid).get_char_name()} is dead!")
        time.sleep(2)
        left(config.hwnd, int(cords_game["jackstraw_ok"][0]), int(cords_game["jackstraw_ok"][1]))
        time.sleep(2)
        if Pointers(config.pid).get_hp() == 0:
            left(config.hwnd, int(cords_game["revive_ok"][0]), int(cords_game["revive_ok"][1]))
            time.sleep(2)
        sit(config)

        if config.revive_and_back == "ON":
            if config.char_type == "Stamina":
                stamina_cure(config)
            go_to_spot(config)


def go_to_spot(config):
    send(config.hwnd, config.map), time.sleep(1)

    coords = config.spot_farm.split(",")
    x = int(coords[0])
    y = int(coords[1])

    right(config.hwnd, x - 20, y - 20)
    time.sleep(0.2)
    right(config.hwnd, x + 20, y + 20)
    time.sleep(0.2)
    right(config.hwnd, x, y)
    time.sleep(1)
    send(config.hwnd, config.map), time.sleep(1)
    wait_until_farm_spot(config)


def wait_until_farm_spot(config):
    countspot = 0
    prevX, prevY = None, None

    while True:
        x = Pointers(config.pid).get_x()
        y = Pointers(config.pid).get_y()
        if prevX == x and prevY == y:
            countspot += 1
            if countspot >= 3:
                tab(config)
                time.sleep(0.5)
                if Pointers(config.pid).is_target_selected():
                    print("Ready to start again !!!")
                    if get_back_enable == 1 and config.get_back == "OFF":
                        print("Setting Get Back ON")
                        config.get_back = "ON"
                    break
                else:
                    return go_to_spot(config)
        else:
            countspot = 0

        prevX, prevY = x, y
        time.sleep(1)


def smart_loot_pull(config):
    try:
        pointers = Pointers(config.pid)
        
        # Verifica se há loot usando método alternativo
        loot_value = pointers.read_value(pointers.LOOT_POINTER, data_type="int")
        if not loot_value or loot_value == 0:
            return False
            
        print("Loot detectado! Iniciando smart pull...")
        
        if pull_nearby_loot(config, radius=8):
            time.sleep(1)
            execute_autopick_collection(config)
            return True
            
        return False
        
    except Exception as e:
        print(f"Erro no smart loot pull: {e}")
        return False


def check_for_loot(pointers):
    """
    Função alternativa para verificar se há loot disponível
    """
    try:
        # Método 1: Verifica o ponteiro de loot
        loot_value = pointers.read_value(pointers.LOOT_POINTER, data_type="int")
        if loot_value and loot_value > 0:
            return True
            
        # Método 2: Verifica a janela de loot
        loot_window = pointers.loot_window()
        if loot_window:
            return True
            
        # Método 3: Verifica se há objetos próximos usando search_id
        target_x, target_y, object_pointer = pointers.search_id()
        if target_x is not None and object_pointer is not None:
            player_x = pointers.get_x()
            player_y = pointers.get_y()
            if player_x and player_y:
                distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)
                # Se há objetos muito próximos (provavelmente loot)
                if distance <= 10:
                    return True
                    
        return False
        
    except Exception as e:
        print(f"Erro ao verificar loot: {e}")
        return False


def pull_nearby_loot(config, radius=5):
    try:
        print(f"Buscando loot em um raio de {radius} metros...")
        pointers = Pointers(config.pid)
        
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        player_x = pointers.get_x()
        player_y = pointers.get_y()
        
        if char_x is None or char_y is None:
            print("Erro ao obter coordenadas do personagem")
            return False
            
        pulled_count = 0
        processed_objects = set()  # Para evitar processar o mesmo objeto múltiplas vezes
        
        for attempt in range(15):
            try:
                target_x, target_y, object_pointer = pointers.search_id()
                
                if target_x is None or object_pointer is None:
                    break
                
                # Cria um identificador único para o objeto baseado em sua posição
                object_id = f"{target_x}_{target_y}_{object_pointer}"
                
                if object_id in processed_objects:
                    continue
                    
                processed_objects.add(object_id)
                    
                distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)
                
                if 1 < distance <= radius:
                    print(f"Puxando loot #{pulled_count + 1} de distância {distance:.1f}m")
                    
                    angle = pulled_count * 45
                    offset_distance = 60
                    
                    new_x = char_x + offset_distance * math.cos(math.radians(angle))
                    new_y = char_y + offset_distance * math.sin(math.radians(angle))
                    
                    if pointers.write_position(object_pointer, new_x, new_y):
                        pulled_count += 1
                        print(f"Loot puxado para próximo do personagem (posição {pulled_count})")
                        time.sleep(0.3)
                    
                elif distance <= 1:
                    print(f"Loot já está muito próximo (distância: {distance:.1f}m)")
                    
            except Exception as e:
                print(f"Erro ao processar loot na tentativa {attempt + 1}: {e}")
                continue
                
        print(f"Total de {pulled_count} loots puxados")
        return pulled_count > 0
        
    except Exception as e:
        print(f"Erro na função pull_nearby_loot: {e}")
        return False


def simplified_loot_pull(config):
    """
    Versão simplificada que sempre tenta puxar objetos próximos
    """
    try:
        pointers = Pointers(config.pid)
        
        # Aguarda um pouco para garantir que o loot apareça
        time.sleep(0.5)
        
        print("Tentando puxar objetos próximos...")
        
        # Tenta puxar objetos sem verificação de loot
        if pull_nearby_loot(config, radius=10):
            time.sleep(1)
            execute_autopick_collection(config)
            return True
        else:
            # Se não puxou nada, ainda assim tenta o autopick
            execute_autopick_collection(config)
            return False
        
    except Exception as e:
        print(f"Erro no simplified loot pull: {e}")
        return False


def execute_autopick_collection(config):
    try:
        pick_x = config.autopick_x
        pick_y = config.autopick_y
        hwnd = config.hwnd
        
        print(f"Coletando itens com SHIFT + Click direito em ({pick_x}, {pick_y})")
        
        lParam = (pick_y << 16) | (pick_x & 0xFFFF)
        
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.1)
        
        for i in range(3):
            win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
            time.sleep(0.1)
            win32api.SendMessage(hwnd, 0x0205, 0, lParam)
            time.sleep(0.2)
            
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print("Coleta automática concluída")
        
    except Exception as e:
        print(f"Erro na coleta automática: {e}")

def get_player_screen_position(config):
    """
    Calcula a posição na tela onde o personagem aparece baseado nas coordenadas do mundo
    """
    try:
        pointers = Pointers(config.pid)
        
        # Obtém posição do personagem no mundo do jogo
        char_x = pointers.char_x()  # Coordenadas brutas
        char_y = pointers.char_y()  # Coordenadas brutas
        
        if char_x is None or char_y is None:
            return None, None
        
        # Para resolução 1024x768, o centro da tela onde o personagem aparece é aproximadamente:
        if config.resolution == "1024*768":
            center_x = 512  # Metade de 1024
            center_y = 384  # Metade de 768
        else:
            # Valores padrão para outras resoluções
            center_x = 400
            center_y = 300
        
        print(f"📍 Posição calculada do personagem na tela: ({center_x}, {center_y})")
        return center_x, center_y
        
    except Exception as e:
        print(f"Erro ao calcular posição do personagem: {e}")
        return None, None


def execute_autopick_at_player_position(config):
    """
    Executa autopick na posição exata onde o personagem aparece na tela
    """
    try:
        # Calcula onde o personagem aparece na tela
        player_screen_x, player_screen_y = get_player_screen_position(config)
        
        if player_screen_x is None or player_screen_y is None:
            print("❌ Não foi possível calcular posição do personagem na tela")
            return False
        
        hwnd = config.hwnd
        
        print(f"🎯 Executando SHIFT + Click direito na posição do personagem: ({player_screen_x}, {player_screen_y})")
        
        # Prepara o lParam com as coordenadas do personagem
        lParam = (player_screen_y << 16) | (player_screen_x & 0xFFFF)
        
        # Executa múltiplos clicks para garantir coleta
        for click_round in range(3):  # 3 rodadas
            print(f"   🔄 Rodada {click_round + 1} de clicks...")
            
            # Pressiona SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            time.sleep(0.05)
            
            # Múltiplos clicks direitos na posição do personagem
            for i in range(4):  # 4 clicks por rodada
                try:
                    # Envia mensagem diretamente para a janela (não depende do mouse físico)
                    win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
                    time.sleep(0.03)
                    win32api.SendMessage(hwnd, 0x0205, 0, lParam)
                    time.sleep(0.05)
                    
                    print(f"      ✅ Click {i+1} enviado")
                except Exception as e:
                    print(f"      ❌ Erro no click {i+1}: {e}")
                    continue
            
            # Solta SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)
        
        print("🎮 Autopick na posição do personagem concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no autopick dinâmico: {e}")
        return False


def execute_autopick_collection_enhanced(config):
    """
    Versão aprimorada que usa tanto a posição configurada quanto a posição do personagem
    """
    try:
        hwnd = config.hwnd
        success_count = 0
        
        print("🎯 Sistema de Autopick Aprimorado Iniciado")
        
        # Método 1: Click na posição do personagem (onde o loot foi puxado)
        print("\n📍 Método 1: Autopick na posição do personagem")
        if execute_autopick_at_player_position(config):
            success_count += 1
            time.sleep(0.5)  # Pausa entre métodos
        
        # Método 2: Click na posição configurada pelo usuário (backup)
        print("\n📍 Método 2: Autopick na posição configurada")
        pick_x = config.autopick_x
        pick_y = config.autopick_y
        
        print(f"🎯 Executando na posição configurada: ({pick_x}, {pick_y})")
        
        lParam = (pick_y << 16) | (pick_x & 0xFFFF)
        
        # Pressiona SHIFT
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.1)
        
        # Executa clicks na posição configurada
        for i in range(3):
            try:
                win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
                time.sleep(0.05)
                win32api.SendMessage(hwnd, 0x0205, 0, lParam)
                time.sleep(0.1)
                print(f"   ✅ Click {i+1} na posição configurada")
            except Exception as e:
                print(f"   ❌ Erro no click {i+1}: {e}")
        
        # Solta SHIFT
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)
        
        success_count += 1
        
        print(f"\n🏁 Autopick concluído - {success_count} métodos executados")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro no autopick aprimorado: {e}")
        return False


def calculate_game_center_coordinates(config):
    """
    Calcula as coordenadas do centro da tela do jogo baseado na resolução
    """
    resolution_configs = {
        "1024*768": {"center_x": 512, "center_y": 384, "offset_x": 0, "offset_y": 0},
        "1280*720": {"center_x": 640, "center_y": 360, "offset_x": 0, "offset_y": 0},
        "1280*800": {"center_x": 640, "center_y": 400, "offset_x": 0, "offset_y": 0},
        "1920*1080": {"center_x": 960, "center_y": 540, "offset_x": 0, "offset_y": 0},
    }
    
    resolution = config.resolution
    if resolution in resolution_configs:
        return resolution_configs[resolution]
    else:
        # Padrão para resoluções não mapeadas
        return {"center_x": 400, "center_y": 300, "offset_x": 0, "offset_y": 0}


def smart_autopick_system(config):
    """
    Sistema inteligente que combina loot pull + autopick na posição ideal
    """
    try:
        print("\n🧠 SISTEMA INTELIGENTE DE AUTOPICK")
        
        # 1. Primeiro garante que o loot está em cima do personagem
        print("🎯 Etapa 1: Verificando se loot está na posição do personagem...")
        
        pointers = Pointers(config.pid)
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        
        if char_x is None or char_y is None:
            print("❌ Não foi possível obter posição do personagem")
            return False
        
        print(f"📍 Personagem em: ({char_x:.0f}, {char_y:.0f})")
        
        # 2. Calcula posição ideal para autopick baseada no centro da tela
        resolution_config = calculate_game_center_coordinates(config)
        ideal_x = resolution_config["center_x"]
        ideal_y = resolution_config["center_y"]
        
        print(f"🎯 Posição ideal para autopick: ({ideal_x}, {ideal_y})")
        
        # 3. Executa autopick na posição ideal
        hwnd = config.hwnd
        lParam = (ideal_y << 16) | (ideal_x & 0xFFFF)
        
        print("🎮 Executando autopick na posição ideal...")
        
        success = True
        for round_num in range(2):  # 2 rodadas
            print(f"   🔄 Rodada {round_num + 1}...")
            
            # Pressiona SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            time.sleep(0.1)
            
            # Múltiplos clicks
            for click in range(5):  # 5 clicks por rodada
                try:
                    win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
                    time.sleep(0.02)
                    win32api.SendMessage(hwnd, 0x0205, 0, lParam)
                    time.sleep(0.08)
                    
                except Exception as e:
                    print(f"      ❌ Erro no click {click + 1}: {e}")
                    success = False
            
            # Solta SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)
        
        if success:
            print("✅ Sistema inteligente executado com sucesso")
        else:
            print("⚠️ Sistema inteligente executado com alguns erros")
            
        return success
        
    except Exception as e:
        print(f"❌ Erro no sistema inteligente: {e}")
        return False
    
def targeted_loot_pull(config):
    """
    Sistema que puxa loots especificamente para as coordenadas do autopick
    """
    try:
        if config.autopick_enabled != "ON":
            return False
            
        pointers = Pointers(config.pid)
        
        print("Iniciando loot pull direcionado...")
        
        # Obtém coordenadas do personagem
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        player_x = pointers.get_x()
        player_y = pointers.get_y()
        
        if char_x is None or char_y is None:
            print("Erro ao obter coordenadas do personagem")
            return False
        
        print(f"Personagem em: X={char_x}, Y={char_y} (tiles: {player_x}, {player_y})")
        
        # Converte coordenadas do autopick para coordenadas do mundo do jogo
        # As coordenadas do autopick são relativas à tela, precisamos converter para coordenadas absolutas
        target_world_x = char_x + (config.autopick_x - 400) * 0.5  # Ajuste baseado na diferença da tela
        target_world_y = char_y + (config.autopick_y - 400) * 0.5  # Ajuste baseado na diferença da tela
        
        print(f"Alvo para puxar loot: X={target_world_x}, Y={target_world_y}")
        
        pulled_count = 0
        attempts = 0
        max_attempts = 20
        
        while attempts < max_attempts:
            try:
                target_x, target_y, object_pointer = pointers.search_id()
                attempts += 1
                
                if target_x is None or object_pointer is None:
                    print(f"Tentativa {attempts}: Nenhum objeto encontrado")
                    time.sleep(0.1)
                    continue
                
                # Calcula distância do objeto ao personagem
                distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)
                
                # Só processa objetos que estão numa distância razoável (possível loot)
                if 0.5 < distance <= 15:
                    print(f"Objeto encontrado a {distance:.1f}m - puxando para coordenadas do autopick")
                    
                    # Puxa para próximo das coordenadas do autopick
                    if pointers.write_position(object_pointer, target_world_x, target_world_y):
                        pulled_count += 1
                        print(f"Objeto #{pulled_count} puxado com sucesso!")
                        time.sleep(0.2)
                        
                        # Se puxou alguns objetos, para para evitar sobrecarga
                        if pulled_count >= 5:
                            break
                    else:
                        print("Falha ao puxar objeto")
                        
                elif distance <= 0.5:
                    print(f"Objeto muito próximo (distância: {distance:.1f}m) - ignorando")
                else:
                    print(f"Objeto muito longe (distância: {distance:.1f}m) - provavelmente não é loot")
                    
                time.sleep(0.1)  # Pequena pausa entre tentativas
                    
            except Exception as e:
                print(f"Erro ao processar objeto na tentativa {attempts}: {e}")
                continue
                
        print(f"Loot pull concluído - {pulled_count} objetos puxados")
        
        if pulled_count > 0:
            time.sleep(1)  # Aguarda objetos se estabilizarem
            execute_autopick_collection(config)
            return True
        else:
            # Mesmo sem puxar, tenta autopick caso haja loot já próximo
            execute_autopick_collection(config)
            return False
        
    except Exception as e:
        print(f"Erro no targeted loot pull: {e}")
        return False


def simple_loot_pull_to_player(config):
    """
    Versão mais simples que puxa loot diretamente para a posição do personagem
    """
    try:
        if config.autopick_enabled != "ON":
            return False
            
        pointers = Pointers(config.pid)
        
        print("Puxando loot para posição do personagem...")
        
        # Obtém posição exata do personagem
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        
        if char_x is None or char_y is None:
            return False
        
        pulled_count = 0
        
        # Tenta puxar objetos próximos
        for i in range(10):
            try:
                target_x, target_y, object_pointer = pointers.search_id()
                
                if target_x is None or object_pointer is None:
                    break
                
                # Calcula posição ligeiramente deslocada do personagem para cada item
                offset_x = char_x + (i * 20) - 60  # Distribui em linha
                offset_y = char_y + (i * 20) - 60
                
                # Puxa o objeto para próximo do personagem
                if pointers.write_position(object_pointer, offset_x, offset_y):
                    pulled_count += 1
                    print(f"Loot #{pulled_count} puxado para próximo do personagem")
                    time.sleep(0.3)
                
            except Exception as e:
                print(f"Erro ao puxar loot {i+1}: {e}")
                continue
        
        print(f"Total puxado: {pulled_count} loots")
        
        if pulled_count > 0:
            time.sleep(1)
        
        # Sempre executa autopick após tentar puxar
        execute_autopick_collection(config)
        return pulled_count > 0
        
    except Exception as e:
        print(f"Erro no simple loot pull: {e}")
        return False


def debug_loot_positions(config):
    """
    Função de debug para mostrar posições de objetos encontrados
    """
    try:
        pointers = Pointers(config.pid)
        
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        player_x = pointers.get_x()
        player_y = pointers.get_y()
        
        print(f"=== DEBUG POSIÇÕES ===")
        print(f"Personagem: X={char_x}, Y={char_y} (tiles: {player_x}, {player_y})")
        print(f"Autopick config: X={config.autopick_x}, Y={config.autopick_y}")
        
        for i in range(5):
            try:
                target_x, target_y, object_pointer = pointers.search_id()
                
                if target_x is not None:
                    distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)
                    print(f"Objeto #{i+1}: X={target_x}, Y={target_y}, Distância={distance:.1f}m, Pointer={hex(object_pointer) if object_pointer else None}")
                else:
                    print(f"Objeto #{i+1}: Não encontrado")
                    
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Erro no debug {i+1}: {e}")
        
        print("=== FIM DEBUG ===")
        
    except Exception as e:
        print(f"Erro no debug: {e}")


def execute_autopick_collection(config):
    """
    Versão melhorada da coleta automática
    """
    try:
        pick_x = config.autopick_x
        pick_y = config.autopick_y
        hwnd = config.hwnd
        
        print(f"Executando autopick em ({pick_x}, {pick_y})")
        
        lParam = (pick_y << 16) | (pick_x & 0xFFFF)
        
        # Executa múltiplos clicks para garantir coleta
        for click_round in range(2):  # 2 rodadas de clicks
            # Pressiona SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            time.sleep(0.1)
            
            # Múltiplos clicks direitos
            for i in range(4):  # 4 clicks por rodada
                win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
                time.sleep(0.05)
                win32api.SendMessage(hwnd, 0x0205, 0, lParam)
                time.sleep(0.1)
            
            # Solta SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)
        
        print("Autopick concluído")
        
    except Exception as e:
        print(f"Erro na coleta automática: {e}")

def direct_loot_pull(config):
    """
    Sistema direto que puxa loot DIRETAMENTE para cima do personagem
    """
    try:
        if config.autopick_enabled != "ON":
            return False
            
        pointers = Pointers(config.pid)
        
        print("=== PUXANDO LOOT PARA CIMA DO PERSONAGEM ===")
        
        # Coordenadas exatas do personagem
        char_x_raw = pointers.char_x()  # Posição bruta X
        char_y_raw = pointers.char_y()  # Posição bruta Y
        player_x = pointers.get_x()     # Posição em tiles X
        player_y = pointers.get_y()     # Posição em tiles Y
        
        if char_x_raw is None or char_y_raw is None or player_x is None or player_y is None:
            print("❌ Erro: Não foi possível obter coordenadas do personagem")
            return False
        
        print(f"🎯 Personagem em: Tiles({player_x}, {player_y}), Raw({char_x_raw:.0f}, {char_y_raw:.0f})")
        
        pulled_count = 0
        
        # Busca e puxa objetos diretamente para cima do personagem
        for attempt in range(15):
            try:
                print(f"🔍 Tentativa {attempt + 1}: Procurando objetos...")
                
                target_x, target_y, object_pointer = pointers.search_id()
                
                if target_x is None or object_pointer is None:
                    print(f"   └─ Nenhum objeto encontrado")
                    time.sleep(0.1)
                    continue
                
                # Calcula distância
                distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)
                print(f"   └─ Objeto: Tiles({target_x}, {target_y}), Distância: {distance:.1f}m")
                
                # Só puxa objetos que estão numa distância razoável (loot)
                if 1 < distance <= 12:
                    print(f"   └─ ✅ PUXANDO LOOT #{pulled_count + 1} PARA CIMA DO PERSONAGEM")
                    
                    # ✨ NOVA LÓGICA: Posiciona EXATAMENTE na posição do personagem
                    # Sem offset, sem círculo - direto na posição do player
                    new_x = char_x_raw  # Mesma posição X do personagem
                    new_y = char_y_raw  # Mesma posição Y do personagem
                    
                    print(f"   └─ Movendo para: X={new_x:.0f}, Y={new_y:.0f} (posição exata do player)")
                    
                    # Move o objeto para a posição exata do personagem
                    success = pointers.write_position(object_pointer, new_x, new_y)
                    
                    if success:
                        pulled_count += 1
                        print(f"   └─ ✅ SUCESSO! Loot #{pulled_count} está agora EM CIMA do personagem")
                        time.sleep(0.3)
                        
                        if pulled_count >= 8:
                            print("📦 Limite atingido (8 objetos), parando...")
                            break
                    else:
                        print(f"   └─ ❌ FALHA ao puxar objeto")
                        
                elif distance <= 1:
                    print(f"   └─ ⚠️ Objeto já muito próximo ({distance:.1f}m)")
                else:
                    print(f"   └─ ⚠️ Objeto muito longe ({distance:.1f}m) - ignorando")
                
                time.sleep(0.15)
                    
            except Exception as e:
                print(f"   └─ ❌ Erro na tentativa {attempt + 1}: {e}")
                continue
        
        print(f"📊 RESULTADO: {pulled_count} objetos puxados PARA CIMA do personagem")
        
        if pulled_count > 0:
            print("⏳ Aguardando objetos se posicionarem...")
            time.sleep(1.2)
        
        print("🤖 Executando coleta automática...")
        execute_autopick_collection(config)
        
        return pulled_count > 0
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        return False


def stack_loot_on_player(config):
    """
    Empilha todo loot na posição exata do player e usa autopick dinâmico
    """
    try:
        if config.autopick_enabled != "ON":
            return False
            
        pointers = Pointers(config.pid)
        
        print("🎯 EMPILHANDO TODO LOOT EM CIMA DO PERSONAGEM")
        
        # Posição exata do personagem
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        
        if char_x is None or char_y is None:
            return False
        
        print(f"📍 Posição do personagem: X={char_x:.0f}, Y={char_y:.0f}")
        
        pulled = 0
        max_attempts = 10  # Reduzido de 12 para 10
        
        # Empilha todos os objetos encontrados na mesma posição
        for i in range(max_attempts):
            try:
                obj_x, obj_y, obj_pointer = pointers.search_id()
                
                if obj_pointer is None:
                    print(f"Tentativa {i+1}: Nenhum objeto encontrado")
                    # Se já puxou alguns objetos, para a busca
                    if pulled > 0:
                        break
                    continue
                
                print(f"🔍 Objeto #{i+1} encontrado - empilhando...")
                
                # Move TODOS os objetos para a mesma posição do personagem
                final_x = char_x
                final_y = char_y
                
                if pointers.write_position(obj_pointer, final_x, final_y):
                    pulled += 1
                    print(f"✅ Objeto #{pulled} empilhado em cima do personagem!")
                    time.sleep(0.2)  # Reduzido de 0.25 para 0.2
                    
                    # Para após puxar alguns objetos para não sobrecarregar
                    if pulled >= 8:
                        print("📦 Limite de 8 objetos atingido, parando...")
                        break
                else:
                    print(f"❌ Falha ao empilhar objeto #{i+1}")
                
            except Exception as e:
                print(f"Erro ao empilhar objeto {i+1}: {e}")
                continue
        
        print(f"📦 TOTAL EMPILHADO: {pulled} objetos na posição do personagem")
        
        if pulled > 0:
            print("⏳ Aguardando objetos se estabilizarem...")
            time.sleep(1.0)  # Reduzido de 1.2 para 1.0
        
        # 🎯 EXECUTA AUTOPICK SIMPLIFICADO E MAIS RÁPIDO
        print("🤖 Executando autopick na posição do personagem...")
        
        # Método simplificado e direto
        hwnd = config.hwnd
        
        # Para resolução 1024x768, usa o centro da tela onde o personagem aparece
        center_x = 512  # Centro de 1024
        center_y = 384  # Centro de 768
        
        print(f"🎯 Executando autopick no centro da tela: ({center_x}, {center_y})")
        
        # Prepara as coordenadas
        lParam = (center_y << 16) | (center_x & 0xFFFF)
        
        try:
            # Execução rápida e direta
            for round_num in range(2):  # 2 rodadas rápidas
                print(f"   🔄 Rodada {round_num + 1}...")
                
                # Pressiona SHIFT
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                time.sleep(0.05)
                
                # 4 clicks rápidos
                for click in range(4):
                    win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
                    time.sleep(0.02)
                    win32api.SendMessage(hwnd, 0x0205, 0, lParam)
                    time.sleep(0.05)
                
                # Solta SHIFT
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.2)
            
            print("✅ Autopick executado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro no autopick: {e}")
        
        return pulled > 0
        
    except Exception as e:
        print(f"❌ Erro no empilhamento: {e}")
        return False


def quick_autopick_system(config):
    """
    Sistema de autopick rápido e eficiente
    """
    try:
        hwnd = config.hwnd
        
        print("🎮 Sistema de Autopick Rápido")
        
        # Coordenadas do centro da tela (onde está o personagem)
        center_x = 512
        center_y = 384
        
        print(f"🎯 Posição do autopick: ({center_x}, {center_y})")
        
        # Prepara coordenadas
        lParam = (center_y << 16) | (center_x & 0xFFFF)
        
        # Execução super rápida
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.1)
        
        # 6 clicks diretos e rápidos
        for i in range(6):
            win32api.SendMessage(hwnd, 0x0204, win32con.MK_RBUTTON | win32con.MK_SHIFT, lParam)
            time.sleep(0.02)
            win32api.SendMessage(hwnd, 0x0205, 0, lParam)
            time.sleep(0.03)
        
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        print("✅ Autopick rápido concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no autopick rápido: {e}")
        return False


def direct_loot_pull(config):
    """
    Sistema direto mais rápido e eficiente
    """
    try:
        if config.autopick_enabled != "ON":
            return False
            
        pointers = Pointers(config.pid)
        
        print("=== SISTEMA DIRETO DE LOOT PULL ===")
        
        # Coordenadas do personagem
        char_x_raw = pointers.char_x()
        char_y_raw = pointers.char_y()
        player_x = pointers.get_x()
        player_y = pointers.get_y()
        
        if char_x_raw is None or char_y_raw is None:
            print("❌ Erro: Coordenadas do personagem não encontradas")
            return False
        
        print(f"🎯 Personagem: Tiles({player_x}, {player_y}), Raw({char_x_raw:.0f}, {char_y_raw:.0f})")
        
        pulled_count = 0
        max_attempts = 10  # Limite de tentativas
        
        # Busca e puxa objetos de forma mais eficiente
        for attempt in range(max_attempts):
            try:
                target_x, target_y, object_pointer = pointers.search_id()
                
                if target_x is None or object_pointer is None:
                    # Se já puxou algo, para a busca
                    if pulled_count > 0:
                        break
                    continue
                
                distance = math.sqrt((target_x - player_x) ** 2 + (target_y - player_y) ** 2)
                
                if 1 < distance <= 12:
                    print(f"✅ Puxando loot #{pulled_count + 1} (dist: {distance:.1f}m)")
                    
                    # Move para posição exata do personagem
                    if pointers.write_position(object_pointer, char_x_raw, char_y_raw):
                        pulled_count += 1
                        time.sleep(0.2)
                        
                        if pulled_count >= 6:  # Limite de 6 objetos
                            break
                
            except Exception as e:
                print(f"❌ Erro na tentativa {attempt + 1}: {e}")
                continue
        
        print(f"📊 TOTAL PUXADO: {pulled_count} objetos")
        
        if pulled_count > 0:
            time.sleep(0.8)  # Tempo reduzido
            
        # Executa autopick rápido
        quick_autopick_system(config)
        
        return pulled_count > 0
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return False

def precise_loot_to_player(config):
    """
    Sistema mais preciso que garante loot exatamente na posição do player
    """
    try:
        pointers = Pointers(config.pid)
        
        print("🎯 SISTEMA PRECISO: Loot direto na posição do player")
        
        # Obtém coordenadas mais precisas
        raw_x = pointers.read_value(pointers.X_POINTER, data_type="float")
        raw_y = pointers.read_value(pointers.Y_POINTER, data_type="float")
        
        if raw_x is None or raw_y is None:
            return False
        
        print(f"📍 Posição precisa: X={raw_x:.2f}, Y={raw_y:.2f}")
        
        moved_count = 0
        
        # Sistema de busca mais agressivo
        for round_num in range(3):  # 3 rodadas de busca
            print(f"\n🔄 Rodada {round_num + 1} de busca...")
            
            for attempt in range(8):  # 8 tentativas por rodada
                try:
                    obj_tile_x, obj_tile_y, obj_pointer = pointers.search_id()
                    
                    if obj_pointer is None:
                        continue
                    
                    player_tile_x = pointers.get_x()
                    player_tile_y = pointers.get_y()
                    
                    if player_tile_x is None or player_tile_y is None:
                        continue
                    
                    # Calcula distância em tiles
                    dist = math.sqrt((obj_tile_x - player_tile_x) ** 2 + (obj_tile_y - player_tile_y) ** 2)
                    
                    if 0.5 < dist <= 15:  # Objeto em distância válida
                        print(f"   🎯 Movendo objeto (dist: {dist:.1f}m) para player...")
                        
                        # Move para a posição EXATA do personagem
                        if pointers.write_position(obj_pointer, raw_x, raw_y):
                            moved_count += 1
                            print(f"   ✅ Objeto #{moved_count} movido!")
                            time.sleep(0.2)
                    
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    continue
            
            time.sleep(0.3)  # Pausa entre rodadas
        
        print(f"\n📊 TOTAL FINAL: {moved_count} objetos movidos para o personagem")
        
        if moved_count > 0:
            time.sleep(1.5)
        
        # 🎯 USA O NOVO SISTEMA INTELIGENTE DE AUTOPICK  
        print("🤖 Executando sistema inteligente de autopick...")
        smart_autopick_system(config)
        
        return moved_count > 0
        
    except Exception as e:
        print(f"Erro no sistema preciso: {e}")
        return False
    
def force_loot_to_coordinates(config):
    """
    Versão alternativa que força loot para coordenadas específicas
    """
    try:
        pointers = Pointers(config.pid)
        
        # Obtém posição do personagem
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        
        if char_x is None or char_y is None:
            return False
        
        print("🎯 Forçando loot para coordenadas específicas...")
        
        # Calcula posição alvo (próxima às coordenadas do autopick)
        # Ajuste experimental: converte coordenadas de tela para mundo
        target_x = char_x + 100  # 5 metros à direita
        target_y = char_y - 50   # 2.5 metros para cima
        
        pulled = 0
        
        for i in range(15):
            try:
                obj_x, obj_y, obj_pointer = pointers.search_id()
                
                if obj_pointer is None:
                    break
                    
                # Calcula posição específica para cada item
                final_x = target_x + (i * 30)  # Espaça os itens
                final_y = target_y + (i * 20)
                
                if pointers.write_position(obj_pointer, final_x, final_y):
                    pulled += 1
                    print(f"✅ Item #{pulled} movido para ({final_x:.0f}, {final_y:.0f})")
                    time.sleep(0.3)
                    
            except Exception as e:
                print(f"Erro ao mover item {i+1}: {e}")
                continue
        
        print(f"📦 Total movido: {pulled} itens")
        
        if pulled > 0:
            time.sleep(2)  # Mais tempo para estabilizar
            
        execute_autopick_collection(config)
        return pulled > 0
        
    except Exception as e:
        print(f"Erro no force loot: {e}")
        return False


def test_object_detection(config):
    """
    Função de teste para verificar se está detectando objetos corretamente
    """
    try:
        pointers = Pointers(config.pid)
        
        print("\n=== TESTE DE DETECÇÃO DE OBJETOS ===")
        
        char_x = pointers.char_x()
        char_y = pointers.char_y()
        player_x = pointers.get_x()
        player_y = pointers.get_y()
        
        print(f"Personagem:")
        print(f"  - Coordenadas brutas: X={char_x}, Y={char_y}")
        print(f"  - Coordenadas tiles: X={player_x}, Y={player_y}")
        print(f"  - Autopick config: X={config.autopick_x}, Y={config.autopick_y}")
        
        print(f"\nProcurando objetos próximos...")
        
        objects_found = []
        
        for i in range(10):
            try:
                obj_x, obj_y, obj_pointer = pointers.search_id()
                
                if obj_x is not None and obj_pointer is not None:
                    distance = math.sqrt((obj_x - player_x) ** 2 + (obj_y - player_y) ** 2)
                    
                    objects_found.append({
                        'id': i+1,
                        'tile_x': obj_x,
                        'tile_y': obj_y,
                        'pointer': obj_pointer,
                        'distance': distance
                    })
                    
                    print(f"  Objeto #{i+1}: Tiles({obj_x}, {obj_y}), Dist: {distance:.1f}m, Ptr: {hex(obj_pointer)}")
                else:
                    print(f"  Objeto #{i+1}: Não encontrado")
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  Objeto #{i+1}: Erro - {e}")
        
        print(f"\n📊 RESUMO: {len(objects_found)} objetos detectados")
        
        # Filtra objetos que podem ser loot (distância razoável)
        potential_loot = [obj for obj in objects_found if 1 < obj['distance'] <= 15]
        print(f"🎯 Possível loot: {len(potential_loot)} objetos")
        
        for loot in potential_loot:
            print(f"  - Objeto #{loot['id']}: {loot['distance']:.1f}m de distância")
        
        print("=== FIM DO TESTE ===\n")
        
        return len(potential_loot)
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        return 0

def deleter(config):
    def inner():
        if config.minimized_mode == "ON":
            hwnd = win32gui.FindWindow(None, config.char_name)
            if hwnd:
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == win32con.SW_SHOWMINIMIZED:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(1)

        if not Pointers(config.pid).is_bag_open():
            print("Open bag")
            send(config.hwnd, config.inventory)
            time.sleep(0.5)
        else:
            print("Bag is open")
            time.sleep(0.5)

        def load_images(folder):
            images = {}
            for filename in os.listdir(folder):
                full_path = os.path.join(folder, filename)
                image = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
                if image is not None:
                    images[filename] = image
            return images

        def capture_window(hwnd):
            try:
                rect = win32gui.GetWindowRect(hwnd)
                width, height = rect[2] - rect[0], rect[3] - rect[1]

                hwnd_dc = win32gui.GetWindowDC(hwnd)
                mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
                save_dc = mfc_dc.CreateCompatibleDC()
                save_bitmap = win32ui.CreateBitmap()
                save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
                save_dc.SelectObject(save_bitmap)

                save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

                bmp_info = save_bitmap.GetInfo()
                bmp_str = save_bitmap.GetBitmapBits(True)
                img = np.frombuffer(bmp_str, dtype=np.uint8)
                img.shape = (bmp_info['bmHeight'], bmp_info['bmWidth'], 4)

                save_dc.DeleteDC()
                mfc_dc.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwnd_dc)
                win32gui.DeleteObject(save_bitmap.GetHandle())

                return img[..., :3]

            except Exception as e:
                print(f"Erro ao capturar a janela: {e}")
                raise

        def get_title_bar_height():
            SM_CYCAPTION = 4
            return ctypes.windll.user32.GetSystemMetrics(SM_CYCAPTION)

        def find_image_in_window(target_image, hwnd):
            title_bar_height = get_title_bar_height()
            window_img = capture_window(hwnd)
            window_gray = cv2.cvtColor(window_img, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(window_gray, target_image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > 0.9:
                adjusted_loc = (max_loc[0], max_loc[1] - title_bar_height)
                return adjusted_loc

            return None

        def find_items_in_window(item_images, hwnd):
            to_delete = []
            tolerance = 3

            window_img = capture_window(hwnd)
            window_gray = cv2.cvtColor(window_img, cv2.COLOR_BGR2GRAY)

            for offset in bag_offsets:
                x1, y1, width, height = offset
                bag_area = window_gray[y1:y1 + height, x1:x1 + width]

                for item_name, item_image in item_images.items():
                    result = cv2.matchTemplate(bag_area, item_image, cv2.TM_CCOEFF_NORMED)
                    threshold = 0.9
                    loc = np.where(result >= threshold)

                    for pt in zip(*loc[::-1]):
                        title_bar_height = get_title_bar_height()
                        global_x = x1 + pt[0]
                        global_y = y1 + pt[1] - title_bar_height

                        if not any(
                                abs(existing_x - global_x) <= tolerance and abs(existing_y - global_y) <= tolerance for
                                existing_x, existing_y in to_delete):
                            to_delete.append((global_x, global_y))

            return to_delete

        item_path = "Images/items"
        item_images = load_images(item_path)

        destroy_path = "Images/misc/destroy-item.bmp"
        destroy_image = cv2.imread(destroy_path, cv2.IMREAD_GRAYSCALE)
        coordinates = find_image_in_window(destroy_image, config.hwnd)

        if coordinates:
            destroy_x, destroy_y = coordinates

            bag_cords = [
                (destroy_x - 5, destroy_y - 200, destroy_x + 220, destroy_y - 15),
                (destroy_x + 250, destroy_y - 420, destroy_x + 490, destroy_y - 10),
            ]

            bag_offsets = [
                (destroy_x - 5, destroy_y - 200, destroy_x + 220, destroy_y - 15),
                (destroy_x + 250, destroy_y - 420, destroy_x + 490, destroy_y - 10),
            ]

            bag_images = []
            for x1, y1, x2, y2 in bag_cords:
                bag_img = capture_window(config.hwnd)[y1:y2, x1:x2]
                bag_images.append(bag_img)

            to_delete = find_items_in_window(item_images, config.hwnd)

            for item in to_delete:
                x, y = int(item[0]), int(item[1])

                left(config.hwnd, x, y)
                time.sleep(0.15)
                left(config.hwnd, destroy_x, destroy_y)
                time.sleep(0.15)
                left(config.hwnd, int(cords_game["deleter_ok"][0]), int(cords_game["deleter_ok"][1]))
                time.sleep(0.15)
        else:
            print("Destroy icon not found.")
        print("Close bag")
        send(config.hwnd, config.inventory)
        time.sleep(1)
        if config.minimized_mode == "ON":
            hwnd = win32gui.FindWindow(None, config.char_name)
            if hwnd:
                placement = win32gui.GetWindowPlacement(hwnd)
                if not placement[1] == win32con.SW_SHOWMINIMIZED:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    return inner


class GameConfig:
    def __init__(self, resolution, char_name, hwnd, get_back, distance, inventory, char_type, pid, pet_food,
                 pet_food_delay, buff_1,
                 buff_2, skill_1, skill_2, potion_hp,
                 skill_3, skill_4, skill_5, skill_6, sit, low_hp,
                 spot_farm, unstuck_speed, buff_delay, deleter_bot, deleter_delay, map,
                 cords, revive_and_back, autopick_enabled="OFF", autopick_x=0, autopick_y=0,
                 minimized_mode="OFF", kill_santa="OFF"):
        self.hwnd = hwnd
        self.char_name = char_name
        self.resolution = resolution
        self.inventory = inventory
        self.char_type = char_type
        self.pid = pid
        self.spot_farm = spot_farm
        self.deleter_bot = deleter_bot
        self.deleter_delay = deleter_delay
        self.map = map
        self.pet_food = pet_food
        self.pet_food_delay = pet_food_delay
        self.unstuck_speed = unstuck_speed
        self.buff_1 = buff_1
        self.buff_2 = buff_2
        self.skill_1 = skill_1
        self.skill_2 = skill_2
        self.skill_3 = skill_3
        self.skill_4 = skill_4
        self.skill_5 = skill_5
        self.skill_6 = skill_6
        self.potion_hp = potion_hp
        self.sit = sit
        self.buff_delay = buff_delay
        self.low_hp = low_hp
        self.cords = cords
        self.get_back = get_back
        self.distance = distance
        self.revive_and_back = revive_and_back
        self.autopick_enabled = autopick_enabled
        self.autopick_x = autopick_x
        self.autopick_y = autopick_y
        self.minimized_mode = minimized_mode
        self.kill_santa = kill_santa


class Game:
    def __init__(self):
        self.settings = {}
        self.keys = {}
        self.processes = {}
        self.stop_events = {}

    def set_settings(self, target):
        file_name = f"characters/{target}.json"
        with open(file_name, "r") as json_file:
            self.settings[target] = json.load(json_file)

    def get_keys(self):
        with open("characters/keys.json", "r") as json_file:
            self.keys = json.load(json_file)

    def load_game(self, target):
        if target in self.processes and self.processes[target]:
            app = QApplication.instance() or QApplication([])
            reply = QMessageBox.question(
                None,
                "Processo em execução",
                f"Char {target} already running. Do you want to restart it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                print(f"Processo para {target} mantido em execução.")
                return
            else:
                print(f"Reiniciando o processo para {target}...")
                self.stop_game(target)

        print(f"Carregando o jogo para o personagem {target}...")
        self.get_keys()
        self.set_settings(target)

        config = GameConfig(
            hwnd=self.settings[target]["HWND"],
            char_name=self.settings[target]["CHAR_NAME"],
            resolution=self.settings[target]["RESOLUTION"],
            inventory=self.keys["INVENTORY"],
            char_type=self.settings[target]["CHAR_TYPE"],
            pid=self.settings[target]["PID"],
            spot_farm=self.settings[target]["SPOT_FARM"],
            deleter_bot=self.settings[target]["DELETER_BOT"],
            deleter_delay=self.settings[target]["DELETER_DELAY"],
            low_hp=self.settings[target]["LOW_HP"],
            pet_food=self.keys["PET_FOOD"],
            pet_food_delay=self.settings[target]["PET_FOOD_DELAY"],
            buff_1=self.keys["BUFF_1"],
            buff_2=self.keys["BUFF_2"],
            skill_1=self.keys["SKILL_1"],
            skill_2=self.keys["SKILL_2"],
            skill_3=self.keys["SKILL_3"],
            skill_4=self.keys["SKILL_4"],
            skill_5=self.keys["SKILL_5"],
            skill_6=self.keys["SKILL_6"],
            potion_hp=self.keys["POTION_HP"],
            sit=self.keys["SIT"],
            buff_delay=self.settings[target]["BUFF_DELAY"],
            map=self.keys["MAP"],
            cords=self.settings[target]["CORDS"],
            unstuck_speed=self.settings[target]["UNSTUCK_SPEED"],
            get_back=self.settings[target]["GET_BACK"],
            distance=self.settings[target]["DISTANCE"],
            revive_and_back=self.settings[target]["REVIVE_AND_BACK"],
            autopick_enabled=self.settings[target].get("AUTOPICK_ENABLED", "OFF"),
            autopick_x=self.settings[target].get("AUTOPICK_X", 400),
            autopick_y=self.settings[target].get("AUTOPICK_Y", 400),
            minimized_mode=self.settings[target].get("MINIMIZED_MODE", "OFF"),
            kill_santa=self.settings[target].get("KILL_SANTA", "OFF")
        )

        stop_event = multiprocessing.Event()

        game_process = multiprocessing.Process(target=start_game_process, args=(config, stop_event))
        game_process.daemon = True
        game_process.start()

        if target not in self.processes:
            self.processes[target] = {}
            self.stop_events[target] = {}

        self.processes[target][game_process.pid] = game_process
        self.stop_events[target][game_process.pid] = stop_event

        print(f"Processo iniciado para {target} (PID: {game_process.pid}).")
        print(f"Processos: {self.processes}")

    def stop_game(self, target, pid=None):
        if target in self.processes:
            if pid is None:
                print(f"Parando todos os processos para {target}...")
                for pid, process in self.processes[target].items():
                    self._terminate_process(target, pid, process)
                del self.processes[target]
                del self.stop_events[target]
            elif pid in self.processes[target]:
                print(f"Parando o processo {pid} para {target}...")
                self._terminate_process(target, pid, self.processes[target][pid])
                del self.processes[target][pid]
                del self.stop_events[target][pid]
                if not self.processes[target]:
                    del self.processes[target]
                    del self.stop_events[target]
            else:
                print(f"PID {pid} não encontrado para o personagem {target}.")
        else:
            print(f"Personagem {target} não encontrado ou processo já encerrado.")

    def _terminate_process(self, target, pid, process):
        self.stop_events[target][pid].set()
        process.terminate()
        process.join()
        print(f"Processo {pid} para {target} encerrado.")


class CycleManager:
    def __init__(self):
        self.cycles = []

    def add_cycle(self, action: Callable, interval_minutes: float, name: str):
        interval_seconds = interval_minutes * 60
        self.cycles.append({
            "action": action,
            "interval": interval_seconds,
            "next_execution": time.time(),
            "name": name
        })

    def execute_cycles(self):
        current_time = time.time()
        for cycle in self.cycles:
            if current_time >= cycle["next_execution"]:
                print(f"Executando ciclo: {cycle['name']}...")
                try:
                    cycle["action"]()
                except Exception as e:
                    print(f"Erro ao executar o ciclo '{cycle['name']}': {e}")
                cycle["next_execution"] = current_time + cycle["interval"]


if __name__ == "__main__":
    print("Módulo Game carregado.")