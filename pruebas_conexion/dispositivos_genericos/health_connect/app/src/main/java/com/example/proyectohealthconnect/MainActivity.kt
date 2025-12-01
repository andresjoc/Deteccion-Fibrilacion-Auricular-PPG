package com.example.proyectohealthconnect

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.proyectohealthconnect.ui.theme.ProyectoHealthConnectTheme
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.ZoneId
import java.time.temporal.ChronoUnit

class MainActivity : ComponentActivity() {

    private lateinit var requestPermissions: ActivityResultLauncher<Set<String>>
    private lateinit var healthConnectClient: HealthConnectClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // 1) Cliente de Health Connect
        healthConnectClient = HealthConnectClient.getOrCreate(this)

        // 2) Permisos mínimos: SOLO lectura de Heart Rate
        val permissions = setOf(
            HealthPermission.getReadPermission(HeartRateRecord::class)
        )

        // 3) Launcher para solicitar permisos
        requestPermissions = registerForActivityResult(
            PermissionController.createRequestPermissionResultContract()
        ) { grantedPermissions ->
            if (grantedPermissions.containsAll(permissions)) {
                println("✅ Permisos concedidos")
            } else {
                println("❌ Permisos denegados")
            }
        }

        // 4) UI
        setContent {
            ProyectoHealthConnectTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    MainScreen(
                        modifier = Modifier.padding(innerPadding),
                        onRequestPermissions = { requestPermissions.launch(permissions) }
                    )
                }
            }
        }
    }
}

@Composable
fun MainScreen(
    modifier: Modifier = Modifier,
    onRequestPermissions: () -> Unit
) {
    val scope = rememberCoroutineScope()
    var status by remember { mutableStateOf("Presiona el botón para pedir permisos") }
    val context = LocalContext.current

    // Lanzador SAF: "Guardar como..." para crear el CSV
    val createCsvLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("text/csv")
    ) { uri ->
        if (uri != null) {
            scope.launch {
                try {
                    val csv = buildHeartRateCsv(context)
                    context.contentResolver.openOutputStream(uri)?.use { out ->
                        out.write(csv.toByteArray())
                        out.flush()
                    }
                    status = "✅ CSV exportado correctamente."
                } catch (e: Exception) {
                    status = "❌ Error al exportar: ${e.message}"
                }
            }
        } else {
            status = "Exportación cancelada."
        }
    }

    Column(modifier = modifier.padding(16.dp)) {
        Text(text = status)

        Button(onClick = {
            scope.launch {
                onRequestPermissions()
                status = "Si no aparece el diálogo, abre Health Connect y otorga permisos"
            }
        }) { Text("Conectar con Health Connect") }

        Spacer(Modifier.height(12.dp))

        Button(onClick = {
            // Intent oficial de ajustes de Health Connect
            val hcSettings = Intent("androidx.health.ACTION_HEALTH_CONNECT_SETTINGS")

            // Abrir la app de Health Connect directamente (si existe)
            val pkgIntent = context.packageManager
                .getLaunchIntentForPackage("com.google.android.apps.healthdata")

            // Último recurso: pantalla de información de la app en Ajustes
            val appDetails = Intent(
                Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                Uri.parse("package:com.google.android.apps.healthdata")
            )

            val chosen = listOf(hcSettings, pkgIntent, appDetails).firstOrNull {
                it != null && it.resolveActivity(context.packageManager) != null
            }

            if (chosen != null) {
                context.startActivity(chosen)
            } else {
                status = "No encontré la app de Health Connect en este dispositivo."
            }
        }) { Text("Abrir Health Connect") }

        Spacer(Modifier.height(12.dp))

        Button(onClick = {
            // Pide nombre/ubicación del archivo
            createCsvLauncher.launch("heart_rate_last_5_days.csv")
        }) { Text("Exportar Heart Rate (5 días) a CSV") }
    }
}

/**
 * Lee Heart Rate de los últimos 5 días y devuelve un CSV con:
 * timestamp (ISO-8601 local), bpm
 */
suspend fun buildHeartRateCsv(context: android.content.Context): String {
    val client = HealthConnectClient.getOrCreate(context)

    val end = Instant.now()
    val start = end.minus(5, ChronoUnit.DAYS)

    val response = client.readRecords(
        ReadRecordsRequest(
            recordType = HeartRateRecord::class,
            timeRangeFilter = TimeRangeFilter.between(start, end)
        )
    )

    val lines = mutableListOf("timestamp,bpm")

    // Aplana todas las muestras de cada registro de HR
    response.records.forEach { rec ->
        rec.samples.forEach { s ->
            val ts = s.time.atZone(ZoneId.systemDefault()).toString()
            lines += "$ts,${s.beatsPerMinute}"
        }
    }

    // Ordenar por timestamp (opcional)
    val header = lines.first()
    val bodySorted = lines.drop(1).sortedBy { it.substringBefore(',') }

    return buildString {
        appendLine(header)
        bodySorted.forEach { appendLine(it) }
    }
}

@Preview(showBackground = true)
@Composable
fun PreviewMainScreen() {
    ProyectoHealthConnectTheme {
        MainScreen(onRequestPermissions = {})
    }
}
