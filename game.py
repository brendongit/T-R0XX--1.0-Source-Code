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
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from keyboard import send
from mouse import *
from pointers import Pointers

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
    """Configura as coordenadas globais com base na resolução."""
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
            "pick_up_all": [400, 400],  # Coordenada padrão, será configurável
        })

    else:
        raise ValueError(f"Resolução não suportada: {resolution}")


def start_game_process(config, stop_event):
    """Executa o loop de jogo em um subprocesso, verificando o sinal de parada."""
    set_coords_by_resolution(config.resolution)

    if config.minimized_mode == "ON" and config.deleter_bot == "OFF":
        hwnd = win32gui.FindWindow(None, config.char_name)
        if hwnd:
            placement = win32gui.GetWindowPlacement(hwnd)
            if not placement[1] == win32con.SW_SHOWMINIMIZED:  # SW_SHOWMINIMIZED é 2
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)  # Minimiza a janela

    if config.minimized_mode == "OFF":
        hwnd = win32gui.FindWindow(None, config.char_name)
        if hwnd:
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:  # SW_SHOWMINIMIZED é 2
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restaura a janela se estiver minimizada
                time.sleep(1)

    while not stop_event.is_set():
        try:
            bot(config)
        except Exception as e:
            print(f"Erro no subprocesso PID={config.pid}: {e}")
            break


def bot(config):
    global safe_spot, get_back_enable, heal_target_name, get_back_enable

    get_back_enable = 0

    x, y = Pointers(config.pid).get_x(), Pointers(config.pid).get_y()
    safe_spot = [x, y]
    print(f"Start  = {safe_spot}")

    manager = CycleManager()
    if config.deleter_bot == "ON":
        manager.add_cycle(deleter(config), config.deleter_delay, "Ciclo de Deleter")

    if config.autopick_enabled == "ON":
        manager.add_cycle(autopick_items(config), config.autopick_delay, "Ciclo de Autopick")

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


def debug_pet_ap(config):
    def inner():
        right(config.hwnd, cords_move["stop"][0] + 2, cords_move["stop"][1] + 2)
        time.sleep(1)
        right(config.hwnd, cords_move["stop"][0] - 2, cords_move["stop"][1] - 2)
        time.sleep(1)

    return inner


def check_distance(config, xY):  # Adiciona um parâmetro de tolerância
    while True:
        get_x = Pointers(config.pid).get_x()
        get_y = Pointers(config.pid).get_y()
        print(f"Posição inicial: {xY}, Posição atual: ({get_x}, {get_y})")

        # Calcula a distância do ponto inicial
        current_distance = math.sqrt((get_x - xY[0]) ** 2 + (get_y - xY[1]) ** 2)

        # Debug: Exibe a distância calculada e o limite
        print(f"Distância atual: {current_distance:.2f} m, Limite: {config.distance} m")

        # Verifica se a distância ultrapassa o limite máximo
        if current_distance >= config.distance:  # Só reposiciona se for MAIOR
            print(f"Distância {current_distance} excede o limite! Reposicionando...")
            if current_distance >= 50:  # V1.3
                go_to_spot(config)
            safe_spot_back(config, xY)

        # Se a distância está dentro do limite, não faz nenhuma movimentação
        if current_distance <= config.distance:
            print("Dentro do limite, sem movimentação.")
            time.sleep(0.1)
            return


