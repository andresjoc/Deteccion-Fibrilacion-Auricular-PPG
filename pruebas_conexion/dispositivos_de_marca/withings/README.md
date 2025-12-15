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
python app.py
```

La aplicación quedará disponible en:

```
http://localhost:5000
```

---

## 🧪 Cómo probar el flujo completo

### 1️⃣ Iniciar autenticación

Abre en tu navegador:

```
http://localhost:5000/
```

Serás redirigido a la página de login de Withings.

---

### 2️⃣ Aceptar permisos

Acepta los permisos solicitados por la aplicación:

```
user.info,user.metrics
```

Al finalizar, Withings redirigirá a:

```
http://localhost:5000/get_token?code=XXX&state=YYY
```

---

### 3️⃣ Obtener token y dispositivos

El endpoint `/get_token`:

- Intercambia el código por un access token
- Guarda el token en memoria
- Consulta los dispositivos del usuario

Ejemplo de respuesta:

```json
{
  "access_token": "ACCESS_TOKEN",
  "devices": { ... }
}
```

---

### 4️⃣ Obtener mediciones de salud

Endpoint:

```
GET /measure/get
```

Este endpoint utiliza la **Measure API (Getmeas)** de Withings.

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

Permite obtener:

- Peso
- Ritmo cardíaco
- SpO2
- Temperatura
- Composición corporal

Los valores deben interpretarse como:

```
valor_real = value × 10^unit
```

---

## ⚠️ Raw Data (uso avanzado)

Los endpoints:

- `/rawdata/activate`
- `/rawdata/get`

Requieren **permisos avanzados** aprobados por Withings.

Si no están habilitados, la API responderá:

```
403 Insufficient_scope
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
