# Prueba-UUID

Script para conectarse a un dispositivo BLE, suscribirse a una característica (UUID) que envía notificaciones y registrar las notificaciones en un CSV.

## Características
- Escanea y conecta a un dispositivo BLE por dirección MAC.
- Lista servicios y características notify disponibles (función `list_device_uuids`).
- Se suscribe a una característica específica (UUID) y guarda cada notificación en un archivo CSV (`datos_BLR.csv`).
- Formato CSV: `timestamp`, `sender`, `data` (los bytes se guardan como hex).

## Requisitos
- Python 3.8+ (se recomienda 3.9+)
- Paquetes Python:
  - bleak

Instala dependencias con pip:
```bash
pip install bleak
```

## Uso

1. Para listar servicios y características "notify" del dispositivo (útil para encontrar el UUID correcto), descomenta la línea correspondiente en `main()` o ejecuta:
```python
# En UUID.py, dentro de main:
# asyncio.run(list_device_uuids(DEVICE_ADDRESS))
```
Y ejecuta:
```bash
python UUID.py
```
La función `list_device_uuids` escaneará brevemente y, si puede conectarse, imprimirá servicios y características con la propiedad `notify`.

2. Para suscribirte y registrar notificaciones en CSV, ejecuta el script tal como está (la suscripción es la opción por defecto):
```bash
python UUID.py
```
Presiona Ctrl+C para detener la suscripción.

## Archivo de salida
- Nombre: `datos_BLR.csv` (se crea/reemplaza al iniciar la suscripción).
- Columnas: `timestamp`, `sender`, `data`
  - `timestamp`: ISO8601 con fecha y hora local (ej. `2025-10-23T19:45:45.123456`)
  - `sender`: identificador de la característica que envió la notificación
  - `data`: bytes de la notificación codificados como hex (por ejemplo `0a1b2c...`)

## Buenas prácticas
- Asegúrate de que ninguna otra aplicación esté conectada al dispositivo BLE cuando intentes conectar desde este script.
- Verifica el rango y la batería del dispositivo.
- Si necesitas leer/interpretar los bytes recibidos, adapta `notification_handler` para decodificarlos según el formato específico del dispositivo (por ejemplo little-endian int16, floats, strings, etc.).

## Ejemplo de modificación rápida
Si esperas texto UTF-8 en lugar de hex, puedes cambiar en `UUID.py` la línea:
```python
decoded_data = data.hex()
```
por:
```python
decoded_data = data.decode('utf-8', errors='replace')
```
