# Prueba - Health Connect

Pequeña aplicación de ejemplo (Kotlin / Jetpack Compose) que demuestra cómo conectarse a Health Connect, solicitar permisos de lectura de registros de frecuencia cardíaca (Heart Rate) y exportar las muestras a un CSV.

Este repositorio contiene una implementación simple en `MainActivity.kt` que:
- Crea un cliente de Health Connect.
- Solicita permisos de lectura para HeartRateRecord.
- Lee los registros de los últimos 5 días.
- Permite exportar las muestras en un CSV ("timestamp,bpm") mediante el diálogo "Guardar como..." del sistema.

Archivo principal: app/src/main/java/com/example/proyectohealthconnect/MainActivity.kt

Requisitos
- Android Studio (última versión recomendada).
- Dispositivo físico o emulador con Google Play Services y/o Health Connect instalado con datos registrados.
- SDK mínimo según la configuración del proyecto (revisar build.gradle del módulo `app`).

Cómo usar (rápido)
1. Clona el repositorio:
   git clone https://github.com/andresjoc/Prueba-Health-Connect.git

2. Abre el proyecto en Android Studio y sincroniza Gradle.

3. Ejecuta la app en un dispositivo o emulador donde esté disponible Health Connect.

4. En la interfaz:
   - "Conectar con Health Connect" -> abre el diálogo de permisos de Health Connect. Debes conceder permiso de lectura para la frecuencia cardíaca (Heart Rate).
   - "Abrir Health Connect" -> intenta abrir la app/configuración de Health Connect directamente en el dispositivo.
   - "Exportar Heart Rate (5 días) a CSV" -> abre el diálogo "Guardar como..." y crea el archivo CSV. El CSV contiene las columnas: timestamp (ISO-8601, zona local), bpm.

Formato del CSV
- Cabecera: timestamp,bpm
- Ejemplo de fila:
  2025-10-23T11:42:10-05:00[America/Bogota],72

Consejos y resolución de problemas
- Si al solicitar permisos no aparece el diálogo, abre la app Health Connect manualmente y verifica permisos para esta app.
- Asegúrate de que la cuenta y la configuración de Health Connect tengan datos de Heart Rate para el rango de tiempo solicitado.
- Si el CSV sale vacío, revisa que existan registros en los últimos 5 días; puedes cambiar el rango en el código para hacer pruebas.

````
