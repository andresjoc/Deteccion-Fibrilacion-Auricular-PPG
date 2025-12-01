import asyncio
import csv
from datetime import datetime
from bleak import BleakClient, BleakScanner, BleakError

# Dirección MAC del dispositivo
DEVICE_ADDRESS = "E7:CF:A3:30:D8:9E"

# UUID de la característica a la que deseas suscribirte
CHAR_UUID = "00000010-0000-3512-2118-0009af100700"  # ← Reemplaza con tu UUID

# Nombre del archivo CSV de salida
CSV_FILENAME = "datos_BLR.csv"

# Función para manejar notificaciones entrantes y guardar al CSV
def notification_handler(sender, data):
    print("🟡 LLEGÓ UNA NOTIFICACIÓN 🟡")  # Marca clara
    timestamp = datetime.now().isoformat()
    decoded_data = data.hex()  # data.decode() si se espera texto

    print(f"🔔 Notificación de {sender}: {decoded_data}")

    with open(CSV_FILENAME, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, sender, decoded_data])


# Función para conectarse y suscribirse
async def subscribe_and_log(address: str, uuid: str):
    try:
        print(f"Conectando al dispositivo {address} ...")
        async with BleakClient(address) as client:
            if not client.is_connected:
                print("❌ No se pudo conectar al dispositivo.")
                return

            print("✅ Conectado al dispositivo BLE.")

            # Comprobamos si el UUID está disponible
            services = client.services  
            found = any(uuid.lower() == char.uuid.lower() for service in services for char in service.characteristics)
            if not found:
                print(f"❌ La característica con UUID {uuid} no fue encontrada en el dispositivo.")
                return

            print("📝 Creando archivo CSV...")
            with open(CSV_FILENAME, mode="w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "sender", "data"])

            print("🔔 Iniciando suscripción...")
            await client.start_notify(uuid, notification_handler)
            print(f"🟢 Suscripción iniciada a UUID: {uuid}")

            print("⌛ Recibiendo datos. Presiona Ctrl+C para detener.")
            while True:
                await asyncio.sleep(1)

    except BleakError as e:
        print(f"❌ Error de BLE: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

async def list_device_uuids(address: str):
    print(f"Escaneando para conectar al dispositivo con dirección {address} ...")
    devices = await BleakScanner.discover(timeout=5.0)
    found = False

    for d in devices:
        if d.address.upper() == address.upper():
            print(f"Dispositivo encontrado: {d.name} ({d.address})")
            found = True
            break

    if not found:
        print("¡Advertencia! No se encontró el dispositivo en el escaneo.")

    try:
        async with BleakClient(address) as client:
            if not client.is_connected:
                print("No se pudo conectar al dispositivo.")
                return

            print("✅ Conectado al dispositivo.")
            services = client.services
            if not services:
                await client.get_services()
                services = client.services

            print("📋 Listando servicios y características:")
            for service in services:
                print(f"🔹 Servicio UUID: {service.uuid} — {service.description}")
                for char in service.characteristics:
                    if "notify" in char.properties and "write" not in char.properties and "write_without_response" not in char.properties:
                        desc = char.description or ""
                        props = ",".join(char.properties)
                        print(f"   ↪ Característica UUID: {char.uuid} — {desc} — propiedades: [{props}]")
            print("✅ Listado completo terminado.")
    except BleakError as e:
        print(f"❌ Ocurrió un error de conexión/listado: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    # Para listar los UUIDs del dispositivo:
    #asyncio.run(list_device_uuids(DEVICE_ADDRESS))
    try:
        asyncio.run(subscribe_and_log(DEVICE_ADDRESS, CHAR_UUID))
    except KeyboardInterrupt:
        print("\n🛑 Suscripción detenida por el usuario.")

if __name__ == "__main__":
    main()
