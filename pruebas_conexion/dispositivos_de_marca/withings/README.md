# Integración con la API de Withings usando Flask

Este proyecto es un **ejemplo de backend en Flask** que muestra cómo integrar la **API de Withings** utilizando **OAuth 2.0**, obtener el consentimiento del usuario y acceder a datos de salud como dispositivos y mediciones.

La parte de **autenticación OAuth** está **basada en el repositorio oficial de Withings**:

> **Repositorio oficial:** > [https://github.com/withings-sas/api-oauth2-python](https://github.com/withings-sas/api-oauth2-python)

---

## 📌 Funcionalidades

- Autenticación OAuth 2.0 con Withings
- Flujo completo de consentimiento del usuario
- Obtención y uso del access token
- Consulta de dispositivos del usuario
- Consulta de métricas de salud (Measure API)
- Endpoints opcionales para Raw Data (requieren permisos avanzados)

---

## 🧠 ¿Cómo funciona?

1. El usuario accede a `/`
2. La app redirige al login de Withings
3. El usuario acepta los permisos
4. Withings redirige a `/get_token`
5. Se intercambia el código de autorización por un access token
6. El access token se usa para llamar a la API de Withings

---

## ⚙️ Requisitos

- Python 3.8 o superior
- Una cuenta de desarrollador en Withings
- pip
- virtualenv

---

## 🧪 Crear y activar el entorno virtual (venv)

Antes de instalar dependencias o ejecutar la aplicación, se recomienda crear un **entorno virtual** para aislar el proyecto.

Desde la raíz del proyecto, ejecuta:

```bash
virtualenv venv
```

Activa el entorno virtual:

- **Linux / macOS**

```bash
source venv/bin/activate
```

- **Windows (PowerShell)**

```powershell
venv\Scripts\activate
```

Una vez activado, el prompt mostrará algo como:

```
(venv)
```

---

## 📦 Instalar el proyecto y dependencias

Con el entorno virtual activo, instala el proyecto en modo editable:

```bash
pip install -e .
```

Esto permite:

- Usar el código como paquete Python
- Que los cambios se reflejen sin reinstalar

---

## 🔧 Configuración del proyecto

Antes de ejecutar la aplicación, debes configurar tus credenciales de Withings.

---

### 1️⃣ Copiar el archivo de configuración

Crea tu archivo de configuración local a partir del ejemplo:

```bash
cp project.conf.example project.conf
```

---

### 2️⃣ Editar el archivo de configuración

Abre el archivo `project.conf` y agrega tus credenciales:

```bash
vim project.conf
```

Debes modificar **únicamente**:

- `client_id`
- `customer_secret`

Estos valores se obtienen al crear tu aplicación en el **Withings Developer Dashboard**.

La variable `state` puede dejarse igual o cambiarse por cualquier texto.

Los demás valores deben permanecer sin cambios.

Ejemplo:

```ini
[withings_api_example]
client_id = TU_CLIENT_ID
customer_secret = TU_CLIENT_SECRET
state = cualquier_string
account_withings_url = https://account.withings.com
wbsapi_withings_url = https://wbsapi.withings.net
callback_uri = http://localhost:5000/get_token
```

⚠️ El valor de `callback_uri` debe coincidir exactamente con el configurado en el panel de desarrolladores de Withings.

---

## ▶️ Ejecutar la aplicación

Con el entorno virtual activo, inicia el servidor Flask:

```bash
python .\scripts\app.py
```

La aplicación quedará disponible en:

```
http://localhost:5000
```

---

## 🧪 Cómo probar el flujo completo

Debes haber iniciado sesión en **Withings** y tener registrado un **smartwatch Withings** (por ejemplo ScanWatch) para utilizar la API.

---

## 1️⃣ Iniciar autenticación OAuth

Abre en tu navegador:

```
http://localhost:5000/
```

Este endpoint inicia el flujo **OAuth 2.0** y te redirige automáticamente a la página de login de Withings.

---

### 2️⃣ Aceptar permisos

Acepta los permisos solicitados por la aplicación. En este código, los scopes configurados son:

```
user.info,user.metrics
```
> ⚠️ Para **Raw Data** se requieren permisos avanzados adicionales aprobados por Withings (Advanced Research API).

Al finalizar, Withings redirigirá automáticamente a:

```
http://localhost:5000/get_token?code=XXX&state=YYY
```

---

### 3️⃣ Obtener token y dispositivos

El endpoint `/get_token`:

- Intercambia el `code` OAuth por un **access token**
- Guarda el token en memoria (session simple)
- Consulta los dispositivos asociados al usuario usando **User v2 - Get**
- Devuelve el token y la información de los dispositivos

Ejemplo de respuesta:

```json
{
  "access_token": "ACCESTOKEN",
  "devices": {
    "status": 0,
    "body": {
      "devices": [
        {
          "battery": "",
          "deviceid": "",
          "first_session_date": 0,
          "hash_deviceid": "",
          "last_session_date": 0,
          "model": "",
          "model_id": 0,
          "timezone": "",
          "type": ""
        }
      ]
    }
  }
}
```
| 📌 Importante

- El campo hash_deviceid es el identificador público del dispositivo

- Este valor es obligatorio para usar la API de Raw Data

- Guárdalo junto con el access_token

---

### 4️⃣ Obtener mediciones de salud

Endpoint:

```
GET /measure/get
```

Este endpoint utiliza la Measure API – Getmeas de Withings y no requiere permisos avanzados.

Ejemplo de respuesta:

```json
{
  "status": 0,
  "body": {
    "measuregrps": [],
    "more": 0
  }
}
```

---

## 📊 Measure API

Permite obtener mediciones de salud ya procesadas, como:

- Peso
- Ritmo cardíaco
- SpO2
- Temperatura
- Composición corporal

---

## ⚠️ Raw Data (uso avanzado)

Los endpoints:

- `/rawdata/activate`
- `/rawdata/get`

Requieren **permisos avanzados** aprobados por Withings.

Si no están habilitados, la API responderá:

```
Insufficient_scope: The request requires higher privileges than provided by the access token
```

### 5️⃣ Activar captura de Raw Data (PPG)

Para activar la captura de datos crudos, debes usar el access_token y el hash_deviceid obtenidos en el paso 3️⃣.

Ejemplo de URL:

```
http://localhost:5000/rawdata/activate?access_token=ACCESSTOKEN&hash_deviceid=HASH
```

Respuesta esperada:

```json
{
  "status": 0,
  "body": {}
}

```

### 6️⃣ Obtener Raw Data capturada

Una vez que el reloj haya sincronizado y haya datos disponibles, puedes obtener los datos crudos usando:

```
http://localhost:5000/rawdata/get?access_token=ACCESSTOKEN&hash_deviceid=HASH
```

Respuesta esperada:

```json
{
  "status": 0,
  "body": {}
}

```

---

## 🧩 Manejo de sesión

- El access token se almacena en memoria
- Se pierde al reiniciar la app
- No hay soporte multiusuario

---

## 🚨 Advertencia

- No maneja refresh tokens
- No persiste datos

---

## 📚 Referencias

- Documentación oficial
  [https://developer.withings.com](https://developer.withings.com)

- Ejemplo OAuth2 oficial
  [https://github.com/withings-sas/api-oauth2-python](https://github.com/withings-sas/api-oauth2-python)
