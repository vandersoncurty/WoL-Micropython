import network
import socket
import time
import gc
from utelegram import ubot
import config

def read_last_update_id():
    try:
        with open('last_update_id.txt', 'r') as file:
            return int(file.read().strip())
    except:
        return 0

def save_last_update_id(update_id):
    with open('last_update_id.txt', 'w') as file:
        file.write(str(update_id))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(config.SSID, config.PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print(".", end="")
    print("\nConectado ao Wi-Fi! IP:", wlan.ifconfig()[0])

def send_wol(mac):
    mac_bytes = bytes(int(x, 16) for x in mac.split(":"))
    if len(mac_bytes) != 6:
        raise ValueError("Endereço MAC inválido!")

    packet = b"\xFF" * 6 + mac_bytes * 16

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    s.sendto(packet, (config.BROADCAST_IP, config.PORT))
    s.close()
    print("Pacote WoL enviado!")

def handle_command(message):
    text = message['message'].get('text', '')
    chat_id = message['message'].get('chat', {}).get('id', '')
    update_id = message['update_id']
    
    last_update_id = read_last_update_id()
    
    if update_id > last_update_id:
        if text.lower() == "/wol":
            try:
                send_wol(config.MAC_ADDRESS)
                bot.send(chat_id, "Pacote WoL enviado!")
                save_last_update_id(update_id)
            except Exception as e:
                bot.send(chat_id, f"Erro: {e}")
    else:
        print("Comando já processado.")

bot = ubot(config.BOT_TOKEN)

bot.register("/wol", handle_command)

def main():
    connect_wifi()
    bot.send(config.CHAT_ID, "ESP32 conectado! Envie /wol para ligar o computador.")
    bot.listen()

if __name__ == "__main__":
    main()
