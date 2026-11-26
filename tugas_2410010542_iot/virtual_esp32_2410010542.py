import time
import random
import paho.mqtt.client as mqtt

# MQTT configuration
BROKER = "127.0.0.1"
PORT = 1883
NIM = "2410010542"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

# Virtual device state (no physical GPIO)
relay_status = False
pwm_value = 0
suhu_virtual = 28.0


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT berhasil terhubung! Virtual ESP32 aktif.")
        client.subscribe(TOPIC_RELAY)
        client.subscribe(TOPIC_PWM)
        print("Subscribe Relay:", TOPIC_RELAY)
        print("Subscribe PWM  :", TOPIC_PWM)
    else:
        print("MQTT gagal terhubung. Kode:", rc)


def on_message(client, userdata, msg):
    global relay_status, pwm_value
    pesan = msg.payload.decode().strip()

    if msg.topic == TOPIC_RELAY:
        if pesan.upper() == "ON":
            relay_status = True
            print("Relay Virtual GPIO 26: ON")
        elif pesan.upper() == "OFF":
            relay_status = False
            print("Relay Virtual GPIO 26: OFF")
        else:
            print("Perintah relay tidak dikenal:", pesan)

    elif msg.topic == TOPIC_PWM:
        try:
            pwm_value = max(0, min(255, int(pesan)))
            persen = round((pwm_value / 255) * 100)
            print("PWM Virtual GPIO 2:", pwm_value)
            print("Kecerahan LED Virtual:", persen, "%")
        except ValueError:
            print("Nilai PWM tidak valid:", pesan)


client = mqtt.Client(client_id="VirtualESP32_2410010542")
client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke MQTT Broker...")
client.connect(BROKER, PORT, 60)
client.loop_start()

print("Simulasi sensor suhu berjalan; pengiriman setiap 3 detik.")
try:
    while True:
        suhu_virtual += random.uniform(-0.3, 0.3)
        suhu_virtual = max(26.0, min(32.0, suhu_virtual))
        suhu = round(suhu_virtual, 2)
        client.publish(TOPIC_SUHU, str(suhu))
        print("Suhu Virtual DHT22:", suhu, "°C")
        time.sleep(3)
except KeyboardInterrupt:
    print("\nSimulator dihentikan.")
    client.loop_stop()
    client.disconnect()