def safe_spot_back(config, xY, tolerance=2):  # Adiciona um parâmetro de tolerância
    while True:
        # Atualiza continuamente a posição atual
        dead(config)

        get_x = Pointers(config.pid).get_x()
        get_y = Pointers(config.pid).get_y()
        time.sleep(0.1)
        # print(f"Primeiro {get_x} {get_y}")

        # Verifica se já está na posição correta com tolerância
        if abs(get_x - xY[0]) <= tolerance and abs(get_y - xY[1]) <= tolerance:
            #print("Chegou ao local seguro com tolerância!")
            break

        # Calcula a diferença entre a posição atual e o destino
        x, y = get_x, get_y
        via = [cords_move["stop"][0], cords_move["stop"][1]]
        repos = [x - xY[0], y - xY[1]]
        time.sleep(0.1)

        # Corrige a posição
        if repos[0] != 0 or repos[1] != 0:
            # Ajusta eixo X
            if repos[0] != 0:
                via[0] -= repos[0]
                time.sleep(0.1)
            # Ajusta eixo Y
            if repos[1] != 0:
                via[1] += repos[1]
                time.sleep(0.1)

            # Move o personagem
            right(config.hwnd, int(via[0]), int(via[1]))
            wait_while_moving(config)

    # Reseta o cursor após chegar no destino
    left(config.hwnd, int(cords_move["mouse_reset"][0]), int(cords_move["mouse_reset"][1]))
    time.sleep(0.1)


def wait_while_moving(config):
    countspot = 0
    prevX, prevY = None, None

    while True:

        x = Pointers(config.pid).get_x()
        y = Pointers(config.pid).get_y()
        # print(x, y)
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


def safe_spot_back_backup(config, xY, tolerance=2):  # Adiciona um parâmetro de tolerância
    def inner():
        while True:
            # Atualiza continuamente a posição atual
            get_x = Pointers(config.pid).get_x()
            get_y = Pointers(config.pid).get_y()

            # Verifica se já está na posição correta com tolerância
            if abs(get_x - xY[0]) <= tolerance and abs(get_y - xY[1]) <= tolerance:
                #print("Chegou ao local seguro com tolerância!")
                break

            # Calcula a diferença entre a posição atual e o destino
            x, y = get_x, get_y
            via = [cords_move["stop"][0], cords_move["stop"][1]]
            repos = [x - xY[0], y - xY[1]]

            # Corrige a posição
            if repos[0] != 0 or repos[1] != 0:
                # Ajusta eixo X
                if repos[0] != 0:
                    via[0] -= repos[0]
                # Ajusta eixo Y
                if repos[1] != 0:
                    via[1] += repos[1]

                # Move o personagem
                right(config.hwnd, int(via[0]), int(via[1]))
                time.sleep(0.1)

        # Reseta o cursor após chegar no destino
        left(config.hwnd, int(cords_move["mouse_reset"][0]), int(cords_move["mouse_reset"][1]))
        time.sleep(0.1)

    return inner


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
            #print(f"Sticness: {stickness}")
            #print(f"Stuck: {stuck}")
            stickness = stickness + 1

        dead(config)
        #check_distance(config, safe_spot)



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

        print("Stting to recover HP")
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
                start_time = time.time()  # Reseta o contador de tempo
            if Pointers(config.pid).is_in_battle():
                print("Someone is hitting me!")
                kill(config)
            sit(config)
            dead(config)
            #print("Recovering HP")


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
        """Click on jackstraw"""
        left(config.hwnd, int(cords_game["jackstraw_ok"][0]), int(cords_game["jackstraw_ok"][1]))
        time.sleep(2)
        """Click on OK Revive Normal"""
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
        #print(x, y)
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


