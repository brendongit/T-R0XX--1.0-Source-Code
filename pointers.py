import math
import re
import pymem


class Pointers:
    def __init__(self, pid):
        self.pm = pymem.Pymem()
        self.pm.open_process_from_id(pid)
        self.CLIENT = self.pm.base_address

        # Ponteiros existentes
        self.DC_POINTER = 0x012CE35C
        self.CHAR_NAME_POINTER = 0x011450EC
        self.LEVEL_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x3C4])
        self.HP_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x3B8])
        self.HP_PLUS_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0xE4])
        self.HP_BUFF_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0xE0])
        self.MAX_HP_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0xDC])
        self.GOLD_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x410])

        self.MANA_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x3BC])
        self.MANA_BUFF_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x6F0])
        self.MAX_MANA_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x6EC])

        self.X_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x810])
        self.Y_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x814])

        self.BATTLE_STATUS_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x854])
        self.SIT_POINTER = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0x290])

        self.TARGET_HP_POINTER = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x59C, 0x0, 0xC, 0x1F4, 0x15C, 0x480])
        self.TARGET_SELECT = self.get_pointer(self.CLIENT + 0x00EC05C8, offsets=[0xD0, 0x2DC, 0x24, 0xC10])
        self.TARGET_NAME_POINTER = self.get_pointer(0x012CE2E0, offsets=[0x18, 0xB1C, 0x0, 0xC, 0xD9C])
        self.TARGET_NAME_POINTER_2 = self.get_pointer(0x012CE2E0, offsets=[0x18, 0xB1C, 0x0, 0xC, 0x1F8, 0x43C])

        self.TEAM_SIZE_POINTER = self.get_pointer(0x0106D328, offsets=[0x3D8])
        self.TEAM_NAME_1 = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x77C, 0x0, 0xC, 0x678, 0x8B4])
        self.TEAM_NAME_2 = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x34C, 0x0, 0xC, 0x678, 0x8B4])
        self.TEAM_NAME_3 = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x3F4, 0x0, 0xC, 0x1F4, 0x15C])
        self.TEAM_NAME_4 = self.get_pointer(0x012CE2E0, offsets=[0x18, 0xA1C, 0x0, 0xC, 0x1F4, 0x54])

        self.BAG_OPEN_POINTER = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x5C4, 0x0, 0xC, 0x1F8, 0x42C, 0xBA0])
        
        # ✅ NOVOS PONTEIROS PARA LOOT PULL
        self.LOOT_POINTER = self.get_pointer(self.CLIENT + 0x00EC05C8, offsets=[0xD0, 0x7F4, 0x0, 0x24, 0x40])
        self.LOOT_WINDOW = 0x0105B958
        self.TARGET_ID = 0x115CB20
        
        # Sistema de busca de objetos
        self.base = 0x0107C6B0
        self.basei = 0x0
        self.BASE_MIN = 0x0000CE00
        self.BASE_MAX = 0x0EFFFFFF

    def get_pointer(self, base_address, offsets):
        """
        Calcula o ponteiro final seguindo uma cadeia de offsets.
        """
        try:
            address = base_address
            for offset in offsets:
                address = self.pm.read_int(address) + offset
            return address
        except Exception as e:
            return None

    def read_value(self, address, data_type="byte"):
        try:
            if data_type == "byte":
                return self.pm.read_bytes(address, 1)[0]
            elif data_type == "int":
                return self.pm.read_int(address)
            elif data_type == "float":
                return self.pm.read_float(address)
            else:
                print(f"Tipo de dado desconhecido: {data_type}")
                return None
        except Exception as e:
            return None

    def read_string_from_pointer(self, base_pointer, offset=0, max_length=50):
        try:
            pointer_address = self.pm.read_int(base_pointer)
            final_address = pointer_address + offset
            byte_data = self.pm.read_bytes(final_address, max_length)
            string_data = byte_data.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
            return string_data
        except Exception as e:
            print(f"String Error: {e}")
            return "Offline Account"

    def get_char_name(self):
        name = self.read_string_from_pointer(self.CHAR_NAME_POINTER, offset=0xBC, max_length=50)

        if re.match(r"^[\w]+$", name):
            return name

        pointer = self.get_pointer(self.CLIENT + 0x00D450EC, offsets=[0xBC])
        if pointer:
            name = self.read_string_from_pointer(pointer, offset=0x0, max_length=50)
        return name

    def get_target_name(self):
        name = self.read_string_from_pointer(self.TARGET_NAME_POINTER, offset=0x9AC, max_length=50)
        if re.match(r"^[\w ]+$", name):
            return name

        pointer = self.get_pointer(0x012CE2E0, offsets=[0x18, 0xB1C, 0x0, 0xC, 0xD9C, 0x9AC])
        if pointer:
            name = self.read_string_from_pointer(pointer, offset=0x0, max_length=50)
        return name

    def team_name_1(self):
        name = self.read_string_from_pointer(self.TEAM_NAME_1, offset=0x4F4, max_length=50)
        if re.match(r"^[\w]+$", name):
            return name
        pointer = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x77C, 0x0, 0xC, 0x678, 0x8B4, 0x4F4])
        if pointer:
            name = self.read_string_from_pointer(pointer, offset=0x0, max_length=50)
        return name

    def team_name_2(self):
        name = self.read_string_from_pointer(self.TEAM_NAME_2, offset=0x4F4, max_length=50)
        if re.match(r"^[\w]+$", name):
            return name
        pointer = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x34C, 0x0, 0xC, 0x678, 0x8B4, 0x4F4])
        if pointer:
            name = self.read_string_from_pointer(pointer, offset=0x0, max_length=50)
        return name

    def team_name_3(self):
        name = self.read_string_from_pointer(self.TEAM_NAME_3, offset=0x54, max_length=50)
        if re.match(r"^[\w]+$", name):
            return name
        pointer = self.get_pointer(0x012CE2E0, offsets=[0x18, 0x3F4, 0x0, 0xC, 0x1F4, 0x15C, 0x54])
        if pointer:
            name = self.read_string_from_pointer(pointer, offset=0x0, max_length=50)
        return name

    def team_name_4(self):
        name = self.read_string_from_pointer(self.TEAM_NAME_4, offset=0x54, max_length=50)
        if re.match(r"^[\w]+$", name):
            return name
        pointer = self.get_pointer(0x012CE2E0, offsets=[0x18, 0xA1C, 0x0, 0xC, 0x1F4, 0x54, 0x54])
        if pointer:
            name = self.read_string_from_pointer(pointer, offset=0x0, max_length=50)
        return name

    def get_level(self):
        return self.read_value(self.LEVEL_POINTER, data_type="byte")

    def is_target_selected(self):
        if self.TARGET_SELECT is None:
            print("Erro: Ponteiro TARGET_SELECT não calculado.")
            return False

        target = self.read_value(self.TARGET_SELECT, data_type="byte")
        if target == 1:
            return True
        return False

    def target_hp(self):
        hp = self.read_value(self.TARGET_HP_POINTER, data_type="int")
        return hp

    def target_hp_full(self):
        return self.read_value(self.TARGET_HP_POINTER, data_type="int") == 597

    def is_target_dead(self):
        dead = self.read_value(self.TARGET_HP_POINTER, data_type="int")
        if dead == 0:
            return True

    def get_hp(self):
        return self.read_value(self.HP_POINTER, data_type="int")

    def get_hp_plus(self):
        plus = self.read_value(self.HP_PLUS_POINTER, data_type="byte")
        if plus >= 100:
            return plus - 100
        else:
            return plus

    def get_hp_buff(self):
        return self.read_value(self.HP_BUFF_POINTER, data_type="int")

    def get_max_hp(self):
        base_hp = self.read_value(self.MAX_HP_POINTER, data_type="int")
        buff_hp = self.get_hp_buff()
        hp_total = base_hp + buff_hp
        plus = self.get_hp_plus()

        if plus == 1:
            print("IGUAL 1")
            return base_hp
        else:
            return math.floor(((hp_total * plus) / 100) + hp_total)

    def get_mana(self):
        return self.read_value(self.MANA_POINTER, data_type="int")

    def get_mana_buff(self):
        return self.read_value(self.MANA_BUFF_POINTER, data_type="int")

    def get_max_mana(self):
        base_mana = self.read_value(self.MAX_MANA_POINTER, data_type="int")
        buff_mana = self.get_mana_buff()
        mana_total = base_mana + buff_mana
        return mana_total

    def is_in_battle(self):
        battle = self.read_value(self.BATTLE_STATUS_POINTER, data_type="byte")
        if battle == 1:
            return True

    def is_sitting(self):
        sitting = self.read_value(self.SIT_POINTER, data_type="byte")
        if sitting == 200:
            return True
        else:
            return False

    def get_x(self):
        x = self.read_value(self.X_POINTER, data_type="float") / 20
        return x > 0 and math.floor(x) or math.ceil(x)

    def get_y(self):
        y = self.read_value(self.Y_POINTER, data_type="float") / 20
        return y > 0 and math.floor(y) or math.ceil(y)

    def is_bag_open(self):
        bag = self.read_value(self.BAG_OPEN_POINTER, data_type="int")
        if bag == 903:
            return True

    def get_team_size(self):
        team = self.read_value(self.TEAM_SIZE_POINTER, data_type="int")
        if team is None:
            return 0
        else:
            return team

    def get_dc(self):
        dc = self.read_value(self.DC_POINTER, data_type="int")
        return dc

    def get_gold(self):
        return self.read_value(self.GOLD_POINTER, data_type="int")

    # ✅ NOVAS FUNÇÕES PARA LOOT PULL
    
    def get_target_id(self):
        """Obtém o ID do alvo atual"""
        id_value = self.read_value(self.TARGET_ID, data_type="int")
        if id_value is None:
            return None
        try:
            return hex(id_value)[2:].upper()
        except Exception as e:
            print(f"Erro ao converter ID para hexadecimal: {e}")
            return None

    def search_id(self):
        """
        Busca por objetos no mapa e retorna suas coordenadas
        """
        try:
            targetid = self.get_target_id()
            if targetid is None:
                return None, None, None

            # Busca crescente
            current_base = self.base
            while current_base <= self.BASE_MAX:
                try:
                    a = self.read_value(current_base + self.basei, "int")
                    if a is None:
                        current_base += 0x4
                        continue

                    b = a + 0x8
                    c_value = self.read_value(b, "int")
                    if c_value is None:
                        current_base += 0x4
                        continue

                    c = hex(c_value)[2:].upper()

                    if c == targetid:
                        # Encontrou o objeto
                        pointer = self.read_value(current_base + self.basei, "int")
                        if pointer is None:
                            return None, None, None

                        # Lê as coordenadas
                        x_value = self.read_value(pointer + 0x810, "float")
                        y_value = self.read_value(pointer + 0x814, "float")

                        if x_value is None or y_value is None:
                            return None, None, None

                        target_x = int(x_value / 20)
                        target_y = int(y_value / 20)

                        self.base = current_base
                        return target_x, target_y, pointer

                    current_base += 0x4

                except Exception:
                    current_base += 0x4
                    continue

            return None, None, None

        except Exception as e:
            print(f"Erro durante a busca: {e}")
            return None, None, None

    def write_position(self, pointer, x, y):
        """
        Escreve nova posição para um objeto na memória
        """
        try:
            basex = pointer + 0x810
            basey = pointer + 0x814

            self.pm.write_float(basex, float(x))
            self.pm.write_float(basey, float(y))
            return True

        except Exception as e:
            print(f"Erro ao definir posição: {e}")
            return False

    def is_loot(self):
        """Verifica se há loot disponível"""
        try:
            loot = self.read_value(self.LOOT_POINTER, data_type="int")
            return loot and loot > 0
        except:
            return False

    def loot_window(self):
        """Verifica se a janela de loot está aberta"""
        try:
            l = self.read_value(self.LOOT_WINDOW, data_type="int")
            if l is None:
                return False
            return l == 1
        except:
            return False

    # Funções auxiliares para coordenadas brutas
    def char_x(self):
        """Coordenadas X brutas do personagem"""
        x = self.read_value(self.X_POINTER, data_type="float")
        return x if x is not None else 0

    def char_y(self):
        """Coordenadas Y brutas do personagem"""  
        y = self.read_value(self.Y_POINTER, data_type="float")
        return y if y is not None else 0