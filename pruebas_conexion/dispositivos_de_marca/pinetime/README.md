# Captura de Señales PPG desde PineTime (Firmware Modificado)

Este repositorio contiene un script en Python para capturar datos PPG crudos (raw) desde un smartwatch PineTime, utilizando un firmware modificado de InfiniTime que habilita la lectura directa del buffer PPG vía BLE.

El propósito es obtener datos PPG a 10 Hz sin filtrado, junto con metadatos de adquisición, para experimentación o análisis biométrico.

---

## 🚀 Requisitos Previos

### 1. Actualizar el Firmware del PineTime

Es obligatorio actualizar el reloj al fork modificado de InfiniTime:

🔗 **Firmware modificado:**  
https://github.com/andresjoc/InfiniTime.git

Debes flashear el siguiente archivo precompilado:

📦 **pinetime-mcuboot-app-dfu-1.15.0.zip**

Este firmware habilita:

- Lectura BLE continua del buffer PPG.
- Frecuencia de muestreo a 10 Hz.
- Sin filtrado ni postprocesamiento.

---

## 🧩 Instalación del Entorno

### 2. Crear entorno virtual

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ⌚ Configuración del PineTime

Antes de ejecutar el script:

- En el PineTime, abre la app de monitor cardiaco.
- Activa la medición de ritmo cardíaco.
- Deja la pantalla activa o el proceso de HRM en segundo plano (según tu firmware modificado).

El reloj comenzará a generar datos PPG que el script capturará como lecturas RAW desde BLE.

---

## ▶️ Ejecución del Script

Ejecuta el script principal:

```bash
python capture_ppg.py
```

Esto hará lo siguiente:

- Conectarse vía BLE a la dirección MAC configurada (`address = "c4:ce:dc:06:4d:89"`).
- Leer paquetes de 64 samples (`<64H>`) desde el UUID **2A39**.
- Eliminar duplicados mediante un algoritmo de superposición.
- Guardar los nuevos samples en un archivo CSV con timestamp.
- Crear un archivo `metadata.json` con parámetros de adquisición.

---

## 📁 Archivos Generados

Al iniciar la captura se crean:

### 1. `TIMESTAMP_ppg_10hz.csv`

**Estructura:**

```
timestamp,ppg_value
1711485091.12,1234
1711485091.12,1201
...
```

Cada línea corresponde a un sample del PPG crudo.

### 2. `TIMESTAMP_metadata.json`

**Ejemplo:**

```json
{
  "infinitime_version": 1.14,
  "led_current_mA": 12,
  "delay_ms": 50,
  "description": "raw ppg capture (no filtering)"
}
```

---

## 🧠 Descripción del Código

### Captura BLE

El script usa `BleakClient` para leer continuamente la characteristic **2A39**, que contiene buffers de 64 muestras PPG sin procesar:

```python
raw_data = await client.read_gatt_char(MODEL_NBR_UUID)
int_array = np.array(list(struct.unpack('<64H', raw_data)))
```

### Eliminación de datos duplicados

Se aplica un algoritmo de correlación entre paquetes consecutivos para:

- Detectar superposición
- Extraer solo nuevos valores

Funciones principales:

- `most_overlap_index()`
- `diff_subset_range()`
- `add_new_data()`

### Guardado de datos

Las nuevas muestras se guardan de inmediato:

```python
csv_file.write(f"{now},{v}\n")
```

---

## ⚠️ Consideraciones Importantes

- La dirección MAC del reloj debe ajustarse manualmente en el código.
- La medición HR debe estar activa, de lo contrario no se emitirán muestras PPG.
- La captura BLE depende de la estabilidad de conexión del host.
- El script está configurado para una frecuencia aproximada de 10 Hz, pero depende del firmware.