def deleter(config):
    def inner():
        if config.minimized_mode == "ON":
            hwnd = win32gui.FindWindow(None, config.char_name)
            if hwnd:
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == win32con.SW_SHOWMINIMIZED:  # SW_SHOWMINIMIZED é 2
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restaura a janela se estiver minimizada
                    time.sleep(1)

        # Verifica se a mochila está aberta
        if not Pointers(config.pid).is_bag_open():
            print("Open bag")
            send(config.hwnd, config.inventory)
            time.sleep(0.5)
        else:
            print("Bag is open")
            time.sleep(0.5)

        def load_images(folder):
            """
            Carrega todas as imagens da pasta sem cache.
            """
            images = {}
            for filename in os.listdir(folder):
                full_path = os.path.join(folder, filename)
                image = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
                if image is not None:
                    images[filename] = image
            return images

        def capture_window(hwnd):
            """
            Captura o conteúdo da janela especificada por hwnd, independentemente de sobreposições.
            """
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
            """
            Obtém a altura da barra de título da janela usando a API do Windows.
            """
            SM_CYCAPTION = 4  # Constante para altura da barra de título
            return ctypes.windll.user32.GetSystemMetrics(SM_CYCAPTION)

        def find_image_in_window(target_image, hwnd):
            """
            Encontra uma imagem dentro da janela especificada pelo HWND,
            descontando a barra de título da janela.
            """
            title_bar_height = get_title_bar_height()

            # Capturar a imagem da janela
            window_img = capture_window(hwnd)
            window_gray = cv2.cvtColor(window_img, cv2.COLOR_BGR2GRAY)

            # Localizar a imagem na janela
            result = cv2.matchTemplate(window_gray, target_image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > 0.9:  # Ajuste o limiar conforme necessário
                adjusted_loc = (max_loc[0], max_loc[1] - title_bar_height)
                return adjusted_loc

            return None

        def find_items_in_window(item_images, hwnd):
            """
            Localiza itens em uma janela específica.
            """
            to_delete = []
            tolerance = 3  # Tolerância em pixels para coordenadas duplicadas

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

            """ok_button = config.deleter_ok.split(",")
            ok_buttonX = int(ok_button[0])
            ok_buttonY = int(ok_button[1])"""

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
                if not placement[1] == win32con.SW_SHOWMINIMIZED:  # SW_SHOWMINIMIZED é 2
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)  # Minimiza a janela

    return inner


class GameConfig:
    """Classe que encapsula as configurações e valores necessários para o jogo."""

    def __init__(self, resolution, char_name, hwnd, get_back, distance, inventory, char_type, pid, pet_food,
                 pet_food_delay, buff_1,
                 buff_2, skill_1, skill_2, potion_hp,
                 skill_3, skill_4, skill_5, skill_6, sit, low_hp,
                 spot_farm, unstuck_speed, buff_delay, deleter_bot, deleter_delay, map,
                 cords, revive_and_back, autopick_enabled="OFF", autopick_delay=5, autopick_x=0, autopick_y=0):
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
        self.autopick_delay = autopick_delay
        self.autopick_x = autopick_x
        self.autopick_y = autopick_y

    def __repr__(self):
        return (
            f"GameConfig(resolution={self.resolution}, hwnd={self.hwnd},char_name={self.char_name}, inventory={self.inventory}, char_type={self.char_type}, pid={self.pid}, pet_food={self.pet_food}, buff_1={self.buff_1}, buff_2={self.buff_2}"
            f"skill_1={self.skill_1}, skill_2={self.skill_2}, skill_3={self.skill_3}, skill_4={self.skill_4}, "
            f"skill_5={self.skill_5}, skill_6={self.skill_6}, sit={self.sit}, low_hp={self.low_hp}, spot_farm={self.spot_farm}, "
            f"deleter_delay={self.deleter_delay}, deleter_bot={self.deleter_bot}, map={self.map}, buff_delay={self.buff_delay},"
            f"pet_food_delay={self.pet_food_delay}, cords={self.cords}, unstuck_speed={self.unstuck_speed}), "
            f"get_back={self.get_back}, distance={self.distance}, revive_and_back={self.revive_and_back},"
            f"potion_hp={self.potion_hp}")


