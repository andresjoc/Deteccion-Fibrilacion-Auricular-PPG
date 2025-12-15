# =========================
# IMPORTS
# =========================

# Flask:
# - Flask → crea la aplicación web
# - request → leer parámetros de la URL (query string)
# - redirect → redirigir el navegador a otra URL
from flask import Flask, request, redirect

# requests:
# Librería para hacer peticiones HTTP (GET, POST) a APIs externas
import requests

# config:
# Archivo de configuración donde tienes client_id, secret, urls, etc.
from withings_api_example import config

# time:
# Para trabajar con timestamps Unix (segundos desde 1970)
import time


# =========================
# APP FLASK
# =========================

# Crear la aplicación Flask
app = Flask(__name__)

# SESSION:
# Diccionario en memoria para guardar datos de la sesión actual.
# No es persistente, se pierde si se reinicia el servidor.
SESSION = {}


# =========================
# CONFIGURACIÓN WITHINGS
# =========================

# ID público de tu aplicación (OAuth)
CLIENT_ID = config.get("withings_api_example", "client_id")
CUSTOMER_SECRET = config.get("withings_api_example", "customer_secret")
STATE = config.get("withings_api_example", "state")
ACCOUNT_URL = config.get("withings_api_example", "account_withings_url")
WBSAPI_URL = config.get("withings_api_example", "wbsapi_withings_url")
CALLBACK_URI = config.get("withings_api_example", "callback_uri")


# =========================
# ENDPOINT /
# =========================

@app.route("/")
def get_code():
    """
    Inicia el flujo OAuth 2.0

    1. Construye una URL de autorización
    2. Redirige al usuario a Withings
    3. El usuario inicia sesión y acepta permisos
    """

    payload = {
        # OAuth exige este valor fijo
        "response_type": "code",

        # Identificador de tu app
        "client_id": CLIENT_ID,

        # State para seguridad
        "state": STATE,

        # Permisos solicitados (con coma, como exige Withings)
        "scope": "user.info,user.metrics",

        # URL a la que volverá Withings
        "redirect_uri": CALLBACK_URI,
    }

    # Construye la URL OAuth completa
    r_auth = requests.get(
        f"{ACCOUNT_URL}/oauth2_user/authorize2",
        params=payload
    )

    # Redirige el navegador a Withings
    return redirect(r_auth.url)


# =========================
# ENDPOINT /get_token
# =========================

@app.route("/get_token")
def get_token():
    """
    Callback OAuth

    Withings redirige aquí con:
    - code → código de autorización temporal
    - state → validación CSRF

    Aquí:
    1. Intercambiamos code → access_token
    2. Guardamos el token
    3. Consultamos dispositivos del usuario
    """

    # Leer parámetros enviados por Withings
    code = request.args.get("code")
    state = request.args.get("state")

    # Datos requeridos para pedir el access_token
    payload = {
        "action": "requesttoken",
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CUSTOMER_SECRET,
        "code": code,
        "redirect_uri": CALLBACK_URI,
    }

    # Petición POST a Withings para obtener el token
    r_token = requests.post(
        f"{WBSAPI_URL}/v2/oauth2",
        data=payload
    ).json()

    # Extraer access_token del response
    access_token = r_token["body"]["access_token"]

    # Guardar token en memoria
    SESSION["access_token"] = access_token
    SESSION["token_time"] = time.time()

    # =========================
    # Obtener dispositivos del usuario
    # =========================

    headers = {
        "Authorization": "Bearer " + access_token
    }

    payload = {
        "action": "getdevice"
    }

    r_getdevice = requests.get(
        f"{WBSAPI_URL}/v2/user",
        headers=headers,
        params=payload
    ).json()

    # Respuesta visible en el navegador
    return {
        "access_token": access_token,
        "devices": r_getdevice
    }


# =========================
# RAW DATA (requiere permisos avanzados)
# =========================

@app.route("/rawdata/activate")
def activate_rawdata():
    """
    Activa captura de datos crudos (PPG o acelerómetro)
    ⚠️ Requiere permisos avanzados
    """

    access_token = request.args.get("access_token")
    hash_deviceid = request.args.get("hash_deviceid")

    # Fecha de fin (1 hora desde ahora)
    enddate = int(time.time()) + 3600

    headers = {
        "Authorization": "Bearer " + access_token
    }

    payload = {
        "action": "activate",
        "hash_deviceid": hash_deviceid,
        "rawdata_type": 2,  # 2 = sensor óptico (PPG)
        "enddate": enddate
    }

    r = requests.post(
        f"{WBSAPI_URL}/v2/rawdata",
        headers=headers,
        data=payload
    )

    return r.json()


@app.route("/rawdata/get")
def get_rawdata():
    """
    Obtiene raw data previamente capturada
    """

    access_token = request.args.get("access_token")
    hash_deviceid = request.args.get("hash_deviceid")

    startdate = int(time.time()) - 3600
    enddate = int(time.time())

    headers = {
        "Authorization": "Bearer " + access_token
    }

    payload = {
        "action": "get",
        "hash_deviceid": hash_deviceid,
        "rawdata_type": 2,
        "startdate": startdate,
        "enddate": enddate
    }

    r = requests.get(
        f"{WBSAPI_URL}/v2/rawdata",
        headers=headers,
        params=payload
    )

    return r.json()


# =========================
# MEASURE API (sin permisos especiales)
# =========================

@app.route("/measure/get")
def get_measures():
    """
    Obtiene mediciones de salud procesadas
    (peso, pulso, SpO2, ECG, etc.)
    """

    # Leer token guardado
    access_token = SESSION.get("access_token")

    if not access_token:
        return {"error": "Not authenticated"}, 401

    headers = {
        "Authorization": "Bearer " + access_token
    }

    payload = {
        "action": "getmeas",

        # Tipo de medida: https://developer.withings.com/api-reference#tag/measure/operation/measure-getmeas
        # 139 = fibrilación auricular por PPG 
        "meastypes": "139",

        # 1 = medidas reales
        "category": 1,
    }

    r = requests.post(
        "https://wbsapi.withings.net/measure",
        headers=headers,
        data=payload
    )

    return r.json()
