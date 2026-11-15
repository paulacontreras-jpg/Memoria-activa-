/*
  Memoria Activa - ESP32 en Wokwi
  Juego de memoria de secuencias (tipo "Simon dice") controlado por MQTT.
  Mide el tiempo de reaccion del jugador y puede adaptar la velocidad.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.mqttdashboard.com";

// Tópicos
const char* TOPIC_COMANDO = "pau/memoria/comando";   // Streamlit -> ESP32
const char* TOPIC_MENSAJE = "pau/memoria/mensaje";   // Streamlit -> ESP32
const char* TOPIC_ESTADO  = "pau/memoria/estado";    // ESP32 -> Streamlit

// Pines
const int PIN_LED_ESTADO = 2;
const int PIN_BUZZER = 18;
const int PIN_LEDS[4]    = {4, 16, 17, 19};   // rojo, verde, azul, amarillo
const int PIN_BOTONES[4] = {25, 26, 27, 33};
const int TONOS[4] = {262, 330, 392, 523};

LiquidCrystal_I2C lcd(0x27, 16, 2);
WiFiClient espClient;
PubSubClient client(espClient);

// ---------- Juego ----------
const int MAX_NIVEL = 30;
const unsigned long TIEMPO_ESPERA = 15000;   // tiempo máximo para pulsar un botón

// Umbrales del modo automático (tiempo medio por pulsación en cada nivel)
const unsigned long RAPIDO_MS = 1200;   // si responde más rápido, el juego se acelera
const unsigned long LENTO_MS  = 2500;   // si responde más lento, el juego se hace más lento

int secuencia[MAX_NIVEL];
int nivel = 0;
int indiceEntrada = 0;
int puntaje = 0;
int velocidad = 500;          // milisegundos que dura cada color
int multiplicador = 2;        // puntos por nivel según dificultad
const char* nombreDificultad = "normal";
bool modoAuto = false;

// Tiempos de reacción
unsigned long sumaNivel = 0;
int cuentaNivel = 0;
unsigned long sumaJuego = 0;
int cuentaJuego = 0;

enum Estado { ESPERA, TU_TURNO };
Estado estado = ESPERA;
unsigned long inicioTurno = 0;

// ---------- Mensajes y pantalla ----------
String comandoPendiente = "";
String mensajePendiente = "";
bool mensajeActivo = false;
unsigned long mensajeHasta = 0;
unsigned long ultimoScroll = 0;
String textoMensaje = "";
int posScroll = 0;
String ultimaL1 = "";
String ultimaL2 = "";

void pantalla(const String& l1, const String& l2) {
  mensajeActivo = false;
  ultimaL1 = l1;
  ultimaL2 = l2;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(l1.substring(0, 16));
  lcd.setCursor(0, 1);
  lcd.print(l2.substring(0, 16));
}

void tono(int frecuencia, int ms) {
  unsigned long medio = 500000UL / frecuencia;
  unsigned long fin = millis() + ms;
  while (millis() < fin) {
    digitalWrite(PIN_BUZZER, HIGH);
    delayMicroseconds(medio);
    digitalWrite(PIN_BUZZER, LOW);
    delayMicroseconds(medio);
  }
}

void destello(int i, int ms) {
  digitalWrite(PIN_LEDS[i], HIGH);
  tono(TONOS[i], ms);
  digitalWrite(PIN_LEDS[i], LOW);
}

void publicarEstado(const char* nombre) {
  char buf[200];
  int tiempoMedio = (cuentaJuego > 0) ? (int)(sumaJuego / cuentaJuego) : 0;
  snprintf(buf, sizeof(buf),
           "{\"estado\":\"%s\",\"nivel\":%d,\"puntaje\":%d,\"dificultad\":\"%s\",\"tiempo\":%d,\"velocidad\":%d}",
           nombre, nivel, puntaje, nombreDificultad, tiempoMedio, velocidad);
  client.publish(TOPIC_ESTADO, buf, true);   // retenido: quien se conecte después ve el último estado
}

void mostrarSecuencia() {
  estado = ESPERA;   // mientras se muestra, no se leen botones
  sumaNivel = 0;
  cuentaNivel = 0;
  pantalla("Nivel " + String(nivel), "Mira bien...");
  publicarEstado("mostrando");
  delay(700);
  for (int i = 0; i < nivel; i++) {
    destello(secuencia[i], velocidad);
    delay(velocidad / 3);
    client.loop();
  }
  pantalla("Nivel " + String(nivel), "Tu turno");
  publicarEstado("tu_turno");
  indiceEntrada = 0;
  inicioTurno = millis();
  estado = TU_TURNO;
}

void iniciarJuego() {
  nivel = 1;
  puntaje = 0;
  sumaJuego = 0;
  cuentaJuego = 0;
  if (modoAuto) velocidad = 600;   // el modo automático siempre arranca a un ritmo medio
  secuencia[0] = random(4);
  mostrarSecuencia();
}

// En modo automático, ajusta la velocidad según lo rápido que respondió en el nivel
void ajustarVelocidad() {
  if (!modoAuto || cuentaNivel == 0) return;
  unsigned long promedio = sumaNivel / cuentaNivel;
  if (promedio < RAPIDO_MS) {
    velocidad = max(250, velocidad - 80);
  } else if (promedio > LENTO_MS) {
    velocidad = min(900, velocidad + 80);
  }
}

void registrarReaccion(unsigned long ms) {
  sumaNivel += ms;
  cuentaNivel++;
  sumaJuego += ms;
  cuentaJuego++;
}

void acierto() {
  estado = ESPERA;
  puntaje += 10 * multiplicador;
  ajustarVelocidad();
  pantalla("Muy bien!", "Puntaje: " + String(puntaje));
  tono(660, 120);
  delay(60);
  tono(880, 180);
  delay(900);

  if (nivel >= MAX_NIVEL) {
    pantalla("Increible!", "Completaste todo");
    publicarEstado("gano");
    return;
  }
  secuencia[nivel] = random(4);
  nivel++;
  mostrarSecuencia();
}

void perdio() {
  estado = ESPERA;
  for (int i = 0; i < 4; i++) digitalWrite(PIN_LEDS[i], HIGH);
  tono(200, 400);
  tono(150, 500);
  for (int i = 0; i < 4; i++) digitalWrite(PIN_LEDS[i], LOW);

  pantalla("Casi lo logras!", "Puntaje: " + String(puntaje));
  publicarEstado("perdio");
  delay(3000);
  pantalla("Puntaje: " + String(puntaje), "Pulsa un boton");
}

// Termina la partida desde la app y guarda el puntaje actual
void terminarManual() {
  estado = ESPERA;
  pantalla("Partida terminada", "Puntaje: " + String(puntaje));
  tono(523, 150);
  delay(60);
  tono(392, 250);
  publicarEstado("termino");
  delay(2000);
  pantalla("Puntaje: " + String(puntaje), "Pulsa un boton");
}

// ---------- Botones ----------
int leerBoton() {
  for (int i = 0; i < 4; i++) {
    if (digitalRead(PIN_BOTONES[i]) == LOW) {
      delay(30);
      return i;
    }
  }
  return -1;
}

void esperarSoltar(int i) {
  while (digitalRead(PIN_BOTONES[i]) == LOW) {
    client.loop();
    delay(10);
  }
  delay(30);
}

// ---------- MQTT ----------
void procesarComando(String c) {
  c.toLowerCase();
  if (c.startsWith("dificultad:")) {
    String d = c.substring(11);
    if (d == "lenta")       { velocidad = 800; multiplicador = 1; nombreDificultad = "lenta";  modoAuto = false; }
    else if (d == "normal") { velocidad = 500; multiplicador = 2; nombreDificultad = "normal"; modoAuto = false; }
    else if (d == "rapida") { velocidad = 300; multiplicador = 3; nombreDificultad = "rapida"; modoAuto = false; }
    else if (d == "auto")   { velocidad = 600; multiplicador = 2; nombreDificultad = "auto";   modoAuto = true; }
    else return;
    if (estado == ESPERA) {
      pantalla("Dificultad:", d);
      publicarEstado("espera");
    }
  } else if (c == "iniciar" || c == "reiniciar") {
    iniciarJuego();
  } else if (c == "terminar") {
    if (estado == TU_TURNO) terminarManual();
  }
}

void mostrarMensaje(const String& m) {
  textoMensaje = m;
  posScroll = 0;
  mensajeActivo = true;
  mensajeHasta = millis() + 10000;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Mensaje:");
  lcd.setCursor(0, 1);
  lcd.print(m.substring(0, 16));
  tono(880, 120);
  delay(80);
  tono(880, 120);
}

void actualizarMensaje() {
  if (!mensajeActivo) return;
  if (millis() > mensajeHasta) {
    mensajeActivo = false;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(ultimaL1.substring(0, 16));
    lcd.setCursor(0, 1);
    lcd.print(ultimaL2.substring(0, 16));
    return;
  }
  if (textoMensaje.length() > 16 && millis() - ultimoScroll > 400) {
    ultimoScroll = millis();
    String v = textoMensaje + "   ";
    String vista = (v + v).substring(posScroll, posScroll + 16);
    lcd.setCursor(0, 1);
    lcd.print(vista);
    posScroll = (posScroll + 1) % v.length();
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  msg.trim();
  Serial.print(topic);
  Serial.print(" -> ");
  Serial.println(msg);

  // Solo se guarda: se procesa en loop() para no bloquear la red
  if (String(topic) == TOPIC_COMANDO) comandoPendiente = msg;
  else if (String(topic) == TOPIC_MENSAJE) mensajePendiente = msg;
}

void setup_wifi() {
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
}

void reconnect() {
  while (!client.connected()) {
    digitalWrite(PIN_LED_ESTADO, LOW);
    pantalla("Conectando MQTT", "...");
    String clientId = "MemoriaActiva-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("MQTT conectado");
      client.subscribe(TOPIC_COMANDO);
      client.subscribe(TOPIC_MENSAJE);
      digitalWrite(PIN_LED_ESTADO, HIGH);
      pantalla("Memoria Activa", "Pulsa un boton");
      publicarEstado("espera");
    } else {
      Serial.print("falla, rc=");
      Serial.println(client.state());
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED_ESTADO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  for (int i = 0; i < 4; i++) {
    pinMode(PIN_LEDS[i], OUTPUT);
    pinMode(PIN_BOTONES[i], INPUT_PULLUP);
  }
  randomSeed(micros() + analogRead(34));

  lcd.init();
  lcd.backlight();
  pantalla("Memoria Activa", "Iniciando...");

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  actualizarMensaje();

  if (comandoPendiente != "") {
    String c = comandoPendiente;
    comandoPendiente = "";
    procesarComando(c);
  }
  if (mensajePendiente != "") {
    String m = mensajePendiente;
    mensajePendiente = "";
    mostrarMensaje(m);
  }

  int b = leerBoton();

  if (estado == ESPERA) {
    // Pulsar cualquier botón también inicia una partida
    if (b >= 0) {
      esperarSoltar(b);
      iniciarJuego();
    }
  } else if (estado == TU_TURNO) {
    if (b >= 0) {
      unsigned long reaccion = millis() - inicioTurno;   // tiempo desde que pudo responder
      registrarReaccion(reaccion);                       // cuenta aciertos y errores
      Serial.print("Reaccion (ms): ");
      Serial.println(reaccion);
      destello(b, 250);
      esperarSoltar(b);
      if (b == secuencia[indiceEntrada]) {
        indiceEntrada++;
        inicioTurno = millis();
        if (indiceEntrada == nivel) acierto();
      } else {
        perdio();
      }
    } else if (millis() - inicioTurno > TIEMPO_ESPERA) {
      perdio();
    }
  }
}
