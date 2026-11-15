// Aviso claro de "ya puedes pulsar": tres notas que suben y las cuatro luces
void senalTuTurno() {
  for (int i = 0; i < 4; i++) digitalWrite(PIN_LEDS[i], HIGH);
  tono(523, 90);
  delay(30);
  tono(659, 90);
  delay(30);
  tono(784, 180);
  for (int i = 0; i < 4; i++) digitalWrite(PIN_LEDS[i], LOW);

  // Si alguien dejó un botón pulsado durante la secuencia, esperar a que lo suelte
  for (int i = 0; i < 4; i++) {
    while (digitalRead(PIN_BOTONES[i]) == LOW) {
      client.loop();
      delay(10);
    }
  }
}
