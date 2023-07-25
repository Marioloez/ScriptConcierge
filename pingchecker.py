import time
import requests
from ping3 import ping, verbose_ping

# Configuración de las IPs a monitorear con sus etiquetas/nombres
ips_to_monitor = {
    "192.168.1.1": "Controladora Aruba",
    "8.8.8.8": "Servidor DNS de Google"
}

ping_interval = 60  # Tiempo en segundos entre cada ping
alert_interval = 300  # Tiempo en segundos entre cada alerta

# Configuración de Discord
discord_webhook_url = "https://discord.com/api/webhooks/xxxxxxxxxxxxxx"  # Reemplaza con tu URL de webhook de Discord

def send_discord_alert(message):
    payload = {
        "content": message
    }
    requests.post(discord_webhook_url, json=payload)

def send_discord_startup_notification():
    # Envía un mensaje de inicio cuando se inicia el script por Discord
    startup_message = "El script de monitoreo de IPs ha comenzado a funcionar."
    send_discord_alert(startup_message)

# Un diccionario para mantener el estado actual de cada IP y el tiempo de la última alerta enviada
ip_status = {ip: True for ip in ips_to_monitor}
last_alert_time = {ip: 0 for ip in ips_to_monitor}

# Enviar el mensaje de inicio al inicio del script
send_discord_startup_notification()

while True:
    current_time = time.time()
    for ip_to_ping, label in ips_to_monitor.items():
        response_time = ping(ip_to_ping)

        if response_time is not None:
            if not ip_status[ip_to_ping]:
                print(f"{label} ({ip_to_ping}) ha vuelto a responder.")
                send_discord_alert(f"{label} ({ip_to_ping}) ha vuelto a responder.")
            ip_status[ip_to_ping] = True
            print(f"{label} ({ip_to_ping}) respondió en {response_time} segundos.")
        else:
            if current_time - last_alert_time[ip_to_ping] >= alert_interval:
                print(f"¡ALERTA! {label} ({ip_to_ping}) no ha respondido.")
                send_discord_alert(f"¡ALERTA! {label} ({ip_to_ping}) no ha respondido.")
                last_alert_time[ip_to_ping] = current_time

            ip_status[ip_to_ping] = False

    time.sleep(ping_interval)