class Game:
    def __init__(self):
        self.settings = {}
        self.keys = {}
        self.processes = {}
        self.stop_events = {}

    def set_settings(self, target):
        """Carrega as configurações do arquivo JSON do personagem."""
        file_name = f"characters/{target}.json"
        with open(file_name, "r") as json_file:
            self.settings[target] = json.load(json_file)

    def get_keys(self):
        """Carrega os atalhos de teclas do arquivo JSON."""
        with open("characters/keys.json", "r") as json_file:
            self.keys = json.load(json_file)

    def load_game(self, target):
        """Carrega os dados do personagem e inicializa o processo de jogo."""
        if target in self.processes and self.processes[target]:  # Verifica se já existe um processo ativo
            # Exibe uma QMessageBox perguntando se deseja reiniciar
            app = QApplication.instance() or QApplication([])  # Usa a instância existente ou cria uma nova
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
            autopick_delay=self.settings[target].get("AUTOPICK_DELAY", 5),
            autopick_x=self.settings[target].get("AUTOPICK_X", 400),
            autopick_y=self.settings[target].get("AUTOPICK_Y", 400)
        )

        # Criação do evento de parada
        stop_event = multiprocessing.Event()

        # Criação do processo, passando o objeto `GameConfig` e a flag de controle
        game_process = multiprocessing.Process(target=start_game_process, args=(config, stop_event))
        game_process.daemon = True  # O processo será encerrado quando o programa principal terminar
        game_process.start()

        # Armazenar o processo e o evento com base no target e pid
        if target not in self.processes:
            self.processes[target] = {}
            self.stop_events[target] = {}

        self.processes[target][game_process.pid] = game_process
        self.stop_events[target][game_process.pid] = stop_event

        print(f"Processo iniciado para {target} (PID: {game_process.pid}).")
        print(f"Processos: {self.processes}")

    def stop_game(self, target, pid=None):
        """Para o processo de jogo associado ao personagem e PID."""
        if target in self.processes:
            if pid is None:
                print(f"Parando todos os processos para {target}...")
                # Para todos os processos associados ao target
                for pid, process in self.processes[target].items():
                    self._terminate_process(target, pid, process)
                del self.processes[target]
                del self.stop_events[target]
            elif pid in self.processes[target]:
                print(f"Parando o processo {pid} para {target}...")
                # Para um processo específico pelo PID
                self._terminate_process(target, pid, self.processes[target][pid])
                del self.processes[target][pid]
                del self.stop_events[target][pid]
                if not self.processes[target]:  # Remove o target se não houver processos restantes
                    del self.processes[target]
                    del self.stop_events[target]
            else:
                print(f"PID {pid} não encontrado para o personagem {target}.")
        else:
            print(f"Personagem {target} não encontrado ou processo já encerrado.")

    def _terminate_process(self, target, pid, process):
        """Auxiliar para encerrar um processo."""
        self.stop_events[target][pid].set()
        process.terminate()  # Termina o processo
        process.join()  # Espera o processo terminar
        print(f"Processo {pid} para {target} encerrado.")


class CycleManager:
    def __init__(self):

        self.cycles = []

    def add_cycle(self, action: Callable, interval_minutes: float, name: str):
        interval_seconds = interval_minutes * 60  # Converte minutos para segundos
        self.cycles.append({
            "action": action,
            "interval": interval_seconds,
            "next_execution": time.time(),  # Executa imediatamente no início
            "name": name
        })

    def execute_cycles(self):
        current_time = time.time()
        for cycle in self.cycles:
            if current_time >= cycle["next_execution"]:
                print(f"Executando ciclo: {cycle['name']}...")
                try:
                    cycle["action"]()  # Executa a função associada ao ciclo
                except Exception as e:
                    print(f"Erro ao executar o ciclo '{cycle['name']}': {e}")
                cycle["next_execution"] = current_time + cycle["interval"]  # Atualiza o próximo tempo de execução


def autopick_items(config):
    """Função para coletar automaticamente os itens com o botão Pick up all"""
    def inner():
        try:
            print("Executando autopick de itens...")
            
            # Clica com o botão direito na posição central para abrir menu contextual
            right(config.hwnd, int(cords_move["stop"][0]), int(cords_move["stop"][1]))
            time.sleep(0.3)
            
            # Clica no botão "Pick up all" usando as coordenadas configuradas
            pick_x = config.autopick_x
            pick_y = config.autopick_y
            
            print(f"Clicando em Pick up all nas coordenadas: ({pick_x}, {pick_y})")
            left(config.hwnd, int(pick_x), int(pick_y))
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Erro na função autopick: {e}")
    
    return inner


if __name__ == "__main__":
    print("Módulo Game carregado.")
