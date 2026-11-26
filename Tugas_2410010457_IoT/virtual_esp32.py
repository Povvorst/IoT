import time
import random
import paho.mqtt.client as mqtt

# =====================================
# KONFIGURASI MQTT
# =====================================
BROKER = "127.0.0.1"
PORT = 1883
NIM = "2410010457"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

# =====================================
# STATUS PERANGKAT VIRTUAL
# =====================================
relay_status = False
pwm_value = 0
suhu_virtual = 28.0


# =====================================
# SAAT MQTT TERHUBUNG
# =====================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT berhasil terhubung!")
        print("Virtual ESP32 aktif.")
        print("--------------------------------")

        client.subscribe(TOPIC_RELAY)
        client.subscribe(TOPIC_PWM)

        print("Subscribe Relay:", TOPIC_RELAY)
        print("Subscribe PWM  :", TOPIC_PWM)
    else:
        print("MQTT gagal terhubung. Kode:", rc)


# =====================================
# SAAT MENERIMA PESAN
# =====================================
def on_message(client, userdata, msg):
    global relay_status, pwm_value

    pesan = msg.payload.decode().strip()

    # Simulasi relay
    if msg.topic == TOPIC_RELAY:
        if pesan.upper() == "ON":
            relay_status = True
            print("Relay Virtual GPIO 26: ON")

        elif pesan.upper() == "OFF":
            relay_status = False
            print("Relay Virtual GPIO 26: OFF")

        else:
            print("Perintah relay tidak dikenal:", pesan)

    # Simulasi PWM
    elif msg.topic == TOPIC_PWM:
        try:
            pwm_value = int(pesan)
            pwm_value = max(0, min(255, pwm_value))

            persen = round((pwm_value / 255) * 100)

            print("PWM Virtual GPIO 2:", pwm_value)
            print("Kecerahan LED Virtual:", persen, "%")

        except ValueError:
            print("Nilai PWM tidak valid:", pesan)


# =====================================
# MEMBUAT CLIENT MQTT
# =====================================
client = mqtt.Client(client_id="VirtualESP32_2410010457")

client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke MQTT Broker...")
client.connect(BROKER, PORT, 60)

# Menjalankan penerima pesan MQTT
client.loop_start()

# =====================================
# SIMULASI SENSOR DHT22
# =====================================
print("Simulasi sensor suhu berjalan...")
print("Pengiriman suhu setiap 3 detik.")
print("--------------------------------")

try:
    while True:
        # Perubahan suhu kecil setiap interval
        suhu_virtual += random.uniform(-0.3, 0.3)

        # Batasi suhu simulasi 26 hingga 32°C
        suhu_virtual = max(26, min(32, suhu_virtual))

        # Kirim data suhu MQTT
        suhu = round(suhu_virtual, 2)

        client.publish(TOPIC_SUHU, str(suhu))

        print("Suhu Virtual DHT22:", suhu, "°C")

        time.sleep(3)

except KeyboardInterrupt:
    print("\nSimulator dihentikan.")

    client.loop_stop()
    client.disconnect()