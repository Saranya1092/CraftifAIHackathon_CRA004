# ESP32 Firmware — SafeZone AI Warning Device (Optional)

> **Status**: This is an OPTIONAL integration. The core SafeZone AI application
> operates fully without this firmware. The hardware LEDs/buzzer provide a
> physical warning at the hazard location.

## Hardware Requirements

- ESP32 DevKit (any variant with WiFi)
- Red LED (GPIO 25, 330Ω resistor)
- Yellow LED (GPIO 26, 330Ω resistor)
- Passive buzzer (GPIO 27)
- USB cable for flashing

## FirmGen Workflow (Official CraftifAI Process)

```
1. Requirement  →  2. Firmware IR  →  3. Flash
```

### Stage 1 — Requirement

```
Subscribe to MQTT topic "safezone/incidents" on broker at ${MQTT_BROKER_IP}:1883.
On receiving a message with severity="high", activate the red LED and buzzer for 3 seconds.
On receiving a message with severity="medium", activate the yellow LED for 2 seconds.
Deduplicate events with the same event_id within 10 seconds.
Flash safely if WiFi or MQTT is unavailable on startup.
Print received event_id and timestamp over UART at 115200 baud.
```

### Stage 2 — Firmware IR

```bash
firmgen requirement \
  --text "Subscribe MQTT safezone/incidents. On high severity: red LED + buzzer 3s.
          On medium severity: yellow LED 2s. Dedup same event_id 10s window.
          Log event_id + timestamp to UART 115200." \
  --target esp32 \
  --output firmware_project/
```

### Stage 3 — Flash

```bash
firmgen build --project firmware_project/ --target esp32
firmgen flash --project firmware_project/ --port COM3  # Windows
firmgen flash --project firmware_project/ --port /dev/ttyUSB0  # Linux
```

## Manual Implementation (if FirmGen unavailable)

The sketch below implements the same requirements without FirmGen.
Compile with PlatformIO or Arduino IDE (ESP32 board package required).

```cpp
// firmware/safezone_alert/src/main.cpp
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <map>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER = "192.168.1.100";
const int   MQTT_PORT = 1883;
const char* MQTT_TOPIC = "safezone/incidents";

const int LED_RED    = 25;
const int LED_YELLOW = 26;
const int BUZZER     = 27;

WiFiClient   wifiClient;
PubSubClient mqttClient(wifiClient);

std::map<String, unsigned long> seenEvents;  // event_id -> millis()
const unsigned long DEDUP_WINDOW_MS = 10000;

void activateAlert(int severity) {
  if (severity == 2) {  // high
    digitalWrite(LED_RED, HIGH);
    tone(BUZZER, 1000, 3000);
    delay(3000);
    digitalWrite(LED_RED, LOW);
  } else if (severity == 1) {  // medium
    digitalWrite(LED_YELLOW, HIGH);
    delay(2000);
    digitalWrite(LED_YELLOW, LOW);
  }
}

void onMessage(char* topic, byte* payload, unsigned int length) {
  String body = String((char*)payload).substring(0, length);
  Serial.printf("[MQTT] %s\n", body.c_str());

  StaticJsonDocument<512> doc;
  if (deserializeJson(doc, body) != DeserializationError::Ok) return;

  String eventId  = doc["event_id"] | "unknown";
  String timestamp = doc["timestamp"] | "";
  const char* severity = doc["severity"] | "low";

  // Dedup
  unsigned long now = millis();
  auto it = seenEvents.find(eventId);
  if (it != seenEvents.end() && (now - it->second) < DEDUP_WINDOW_MS) {
    Serial.printf("[DEDUP] Skipping duplicate event %s\n", eventId.c_str());
    return;
  }
  seenEvents[eventId] = now;

  Serial.printf("[EVENT] id=%s time=%s severity=%s\n",
                eventId.c_str(), timestamp.c_str(), severity);

  int sevLevel = strcmp(severity, "high") == 0 ? 2 :
                 strcmp(severity, "medium") == 0 ? 1 : 0;
  activateAlert(sevLevel);
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("MQTT connecting...");
    if (mqttClient.connect("safezone-esp32")) {
      mqttClient.subscribe(MQTT_TOPIC);
      Serial.println("OK");
    } else {
      Serial.printf("FAILED rc=%d, retry in 5s\n", mqttClient.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("WiFi connecting");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts++ < 20) {
    delay(500); Serial.print(".");
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nWiFi failed – running offline");
    return;
  }
  Serial.printf("\nWiFi OK IP=%s\n", WiFi.localIP().toString().c_str());

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(onMessage);
  connectMQTT();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
    connectMQTT();
  }
  mqttClient.loop();

  // Cleanup old dedup entries
  unsigned long now = millis();
  for (auto it = seenEvents.begin(); it != seenEvents.end();) {
    if (now - it->second > DEDUP_WINDOW_MS) it = seenEvents.erase(it);
    else ++it;
  }
}
```

## Acceptance Criteria (Hardware Test)

To claim this feature operational:
1. Flash the firmware to an ESP32.
2. Inject a test incident via the backend or MQTT CLI:
   ```bash
   mosquitto_pub -t safezone/incidents -m '{"event_id":"test-1","severity":"high","timestamp":"2026-01-01T00:00:00Z"}'
   ```
3. Observe red LED + buzzer activate for 3 seconds.
4. Verify UART output shows the event_id and timestamp.
5. Send the same event_id again – verify it is deduplicated.

## Dependency Notes

- `PubSubClient` library: knolleary/pubsubclient
- `ArduinoJson`: bblanchon/ArduinoJson
- FirmGen requires the CraftifAI FirmGen CLI installed in the same container as PipeGen.
