import multiprocessing
import os
import sys
import json
import time
import webbrowser
import win32con
from PIL import ImageGrab
from _ctypes import byref
from pynput import keyboard
import psutil
import win32gui
import win32process
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget,
    QLabel, QListWidget, QPushButton, QSpacerItem, QSizePolicy, QProgressBar, QCheckBox, QLineEdit, QSlider, QComboBox,
    QInputDialog, QMessageBox, QListView, QScrollBar
)
from PyQt6.QtCore import Qt, QTimer
from mouse import *
import ctypes
from ctypes import windll, Structure, c_long
from game import Game
from pointers import Pointers


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.start_style = """
                        QPushButton {
                            /* Background color of the button */
                            /*background-color: #4CAF50; /* Green */
                            /*color: Black; /* Text color */
                            max-width: 71px; /* Button width */
                            max-height: 20px; /* Button height */
                            border: 2px solid #696969; /* Border color */
                            border-radius: 5px; /* Rounded corners */
                            padding: 2px 2px; /* Padding for better spacing */
                            font-size: 14px; /* Font size */
                            font-weight: bold; /* Font weight */
                            text-align: center; /* Align text in the center */
                            text-decoration: none; /* Remove underline */
                        }

                        QPushButton:hover {
                            /* Style when the mouse hovers over the button */
                            background-color: #66CDAA; /* Slightly darker green */
                            border-color: #696969; /* Match border color with background */
                        }

                        QPushButton:pressed {
                            /* Style when the button is pressed */
                            background-color: #3CB371; /* Even darker green */
                            border-color: #696969; /* Match border color */
                            color: #d4d4d4; /* Change text color */
                        }"""

        self.stop_style = """
            QPushButton {                                                                  
                /* Background color of the button */                                                           
                /*background-color: #4CAF50; /* Green */                                                       
                /*color: Black; /* Text color */                                                               
                max-width: 71px; /* Button width */                                                            
                max-height: 20px; /* Button height */                                                          
                border: 2px solid #696969; /* Border color */                                                  
                border-radius: 5px; /* Rounded corners */                                                      
                padding: 2px 2px; /* Padding for better spacing */                                             
                font-size: 14px; /* Font size */                                                               
                font-weight: bold; /* Font weight */                                                           
                text-align: center; /* Align text in the center */                                             
                text-decoration: none; /* Remove underline */                                                  
            }                                                                                                  
                                                                                                               
            QPushButton:hover {                                                            
                /* Style when the mouse hovers over the button */                                              
                background-color: #DC143C; /* Slightly darker green */                                         
                border-color: #696969; /* Match border color with background */                                
            }                                                                                                  
                                                                                                               
            QPushButton:pressed {                                                          
                /* Style when the button is pressed */                                                         
                background-color: #FF6347; /* Even darker green */                                             
                border-color: #696969; /* Match border color */                                                
                color: #d4d4d4; /* Change text color */                                                        
            }"""

        self.update_style = """
            QPushButton {                                                                
                /* Background color of the button */                                                             
                /*background-color: #4CAF50; /* Green */                                                         
                /*color: Black; /* Text color */                                                                 
                max-width: 160px; /* Button width */                                                              
                max-height: 20px; /* Button height */                                                            
                border: 2px solid #696969; /* Border color */                                                    
                border-radius: 5px; /* Rounded corners */                                                        
                padding: 2px 2px; /* Padding for better spacing */                                               
                font-size: 14px; /* Font size */                                                                 
                font-weight: bold; /* Font weight */                                                             
                text-align: center; /* Align text in the center */                                               
                text-decoration: none; /* Remove underline */                                                    
            }                                                                                                    
                                                                                 
            QPushButton:hover {                                                                                  
                /* Style when the mouse hovers over the button */                                                
                background-color: #00BFFF; /* Slightly darker green */                                           
                border-color: #696969; /* Match border color with background */                                  
            }                                                                                                    
                                                                                 
            QPushButton:pressed {                                                                                
                /* Style when the button is pressed */                                                           
                background-color: #87CEEB; /* Even darker green */                                               
                border-color: #696969; /* Match border color */                                                  
                color: #d4d4d4; /* Change text color */                                                          
            }"""

        self.menu_style = """
            QMenuBar {
                background-color: #2e3b4e;
                color: #ffffff;
                font-size: 16px;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 2px 5px;
                text-align: center; /* Centraliza o texto */
            }
            QMenuBar::item:selected {
                background: #4a6fa5;
            }
            QMenu {
                background-color: #2e3b4e;
                border: 1px solid #4a6fa5;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                color: #ffffff;
                padding: 6px 10px;
                margin: 2px 0;
                font-size: 16px;
                text-align: center; /* Centraliza o texto */
            }
            QMenu::item:selected {
                background-color: #4a6fa5;
                color: #ffffff;
            }
        """

        self.side_button_style = """
                        QPushButton {
                            /* Background color of the button */
                            /*background-color: #4CAF50; /* Green */
                            /*color: Black; /* Text color */
                            min-width: 80px; /* Button width */
                            /*max-height: 20px; /* Button height */
                            /*border: 2px solid #696969; /* Border color */
                            /*border-radius: 5px; /* Rounded corners */
                            padding: 2px 2px; /* Padding for better spacing */
                            font-size: 12px; /* Font size */
                            font-weight: bold; /* Font weight */
                            text-align: center; /* Align text in the center */
                            text-decoration: none; /* Remove underline */
                        }

                        QPushButton:hover {
                            /* Style when the mouse hovers over the button */
                            background-color: #92B08C; /* Slightly darker green */
                            border-color: #696969; /* Match border color with background */
                        }

                        QPushButton:pressed {
                            /* Style when the button is pressed */
                            background-color: #F4A460; /* Even darker green */
                            border-color: #696969; /* Match border color */
                            color: #d4d4d4; /* Change text color */
                        }"""

        self.unlock = False
        self.game = Game()

        self.setWindowTitle("T-R0XX BOT 1.0")
        self.setWindowIcon(QIcon("icons/bot.ico"))
        #self.setGeometry(100, 100, 800, 200)
        self.setFixedSize(810, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self._start_pos = None
        self.selected_pid = None  # PID do processo selecionado
        self.character_pid_map = {}  # Dicionário para mapear nomes a PIDs

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Menu Bar
        self.create_menu_bar()

        # Layouts
        main_layout = QVBoxLayout(self.central_widget)
        body_layout = QHBoxLayout()

        self.create_side_menu(body_layout)
        self.create_central_area(body_layout)
        self.create_right_list(body_layout)

        main_layout.addLayout(body_layout)
        self.create_footer(main_layout)

        # Load window data on startup
        self.load_window_data()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._start_pos:
            self.move(event.globalPosition().toPoint() - self._start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = None
            event.accept()

    def create_menu_bar(self):
        # Cria a barra de menus
        menu_bar = QMenuBar(self)
        menu_bar.setStyleSheet(self.menu_style)
        self.setMenuBar(menu_bar)

        """# Cria o menu "Donate" e adiciona ao menu bar
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)"""

        # Adiciona uma ação ao menu "Donate"
        donate_action = QAction("Donate", self)
        donate_action.triggered.connect(lambda: self.open_url("https://tonyrogerio.com.br/donations"))
        menu_bar.addAction(donate_action)


        # Adiciona ações ao menu "Help"
        youtube_action = QAction("YouTube", self)
        youtube_action.triggered.connect(lambda: self.open_url("https://www.youtube.com/@tonyr0xx"))
        menu_bar.addAction(youtube_action)

    def open_url(self, url):
        webbrowser.open(url)

    def create_side_menu(self, parent_layout):
        side_menu = QVBoxLayout()

        # Buttons
        self.home_button = QPushButton("Home")
        self.home_button.setStyleSheet(self.side_button_style)
        self.keys_button = QPushButton("Keys")
        self.keys_button.setStyleSheet(self.side_button_style)
        #self.deleter_button = QPushButton("Deleter")

        # Button actions
        self.home_button.clicked.connect(lambda: self.central_area.setCurrentIndex(0))  # Home no índice 0
        self.keys_button.clicked.connect(lambda: self.central_area.setCurrentIndex(1))  # Keys no índice 1
        #self.deleter_button.clicked.connect(lambda: self.central_area.setCurrentIndex(2))  # (Se necessário)

        # Add buttons to layout
        side_menu.addWidget(self.home_button)
        side_menu.addWidget(self.keys_button)
        #side_menu.addWidget(self.deleter_button)
        side_menu.addStretch()

        parent_layout.addLayout(side_menu)

    def create_central_area(self, parent_layout):
        self.central_area = QStackedWidget()
        parent_layout.addWidget(self.central_area)

        # Adiciona todas as páginas, incluindo Home com valores iniciais
        self.home_page = Home(self, pid=None)  # Inicializa sem PID
        self.keys_page = Keys(self)  # Página Keys
        #self.deleter_page = QWidget()  # Placeholder para Deleter

        self.central_area.addWidget(self.home_page)  # Página Home no índice 0
        self.central_area.addWidget(self.keys_page)  # Página Keys no índice 1
        #self.central_area.addWidget(self.deleter_page)  # Página Deleter no índice 2

    def create_right_list(self, parent_layout):
        self.right_layout_list = QVBoxLayout()

        # Update button
        self.update_button = QPushButton("Update List")
        self.update_button.setStyleSheet(self.update_style)
        self.update_button.setMaximumWidth(180)
        self.update_button.clicked.connect(self.update_list)

        # List widget
        self.right_list = QListWidget()
        self.right_list.setMaximumWidth(165)
        self.right_list.setStyleSheet("font-weight: bold; font-size: 18px; font-family: Consolas")
        self.right_list.itemClicked.connect(self.on_character_selected)  # Conecta o evento de clique

        # Add widgets to layout
        self.right_layout_list.addWidget(self.right_list)
        self.right_layout_list.addWidget(self.update_button)

        parent_layout.addLayout(self.right_layout_list)

    def create_footer(self, main_layout):
        footer_layout = QHBoxLayout()

        # Footer text
        self.footer = QLabel("")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Start/Stop buttons
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet(self.start_style)
        self.start_button.clicked.connect(self.start)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(self.stop_style)
        self.stop_button.clicked.connect(self.stop)

        # Footer button layout
        right_buttons_layout = QHBoxLayout()
        right_buttons_layout.addWidget(self.start_button)
        right_buttons_layout.addWidget(self.stop_button)

        footer_layout.addWidget(self.footer)
        footer_layout.addLayout(right_buttons_layout)

        main_layout.addLayout(footer_layout)

    def find_window_by_title(self):
        hwnds = []
        processes = []
        self.character_pid_map.clear()  # Limpa o mapeamento antes de atualizar

        # Step 1: Find processes with the name "client.exe"
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] and proc.info['name'].lower() == "client.exe":
                processes.append(proc.info['pid'])  # Armazena o PID do processo encontrado

        if not processes:
            print("Nenhum processo 'client.exe' encontrado.")
            return

        # Step 2: Find visible windows for these processes
        def enum_callback(hwnd, lparam):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in processes:
                    hwnds.append({'hwnd': hwnd, 'pid': pid, 'name': win32gui.GetWindowText(hwnd)})

        win32gui.EnumWindows(enum_callback, None)

        if not hwnds:
            print("Nenhuma janela visível associada ao 'client.exe' encontrada.")
            return

        # Step 3: Retrieve the character name using Pointers
        for hwnd_entry in hwnds:
            try:
                pointer = Pointers(hwnd_entry['pid'])  # Inicializa o ponteiro para o processo
                char_name = pointer.get_char_name()  # Obtém o nome do personagem
                hwnd_entry['character_name'] = char_name

                # Atualiza o mapeamento de nomes para PIDs
                self.character_pid_map[char_name] = hwnd_entry['pid']
            except Exception as e:
                hwnd_entry['character_name'] = "Home"
                print(f"Erro ao acessar o processo {hwnd_entry['pid']}: {e}")

        # Step 4: Save the data to a JSON file
        with open('characters/hwnd.json', 'w') as file:
            json.dump(hwnds, file, indent=4)

        print("Dados das janelas e personagens salvos em 'hwnd.json'.")

    def set_names(self, client, pid, contains, new_title):
        """
        Modifica o título de uma janela específica com base no PID e no texto do título.

        :param client: Nome do processo (exemplo: "client.exe").
        :param pid: PID do processo da janela que será modificada.
        :param contains: Texto que deve estar no título da janela para ser alterado.
        :param new_title: Novo título a ser definido na janela.
        :return: Lista com os identificadores das janelas alteradas.
        """

        def enum_callback(hwnd, lista):
            if win32gui.IsWindowVisible(hwnd):  # Verifica se a janela está visível
                tittle = win32gui.GetWindowText(hwnd)
                if contains in tittle:  # Verifica se o título contém o texto esperado
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid:  # Verifica se o PID corresponde ao esperado
                        for proc in psutil.process_iter(['pid', 'name']):
                            if proc.info['pid'] == pid and proc.info['name'].lower() == client.lower():
                                # Altera o título da janela
                                win32gui.SetWindowText(hwnd, new_title)
                                lista.append(hwnd)

        # Lista para armazenar as janelas que foram alteradas
        windows_changed = []
        win32gui.EnumWindows(enum_callback, windows_changed)
        return windows_changed

    def update_list(self):
        try:
            self.find_window_by_title()
            self.load_window_data()
        except Exception as e:
            print(f"Erro ao atualizar lista: {e}")

    def load_window_data(self):
        """Load window data from JSON file and update the list."""
        try:
            with open('characters/hwnd.json', 'r') as file:
                hwnd_data = json.load(file)
                self.right_list.clear()
                for item in hwnd_data:
                    # Adicionar apenas o nome do personagem à lista
                    character_name = item.get('character_name', 'Home')
                    self.right_list.addItem(character_name)
        except FileNotFoundError:
            print("Arquivo hwnd.json não encontrado.")

    def on_character_selected(self, item):
        self.unlock = True
        """Evento chamado ao selecionar um personagem na lista."""
        self.character_name = item.text()
        if self.character_name in self.character_pid_map:
            selected_pid = self.character_pid_map[self.character_name]

            # Verifica se o processo ainda existe pelo PID
            if not psutil.pid_exists(selected_pid):
                print(f"Processo com PID {selected_pid} não encontrado. Atualizando lista.")
                #self.update_list()
                return

            self.home_page.update_pid(selected_pid)
            print(f"Personagem selecionado: {self.character_name}, PID: {selected_pid}")

            client = "client.exe"
            pid = selected_pid
            contains = "Talisman Online"
            new_tittle = self.character_name
            self.set_names(client, pid, contains, new_tittle)

            # Atualiza settings
            self.home_page.load_settings()

        else:
            print("Personagem não encontrado no mapeamento.")

    def start(self):
        if self.unlock:
            if not self.character_name:
                print("Erro: Nenhum personagem selecionado.")
                return
            target = self.character_name
            print("Current Target = ", target)
            self.home_page.save_settings()
            self.game.load_game(target)

    def stop(self):
        if self.unlock:
            target = self.character_name
            self.game.stop_game(target)


class Home(QWidget):

    def __init__(self, main_window, pid=None):
        super().__init__()

        self.labels_style = """font-weight: bold; font-size: 14px; font-family: Consolas"""

        save_settings_style = """
        QPushButton {
            /* Background color of the button */
            /*background-color: #4CAF50; /* Green */
            /*color: Black; /* Text color */
            max-width: 120px; /* Button width */
            max-height: 20px; /* Button height */
            border: 2px solid #696969; /* Border color */
            border-radius: 5px; /* Rounded corners */
            padding: 2px 4px; /* Padding for better spacing */
            font-size: 14px; /* Font size */
            font-weight: bold; /* Font weight */
            text-align: center; /* Align text in the center */
            text-decoration: none; /* Remove underline */
        }

        QPushButton:hover {
            /* Style when the mouse hovers over the button */
            background-color: #008B8B; /* Slightly darker green */
            border-color: #696969; /* Match border color with background */
        }

        QPushButton:pressed {
            /* Style when the button is pressed */
            background-color: #3CB371; /* Even darker green */
            border-color: #696969; /* Match border color */
            color: #d4d4d4; /* Change text color */
        }"""

        self.button_style = """
                QPushButton {
                    /* Background color of the button */
                    /*background-color: #4CAF50; /* Green */
                    /*color: Black; /* Text color */
                    /*max-width: 120px; /* Button width */
                    /*max-height: 20px; /* Button height */
                    /*border: 2px solid #696969; /* Border color */
                    /*border-radius: 5px; /* Rounded corners */
                    padding: 2px 2px; /* Padding for better spacing */
                    font-size: 12px; /* Font size */
                    font-weight: bold; /* Font weight */
                    text-align: center; /* Align text in the center */
                    text-decoration: none; /* Remove underline */
                }

                QPushButton:hover {
                    /* Style when the mouse hovers over the button */
                    background-color: #92B08C; /* Slightly darker green */
                    border-color: #696969; /* Match border color with background */
                }

                QPushButton:pressed {
                    /* Style when the button is pressed */
                    background-color: #F4A460; /* Even darker green */
                    border-color: #696969; /* Match border color */
                    color: #d4d4d4; /* Change text color */
                }"""

        self.unlock = False
        self._image_create_active = False
        self._image_create_cancelled = False
        self.main_window = main_window
        self.pid = pid  # PID inicial (pode ser None)
        self.char_name = "Home"
        if self.char_name == "Home":
            main_window.update_list()
        self.pointers = None if pid is None else Pointers(pid)

        self.list_class = ["Stamina"]
        self.resolution_list = ["1024*768"]

        # Button to save settings
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet(save_settings_style)
        self.save_button.clicked.connect(self.save_settings)

        # Button to load settings
        self.load_button = QPushButton("Load Settings")
        self.load_button.clicked.connect(self.load_settings)

        self.home_layout = QVBoxLayout(self)
        self.center_layout = QHBoxLayout()

        # Título da página
        self.title_label = QLabel(f"{self.char_name}")
        self.title_label.setStyleSheet("color: #FF4500; font-weight: bold; font-size: 24px; font-family: Consolas")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Barra de progresso para o HP
        self.hp_bar = QProgressBar(self)
        self.hp_bar.setMinimum(0)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(0)

        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #363636;  /* Borda da barra */
                border-radius: 2px;         /* Bordas arredondadas */
                background: #1C1C1C;       /* Cor de fundo */
                font: bold 12px 'Consolas';   /* Fonte da barra */
                text-align: center;        /* Centraliza o texto */
                min-height: 15px;          /* Altura mínima da barra */
                max-height: 15px;
                max-width: 300px;
                min-width: 300px;
                
            }

            QProgressBar::chunk {
                background-color: #DC143C; /* Cor da parte preenchida */
                border-radius: 2px;        /* Bordas arredondadas na parte preenchida */
            }
        """)

        # Timer para atualização periódica
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_hp_bar)
        self.timer.start(100)  # Atualiza a cada 200ms

        # Select class
        self.char_class = QComboBox()
        self.char_class.setFixedHeight(18)
        self.char_class.addItems(self.list_class)
        self.char_class.setMaximumWidth(100)
        self.char_class.setMinimumWidth(100)
        self.char_class_tittle = QLabel("Character Type")
        self.char_class_tittle.setFont(QFont('Consolas', 12))
        self.resolution = QComboBox()
        self.resolution.addItems(self.resolution_list)
        self.resolution.setFixedHeight(18)
        self.resolution.setMaximumWidth(100)
        self.resolution.setMinimumWidth(100)

        # Add widgets to layout
        self.home_layout.addWidget(self.title_label)

        self.hp_bar_layout = QHBoxLayout()
        self.hp_bar_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.hp_bar_layout.addWidget(self.hp_bar)
        self.hp_bar_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.home_layout.addLayout(self.hp_bar_layout)

        self.h0 = QHBoxLayout()
        self.h0.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.h0.addWidget(self.char_class_tittle)
        self.h0.addWidget(self.char_class)
        self.h0.addWidget(self.resolution)
        self.h0.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.h0.addWidget(self.save_button)
        self.home_layout.addLayout(self.h0)
        self.home_layout.addWidget(QLabel(""))

        # LEFT LAYOUT
        self.left_layout = QVBoxLayout()
        # Slider for LOW_HP
        self.low_hp_slider = QSlider(Qt.Orientation.Horizontal)
        self.low_hp_slider.setRange(10, 100)
        self.low_hp_slider.setValue(40)
        self.low_hp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.low_hp_slider.setTickInterval(10)
        self.low_hp_slider.valueChanged.connect(self.update_low_hp_label)

        # Label for LOW_HP
        self.low_hp_label = QLabel(f"Low HP : {self.low_hp_slider.value():} % ")
        self.low_hp_label.setStyleSheet(self.labels_style)
        self.low_hp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider for BUFF_DELAY (in minutes)
        self.buff_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.buff_delay_slider.setRange(1, 30)  # 1 to 30 minutes
        self.buff_delay_slider.setValue(5)
        self.buff_delay_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.buff_delay_slider.setTickInterval(10)
        self.buff_delay_slider.valueChanged.connect(self.update_buff_delay_label)

        # Label for BUFF_DELAY
        self.buff_delay_label = QLabel(f"Buff Delay: {self.buff_delay_slider.value()} min")
        self.buff_delay_label.setStyleSheet(self.labels_style)
        self.buff_delay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider for PET_FOOD_DELAY (in minutes)
        self.pet_food_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.pet_food_delay_slider.setRange(1, 50)  # 1 to 30 minutes
        self.pet_food_delay_slider.setValue(45)
        self.pet_food_delay_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pet_food_delay_slider.setTickInterval(10)
        self.pet_food_delay_slider.valueChanged.connect(self.update_pet_food_delay_label)

        # Label for PET_FOOD_DELAY
        self.pet_food_delay_label = QLabel(f"Pet Food Delay: {self.pet_food_delay_slider.value()} min")
        self.pet_food_delay_label.setStyleSheet(self.labels_style)
        self.pet_food_delay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider for DELETER_DELAY (in minutes)
        self.deleter_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.deleter_delay_slider.setRange(1, 60)
        self.deleter_delay_slider.setValue(20)
        self.deleter_delay_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.deleter_delay_slider.setTickInterval(10)
        self.deleter_delay_slider.valueChanged.connect(self.update_deleter_delay_label)

        # Label for DELETER_DELAY
        self.deleter_delay_label = QLabel(f"Deleter Delay: {self.deleter_delay_slider.value()} min")
        self.deleter_delay_label.setStyleSheet(self.labels_style)
        self.deleter_delay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider for GET_BACK
        self.get_back_slider = QSlider(Qt.Orientation.Horizontal)
        self.get_back_slider.setRange(0, 50)
        self.get_back_slider.setValue(25)
        self.get_back_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.get_back_slider.setTickInterval(10)
        self.get_back_slider.valueChanged.connect(self.update_get_back_label)

        # Label for GET_BACK
        self.get_back_label = QLabel(f"Get Back Distance: {self.get_back_slider.value()} m")
        self.get_back_label.setStyleSheet(self.labels_style)
        self.get_back_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider for Unstuck speed
        self.unstuck_slider = QSlider(Qt.Orientation.Horizontal)
        self.unstuck_slider.setRange(0, 20)
        self.unstuck_slider.setValue(10)
        self.unstuck_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.unstuck_slider.setTickInterval(10)
        self.unstuck_slider.valueChanged.connect(self.update_unstuck_label)

        # Label for unstuck speed
        self.unstuck_label = QLabel(f"Unstuck Speed: {self.unstuck_slider.value()}")
        self.unstuck_label.setStyleSheet(self.labels_style)
        self.unstuck_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Checkbox for DELETER_BOT
        self.deleter_checkbox = QCheckBox("Delete Items")
        self.deleter_checkbox.setStyleSheet(self.labels_style)
        self.deleter_checkbox.setChecked(True)

        # Checkbox for GET_BACK (ON/OFF)
        self.get_back_checkbox = QCheckBox("Get Back System")
        self.get_back_checkbox.setStyleSheet(self.labels_style)
        self.get_back_checkbox.setChecked(True)

        # Checkbox for revive ad back
        self.revive_back_checkbox = QCheckBox("Revive and Back")
        self.revive_back_checkbox.setStyleSheet(self.labels_style)
        self.revive_back_checkbox.setChecked(True)

        # Checkbox for autopick
        self.autopick_checkbox = QCheckBox("Auto Pick Items")
        self.autopick_checkbox.setStyleSheet(self.labels_style)
        self.autopick_checkbox.setChecked(False)

        # Slider for AUTOPICK_DELAY (in seconds)
        self.autopick_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.autopick_delay_slider.setRange(1, 30)
        self.autopick_delay_slider.setValue(5)
        self.autopick_delay_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.autopick_delay_slider.setTickInterval(5)
        self.autopick_delay_slider.valueChanged.connect(self.update_autopick_delay_label)

        # Label for AUTOPICK_DELAY
        self.autopick_delay_label = QLabel(f"Autopick Delay: {self.autopick_delay_slider.value()} sec")
        self.autopick_delay_label.setStyleSheet(self.labels_style)
        self.autopick_delay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.l1 = QHBoxLayout() # LINHA 1
        self.l1.addWidget(self.low_hp_label)
        self.l1.addWidget(self.low_hp_slider)
        self.l3 = QHBoxLayout()
        self.l3.addWidget(self.pet_food_delay_label)
        self.l3.addWidget(self.pet_food_delay_slider)
        self.l4 = QHBoxLayout()
        self.l4.addWidget(self.buff_delay_label)
        self.l4.addWidget(self.buff_delay_slider)
        self.l5 = QHBoxLayout()
        self.l5.addWidget(self.deleter_delay_label)
        self.l5.addWidget(self.deleter_delay_slider)
        self.l6 = QHBoxLayout()
        self.l6.addWidget(self.get_back_label)
        self.l6.addWidget(self.get_back_slider)
        self.l7 = QHBoxLayout()
        self.l7.addWidget(self.unstuck_label)
        self.l7.addWidget(self.unstuck_slider)
        self.l8 = QHBoxLayout()
        self.l8.addWidget(self.deleter_checkbox)
        self.l8.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.l9 = QHBoxLayout()
        self.l9.addWidget(self.get_back_checkbox)
        self.l9.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.l11 = QHBoxLayout()
        self.l11.addWidget(self.revive_back_checkbox)
        self.l11.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.l12 = QHBoxLayout()
        self.l12.addWidget(self.autopick_checkbox)
        self.l12.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.l13 = QHBoxLayout()
        self.l13.addWidget(self.autopick_delay_label)
        self.l13.addWidget(self.autopick_delay_slider)

        self.left_layout.addLayout(self.l1)
        #self.left_layout.addLayout(self.l2)
        self.left_layout.addLayout(self.l3)
        self.left_layout.addLayout(self.l4)
        self.left_layout.addLayout(self.l5)
        self.left_layout.addLayout(self.l6)
        self.left_layout.addLayout(self.l7)
        self.left_layout.addLayout(self.l8)
        self.left_layout.addLayout(self.l9)
        self.left_layout.addLayout(self.l11)
        self.left_layout.addLayout(self.l12)
        self.left_layout.addLayout(self.l13)
        self.center_layout.addLayout(self.left_layout)

        self.right_layout = QVBoxLayout()

        self.spot_farm_label = QLabel(f"Spot Farm:")
        self.spot_farm_label.setStyleSheet(self.labels_style)
        self.spot_farm_input = QLineEdit("")
        self.spot_farm_input.setMaximumWidth(110)
        self.spot_farm_input.setPlaceholderText("Back after revive")

        self.get_cords_button = QPushButton("Get Cords")
        self.get_cords_button.setStyleSheet(self.button_style)
        self.get_cords_button.setMaximumWidth(110)
        self.get_cords_button.setMinimumWidth(80)
        self.get_cords_button.clicked.connect(self.get_cords)
        self.get_cords_input = QLineEdit("")
        self.get_cords_input.setMaximumWidth(110)
        self.get_cords_input.setPlaceholderText("Coordinates")
        self.get_cords_test_l = QPushButton("L")
        self.get_cords_test_l.setStyleSheet(self.button_style)
        self.get_cords_test_l.setMaximumWidth(20)
        self.get_cords_test_l.setMinimumWidth(14)
        self.get_cords_test_l.clicked.connect(self.cords_test_l)
        self.get_cords_test_r = QPushButton("R")
        self.get_cords_test_r.setStyleSheet(self.button_style)
        self.get_cords_test_r.setMaximumWidth(20)
        self.get_cords_test_r.setMinimumWidth(14)
        self.get_cords_test_r.clicked.connect(self.cords_test_r)

        self.get_image_button = QPushButton("Get Image")
        self.get_image_button.setStyleSheet(self.button_style)
        self.get_image_button.setMaximumWidth(110)
        self.get_image_button.setMinimumWidth(80)
        self.get_image_button.clicked.connect(self.image_create)
        self.get_image_input = QLineEdit("")
        self.get_image_input.setMaximumWidth(110)
        self.get_image_input.setMinimumWidth(110)
        self.get_image_input.setPlaceholderText("Image name")

        # Autopick coordinates
        self.autopick_coords_label = QLabel("Autopick Coords:")
        self.autopick_coords_label.setStyleSheet(self.labels_style)
        self.autopick_coords_input = QLineEdit("400,400")
        self.autopick_coords_input.setMaximumWidth(110)
        self.autopick_coords_input.setPlaceholderText("X,Y coordinates")
        
        self.get_autopick_button = QPushButton("Get Autopick")
        self.get_autopick_button.setStyleSheet(self.button_style)
        self.get_autopick_button.setMaximumWidth(110)
        self.get_autopick_button.setMinimumWidth(80)
        self.get_autopick_button.clicked.connect(self.get_autopick_coords)
        
        self.autopick_test_button = QPushButton("Test")
        self.autopick_test_button.setStyleSheet(self.button_style)
        self.autopick_test_button.setMaximumWidth(40)
        self.autopick_test_button.setMinimumWidth(40)
        self.autopick_test_button.clicked.connect(self.test_autopick_coords)

        self.r1 = QHBoxLayout()
        self.r1.addWidget(self.spot_farm_label)
        self.r1.addWidget(self.spot_farm_input)
        self.r5 = QHBoxLayout()
        self.r5.addWidget(self.get_cords_button)
        self.r5.addWidget(self.get_cords_test_l)
        self.r5.addWidget(self.get_cords_test_r)
        self.r5.addWidget(self.get_cords_input)
        self.r6 = QHBoxLayout()
        self.r6.addWidget(self.get_image_button)
        self.r6.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.r6.addWidget(self.get_image_input)
        self.r7 = QHBoxLayout()
        self.r7.addWidget(self.autopick_coords_label)
        self.r7.addWidget(self.autopick_coords_input)
        self.r8 = QHBoxLayout()
        self.r8.addWidget(self.get_autopick_button)
        self.r8.addWidget(self.autopick_test_button)
        self.r8.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.right_layout.addLayout(self.r1)
        self.right_layout.addLayout(self.r5)
        self.right_layout.addLayout(self.r6)
        self.right_layout.addLayout(self.r7)
        self.right_layout.addLayout(self.r8)
        self.right_layout.addItem(QSpacerItem(20, 300, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.center_layout.addLayout(self.right_layout)

        self.home_layout.addLayout(self.center_layout)

        ## Espaçador final##
        self.home_layout.addItem(QSpacerItem(20, 30, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.setLayout(self.home_layout)

    # Função para calcular porcentagem de HP
    def hp_bar_percentage(self):
        try:
            max_hp = Pointers(self.pid).get_max_hp()
            current_hp = Pointers(self.pid).get_hp()

            # Verifica se max_hp é válido para evitar divisão por zero
            if max_hp <= 0:
                return 0

            percentage = (current_hp / max_hp) * 100
            rounded_percentage = round(percentage, 2)

            # Garante que o percentual esteja no intervalo esperado
            if rounded_percentage < 0 or rounded_percentage > 100:
                return 0

            return rounded_percentage
        except Exception as e:
            # Log do erro (se necessário)
            # print(f"Erro ao calcular HP: {e}")
            return 0

    # Método para atualizar a barra de HP
    def update_hp_bar(self):
        if self.pid is not None:
            percentage = self.hp_bar_percentage()
            self.hp_bar.setValue(int(percentage))
            self.hp_bar.setFormat(f"{percentage:.2f}% HP")

        else:
            self.hp_bar.setValue(0)
            self.hp_bar.setFormat("0% HP")

    def update_low_hp_label(self):
        self.low_hp_label.setText(f"Low HP : {self.low_hp_slider.value():} % ")

    def update_get_back_label(self):
        self.get_back_label.setText(f"Get Back Distance: {self.get_back_slider.value()} m")

    def update_unstuck_label(self):
        self.unstuck_label.setText(f"Unstuck Speed: {self.unstuck_slider.value()}")

    def update_buff_delay_label(self):
        self.buff_delay_label.setText(f"Buff Delay: {self.buff_delay_slider.value()} min")

    def update_pet_food_delay_label(self):
        self.pet_food_delay_label.setText(f"Pet Food Delay: {self.pet_food_delay_slider.value()} min")

    def update_deleter_delay_label(self):
        self.deleter_delay_label.setText(f"Deleter Delay: {self.deleter_delay_slider.value()} min")

    def update_autopick_delay_label(self):
        self.autopick_delay_label.setText(f"Autopick Delay: {self.autopick_delay_slider.value()} sec")

    def image_create(self):
        """Captura a posição do mouse e salva uma área como imagem BMP."""
        if self._image_create_active:
            print("Image capture is already underway.")
            self.main_window.footer.setText("Image capture is already underway.")
            QApplication.processEvents()
            return

        self._image_create_active = True
        self._image_create_cancelled = False

        try:
            image_name = self.get_image_input.text()

            if not image_name.strip():
                print("Canceled operation or invalid entry.")
                self.get_image_input.setPlaceholderText("type image name")
                QApplication.processEvents()
                return

            image_name = image_name.strip()
            file_path = os.path.join("Images", "items", f"{image_name}.bmp")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            def on_press(key):
                """Handler para o pressionamento de teclas."""
                try:
                    if self._image_create_cancelled:
                        print("Image capture has been canceled.")
                        self.main_window.footer.setText("Image capture has been canceled.")
                        return False

                    if key == keyboard.Key.esc:
                        pt = POINT()
                        windll.user32.GetCursorPos(byref(pt))
                        mouse_x, mouse_y = pt.x, pt.y

                        # Tamanho fixo da captura
                        capture_size = 16
                        start_x = max(mouse_x - capture_size // 2, 0)
                        start_y = max(mouse_y - capture_size // 2, 0)
                        end_x = start_x + capture_size
                        end_y = start_y + capture_size

                        # Validação das coordenadas e captura da imagem
                        try:
                            bbox = (start_x, start_y, end_x, end_y)
                            img = ImageGrab.grab(bbox=bbox)
                            img.save(file_path, format="BMP")
                            print(f"Saved: {file_path}")
                            self.main_window.footer.setText(f"Saved: {file_path}")
                        except Exception as e:
                            print(f"Error: {e}")
                            self.main_window.footer.setText("Error.")

                        return False  # Encerra o listener
                except Exception as e:
                    print(f"Error: {e}")
                    return False  # Encerra o listener

            print("Move the mouse to the desired location and press ESC to capture the image.")
            self.main_window.footer.setText("Move the mouse to the desired location and press ESC to capture the image.")
            QApplication.processEvents()

            # Criação e gerenciamento do listener de forma segura
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()  # Aguarda até que o listener seja encerrado

        except Exception as e:
            print(f"Image capture error: {e}")

        finally:
            self._image_create_active = False
            print("Finished image capture.")
            self.main_window.footer.setText("")
            self.get_image_input.setPlaceholderText("Image name")

    def cancel_image_create(self):
        """Cancela a captura de imagem."""
        if self._image_create_active:
            self._image_create_cancelled = True
            self.main_window.footer.setText("Image capture has been canceled.")
            QApplication.processEvents()
            print("Image capture has been canceled.")

    def get_cords(self):
        """Captura a posição do mouse relativa à janela selecionada ao pressionar ESC."""
        if not self.pid:
            print("No window have been selected.")
            self.main_window.footer.setText("Select a window before capturing the coordinates.")
            QApplication.processEvents()
            return

        # Impede execução simultânea
        if getattr(self, "_spot_farm_active", False):
            print("The coordinate capture is already underway.")
            self.main_window.footer.setText("The coordinate capture is already underway.")
            QApplication.processEvents()
            return

        self._get_cords_active = True
        self._get_cords_cancelled = False

        try:
            # Obtém o identificador da janela (HWND) pelo PID
            hwnd = None

            def enum_callback(handle, _):
                _, process_pid = win32process.GetWindowThreadProcessId(handle)
                if process_pid == self.pid and win32gui.IsWindowVisible(handle):
                    nonlocal hwnd
                    hwnd = handle

            win32gui.EnumWindows(enum_callback, None)

            if not hwnd:
                print("The selected window could not be found.")
                self.main_window.footer.setText("The selected window could not be found.")
                QApplication.processEvents()
                self._get_cords_active = False
                return

            print(f"Janela selecionada (HWND): {hwnd}")

            # Obtém as coordenadas do cliente da janela
            client_pos = win32gui.ClientToScreen(hwnd, (0, 0))
            client_x, client_y = client_pos

            def on_press(key):
                try:
                    if self._get_cords_cancelled:
                        print("Coordinate capture has been canceled.")
                        return False

                    if key == keyboard.Key.esc:
                        pt = POINT()
                        windll.user32.GetCursorPos(ctypes.byref(pt))
                        mouse_x, mouse_y = pt.x, pt.y

                        # Calcula a posição relativa
                        relative_x = mouse_x - client_x
                        relative_y = mouse_y - client_y

                        # Validação dos valores capturados
                        if isinstance(relative_x, int) and isinstance(relative_y, int):
                            # Atualiza o campo de entrada
                            self.get_cords_input.setText(f"{relative_x},{relative_y}")
                            print(f"Coordenadas relativas capturadas: {relative_x},{relative_y}")
                        else:
                            print("Erro: Coordenadas capturadas são inválidas.")
                            self.main_window.footer.setText("Error when capturing coordinates.")
                            return False

                        self.main_window.footer.setText("")
                        QApplication.processEvents()
                        return False  # Encerra o listener
                except Exception as e:
                    print(f"Erro no listener de teclado: {e}")
                    self.main_window.footer.setText("Error when capturing coordinates.")
                    QApplication.processEvents()
                    return False  # Garante que o listener será encerrado

            self.main_window.footer.setText(
                "Move the mouse to the desired location and press ESC to capture the coordinates."
            )
            QApplication.processEvents()

            # Criação e gerenciamento do listener de forma segura
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            listener.wait()  # Aguarda até que o listener seja encerrado

        except Exception as e:
            print(f"Erro ao capturar posição relativa: {e}")
            self.main_window.footer.setText("Error when capturing coordinates.")
            QApplication.processEvents()

        finally:
            self._get_cords_active = False
            print("Captura de coordenadas finalizada.")

    def cancel_get_cords(self):
        """Cancela a captura de coordenadas."""
        if getattr(self, "_get_cords_active", False):
            self._get_cords_cancelled = True
            self.main_window.footer.setText("Captura de coordenadas cancelada.")
            QApplication.processEvents()
            print("Captura de coordenadas foi cancelada.")

    def cords_test_l(self):
        try:
            # Abrir e ler o arquivo JSON
            file_name = f"characters/{self.char_name}.json"
            with open(file_name, "r") as file:
                hwnd_data = json.load(file)

            # Verificar se o JSON contém o `CHAR_NAME` esperado
            if hwnd_data.get("CHAR_NAME") == self.char_name:
                hwnd = hwnd_data["HWND"]
                spot = hwnd_data["CORDS"]  # Exemplo: "59,83"

                # Separar as coordenadas
                spot_split = spot.split(",")  # ["59", "83"]
                xPos = int(spot_split[0])  # Converte o primeiro valor para inteiro
                yPos = int(spot_split[1])  # Converte o segundo valor para inteiro

                print(f"Character: {self.char_name}, HWND: {hwnd}, Spot: ({xPos}, {yPos})")

                # Realizar o clique no formato adequado
                time.sleep(0.1)
                left(hwnd, xPos, yPos)
                return hwnd
            else:
                # Caso o `CHAR_NAME` não corresponda
                print(f"No HWND found for character: {self.char_name}")
                return None

        except FileNotFoundError:
            print("Error: JSON file not found.")
        except json.JSONDecodeError:
            print("Error: JSON file is not properly formatted.")
        except KeyError as e:
            print(f"Error: Missing key in JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def cords_test_r(self):
        try:
            # Abrir e ler o arquivo JSON
            file_name = f"characters/{self.char_name}.json"
            with open(file_name, "r") as file:
                hwnd_data = json.load(file)

            # Verificar se o JSON contém o `CHAR_NAME` esperado
            if hwnd_data.get("CHAR_NAME") == self.char_name:
                hwnd = hwnd_data["HWND"]
                spot = hwnd_data["CORDS"]  # Exemplo: "59,83"

                # Separar as coordenadas
                spot_split = spot.split(",")  # ["59", "83"]
                xPos = int(spot_split[0])  # Converte o primeiro valor para inteiro
                yPos = int(spot_split[1])  # Converte o segundo valor para inteiro

                print(f"Character: {self.char_name}, HWND: {hwnd}, Spot: ({xPos}, {yPos})")

                # Realizar o clique no formato adequado
                time.sleep(0.1)
                right(hwnd, xPos, yPos)
                return hwnd
            else:
                # Caso o `CHAR_NAME` não corresponda
                print(f"No HWND found for character: {self.char_name}")
                return None

        except FileNotFoundError:
            print("Error: JSON file not found.")
        except json.JSONDecodeError:
            print("Error: JSON file is not properly formatted.")
        except KeyError as e:
            print(f"Error: Missing key in JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_autopick_coords(self):
        """Captura as coordenadas para o botão Pick up all"""
        if not self.pid:
            print("No window have been selected.")
            self.main_window.footer.setText("Select a window before capturing the coordinates.")
            QApplication.processEvents()
            return

        # Impede execução simultânea
        if getattr(self, "_autopick_coords_active", False):
            print("The coordinate capture is already underway.")
            self.main_window.footer.setText("The coordinate capture is already underway.")
            QApplication.processEvents()
            return

        self._autopick_coords_active = True
        self._autopick_coords_cancelled = False

        try:
            # Obtém o identificador da janela (HWND) pelo PID
            hwnd = None

            def enum_callback(handle, _):
                _, process_pid = win32process.GetWindowThreadProcessId(handle)
                if process_pid == self.pid and win32gui.IsWindowVisible(handle):
                    nonlocal hwnd
                    hwnd = handle

            win32gui.EnumWindows(enum_callback, None)

            if not hwnd:
                print("The selected window could not be found.")
                self.main_window.footer.setText("The selected window could not be found.")
                QApplication.processEvents()
                self._autopick_coords_active = False
                return

            print(f"Janela selecionada (HWND): {hwnd}")

            # Obtém as coordenadas do cliente da janela
            client_pos = win32gui.ClientToScreen(hwnd, (0, 0))
            client_x, client_y = client_pos

            def on_press(key):
                try:
                    if self._autopick_coords_cancelled:
                        print("Coordinate capture has been canceled.")
                        return False

                    if key == keyboard.Key.esc:
                        pt = POINT()
                        windll.user32.GetCursorPos(ctypes.byref(pt))
                        mouse_x, mouse_y = pt.x, pt.y

                        # Calcula a posição relativa
                        relative_x = mouse_x - client_x
                        relative_y = mouse_y - client_y

                        # Validação dos valores capturados
                        if isinstance(relative_x, int) and isinstance(relative_y, int):
                            # Atualiza o campo de entrada
                            self.autopick_coords_input.setText(f"{relative_x},{relative_y}")
                            print(f"Autopick coordinates captured: {relative_x},{relative_y}")
                        else:
                            print("Erro: Coordenadas capturadas são inválidas.")
                            self.main_window.footer.setText("Error when capturing coordinates.")
                            return False

                        self.main_window.footer.setText("")
                        QApplication.processEvents()
                        return False  # Encerra o listener
                except Exception as e:
                    print(f"Erro no listener de teclado: {e}")
                    self.main_window.footer.setText("Error when capturing coordinates.")
                    QApplication.processEvents()
                    return False  # Garante que o listener será encerrado

            self.main_window.footer.setText(
                "Move mouse over 'Pick up all' button and press ESC to capture coordinates."
            )
            QApplication.processEvents()

            # Criação e gerenciamento do listener de forma segura
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            listener.wait()  # Aguarda até que o listener seja encerrado

        except Exception as e:
            print(f"Erro ao capturar posição relativa: {e}")
            self.main_window.footer.setText("Error when capturing coordinates.")
            QApplication.processEvents()

        finally:
            self._autopick_coords_active = False
            print("Autopick coordinate capture finished.")

    def test_autopick_coords(self):
        """Testa as coordenadas do autopick clicando na posição configurada"""
        try:
            # Abre e lê o arquivo JSON
            file_name = f"characters/{self.char_name}.json"
            with open(file_name, "r") as file:
                hwnd_data = json.load(file)

            # Verifica se o JSON contém o CHAR_NAME esperado
            if hwnd_data.get("CHAR_NAME") == self.char_name:
                hwnd = hwnd_data["HWND"]
                autopick_coords = self.autopick_coords_input.text()  # Exemplo: "400,400"

                if autopick_coords and "," in autopick_coords:
                    # Separa as coordenadas
                    coords_split = autopick_coords.split(",")
                    xPos = int(coords_split[0])
                    yPos = int(coords_split[1])

                    print(f"Testing autopick at coordinates: ({xPos}, {yPos})")

                    # Realiza o clique no formato adequado
                    time.sleep(0.1)
                    left(hwnd, xPos, yPos)
                    print("Autopick test click performed")
                else:
                    print("Invalid autopick coordinates format")
            else:
                print(f"No HWND found for character: {self.char_name}")

        except FileNotFoundError:
            print("Error: JSON file not found.")
        except json.JSONDecodeError:
            print("Error: JSON file is not properly formatted.")
        except KeyError as e:
            print(f"Error: Missing key in JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during autopick test: {e}")

    def save_settings(self):
        if self.unlock:
            with open('characters/hwnd.json', 'r') as file:
                hwnd_data = json.load(file)

            # Loop through the JSON data to find the matching character_name
            for item in hwnd_data:
                if item["character_name"] == self.char_name:
                    hwnd = item["hwnd"]
                    pid = item["pid"]
            settings = {
                "CHAR_NAME": self.char_name,
                "CHAR_TYPE": self.char_class.currentText(),
                "HWND": hwnd,
                "PID": pid,
                "RESOLUTION": self.resolution.currentText(),
                "LOW_HP": self.low_hp_slider.value(),
                "PET_FOOD_DELAY": self.pet_food_delay_slider.value(),
                "BUFF_DELAY": self.buff_delay_slider.value(),
                "DELETER_BOT": "ON" if self.deleter_checkbox.isChecked() else "OFF",
                "DELETER_DELAY": self.deleter_delay_slider.value(),
                "SPOT_FARM": self.spot_farm_input.text(),
                "CORDS": self.get_cords_input.text(),
                "GET_BACK": "ON" if self.get_back_checkbox.isChecked() else "OFF",
                "DISTANCE": self.get_back_slider.value(),
                "UNSTUCK_SPEED": self.unstuck_slider.value(),
                "REVIVE_AND_BACK": "ON" if self.revive_back_checkbox.isChecked() else "OFF",
                "AUTOPICK_ENABLED": "ON" if self.autopick_checkbox.isChecked() else "OFF",
                "AUTOPICK_DELAY": self.autopick_delay_slider.value(),
            }
            
            # Adicionar coordenadas do autopick se disponíveis
            autopick_coords = self.autopick_coords_input.text()
            if autopick_coords and "," in autopick_coords:
                coords_split = autopick_coords.split(",")
                if len(coords_split) == 2:
                    try:
                        settings["AUTOPICK_X"] = int(coords_split[0])
                        settings["AUTOPICK_Y"] = int(coords_split[1])
                    except ValueError:
                        settings["AUTOPICK_X"] = 400
                        settings["AUTOPICK_Y"] = 400
            else:
                settings["AUTOPICK_X"] = 400
                settings["AUTOPICK_Y"] = 400
            try:
                file_name = f"characters/{self.char_name}.json"

                with open(file_name, "w") as json_file:
                    json.dump(settings, json_file, indent=4)
                print("Settings saved.")
            except Exception as e:
                print(f"Error saving settings: {e}")

    def load_settings(self):
        try:
            file_name = f"characters/{self.char_name}.json"

            with open(file_name, "r") as json_file:
                settings = json.load(json_file)
                self.char_class.setCurrentText(settings["CHAR_TYPE"])
                self.resolution.setCurrentText(settings["RESOLUTION"])
                self.low_hp_slider.setValue(int(settings["LOW_HP"]))
                self.pet_food_delay_slider.setValue(settings["PET_FOOD_DELAY"])
                self.buff_delay_slider.setValue(settings["BUFF_DELAY"])
                self.deleter_checkbox.setChecked(settings["DELETER_BOT"] == "ON")
                self.deleter_delay_slider.setValue(settings["DELETER_DELAY"])
                self.spot_farm_input.setText(settings["SPOT_FARM"])
                self.get_cords_input.setText(settings["CORDS"])
                self.get_back_checkbox.setChecked(settings["GET_BACK"] == "ON")
                self.get_back_slider.setValue(settings["DISTANCE"])
                self.unstuck_slider.setValue(settings["UNSTUCK_SPEED"])
                self.revive_back_checkbox.setChecked(settings["REVIVE_AND_BACK"] == "ON")
                
                # Carregar configurações do autopick
                self.autopick_checkbox.setChecked(settings.get("AUTOPICK_ENABLED", "OFF") == "ON")
                self.autopick_delay_slider.setValue(settings.get("AUTOPICK_DELAY", 5))
                
                # Carregar coordenadas do autopick
                autopick_x = settings.get("AUTOPICK_X", 400)
                autopick_y = settings.get("AUTOPICK_Y", 400)
                self.autopick_coords_input.setText(f"{autopick_x},{autopick_y}")

                print("Settings loaded.")
        except Exception as e:
            print(f"Saving new settings.")
            self.save_settings()

    def update_pid(self, pid):
        self.unlock = True
        """Atualiza o PID e o nome do personagem dinamicamente."""
        self.pid = pid
        self.pointers = Pointers(self.pid)
        self.char_name = self.pointers.get_char_name()
        self.title_label.setText(f"{self.char_name}")


class Keys(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Lista de opções disponíveis
        self.keys = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'Space', 'P', 'I', 'F', 'M', 'Q', 'W', 'E', 'R'
        ]

        # Dicionário para armazenar os valores selecionados
        self.selected_keys = {
            "SIT": "8",
            "SELECT_YOURSELF": "F1",
            "INVENTORY": "I",
            "FRIENDS": "F",
            "MAP": "M",
            "FOLLOW": "P",
            "MOUNT": "Space",
            "PET_FOOD": "0",
            "BUFF_1": "9",
            "BUFF_2": "9",
            "POTION_HP": "5",
            "POTION_MP": "6",
            "SKILL_1": "5",
            "SKILL_2": "2",
            "SKILL_3": "2",
            "SKILL_4": "1",
            "SKILL_5": "1",
            "SKILL_6": "1",
        }

        self.load_keys()

        # Layout principal
        self.keys_layout = QVBoxLayout(self)

        # Título
        keys_title = QLabel("Keys Settings")
        keys_title.setFont(QFont("Consolas", 16))
        keys_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        color_1 = QLabel("Used Above 45 % HP target")
        color_1.setStyleSheet("color: #9390DB; font-weight: bold; font-size: 16px; font-family: Consolas")
        color_2 = QLabel("Used Below 45 % HP target")
        color_2.setStyleSheet("color: #FF1493; font-weight: bold; font-size: 16px; font-family: Consolas")
        skills_description = QHBoxLayout()
        skills_description.addWidget(color_1)
        skills_description.addWidget(color_2)

        self.keys_layout.addWidget(keys_title)
        self.keys_layout.addLayout(skills_description)

        # Layout para os rótulos e combos
        self.top_layout = QHBoxLayout()
        self.khorizontal_1 = QVBoxLayout()
        self.khorizontal_2 = QVBoxLayout()

        # Adiciona todos os combos e labels
        for key_name in self.selected_keys.keys():
            label, combo = self.create_combobox(key_name)
            #print(label.text())
            if label.text() == "Skill 1:":
                label.setStyleSheet("color: #9390DB; font-weight: bold; font-size: 16px; font-family: Consolas")
            if label.text() == "Skill 2:":
                label.setStyleSheet("color: #9390DB; font-weight: bold; font-size: 16px; font-family: Consolas")
            if label.text() == "Skill 3:":
                label.setStyleSheet("color: #9390DB; font-weight: bold; font-size: 16px; font-family: Consolas")
            if label.text() == "Skill 4:":
                label.setStyleSheet("color: #FF1493; font-weight: bold; font-size: 16px; font-family: Consolas")
            if label.text() == "Skill 5:":
                label.setStyleSheet("color: #FF1493; font-weight: bold; font-size: 16px; font-family: Consolas")
            if label.text() == "Skill 6:":
                label.setStyleSheet("color: #FF1493; font-weight: bold; font-size: 16px; font-family: Consolas")
            self.khorizontal_1.addWidget(label)
            self.khorizontal_2.addWidget(combo)

        # Adiciona layouts ao layout superior
        self.top_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.top_layout.addLayout(self.khorizontal_1)
        self.top_layout.addLayout(self.khorizontal_2)
        self.top_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Adiciona o layout superior ao layout principal
        self.keys_layout.addLayout(self.top_layout)

    def create_combobox(self, key_name):
        """
        Cria um QLabel e QComboBox associados a uma chave.
        """
        label = QLabel(f"{key_name.capitalize().replace('_', ' ')}:")
        label.setFixedHeight(18)
        label.setStyleSheet("font-weight: bold; font-size: 16px; font-family: Consolas")

        combo = QComboBox()
        combo.setFixedHeight(20)
        combo.addItems(self.keys)
        combo.setMaximumWidth(100)

        list_view = QListView()
        list_view.setStyleSheet("font-size: 12px;")
        combo.setView(list_view)

        # Conecta o evento de mudança para atualizar o dicionário
        combo.currentTextChanged.connect(
            lambda text, key=key_name: self.update_key_value(key, text)
        )

        # Define o valor inicial no combo
        combo.setCurrentText(self.selected_keys[key_name])

        return label, combo

    def update_key_value(self, key, value):
        """
        Atualiza o valor da chave no dicionário quando o combo é alterado.
        """
        self.selected_keys[key] = value
        #print(f"Atualizado: {key} -> {value}")  # Debug para ver atualizações
        self.save_keys()

    def save_keys(self):
        with open("characters/keys.json", "w") as json_file:
            json.dump(self.selected_keys, json_file, indent=4)

    def load_keys(self):
        if not os.path.exists("characters/keys.json"):

            with open("characters/keys.json", "w") as json_file:
                json.dump(self.selected_keys, json_file, indent=4)
                print("Arquivo 'keys.json' criado com os valores padrão.")

        with open("characters/keys.json", "r") as json_file:
            self.selected_keys = json.load(json_file)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/bot.ico"))
    app.setStyle('Fusion') # Puxa o tema do sistema
    bot = Main()
    bot.show()
    sys.exit(app.exec())
