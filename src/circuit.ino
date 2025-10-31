/*
    Este código controla un servo para abrir una puerta y un buzzer para emitir sonidos
    basados en comandos recibidos desde la PC a través del monitor serial.

    Comandos:
    - "abrir_puerta": Abre la puerta (gira el servo) y emite un sonido de confirmación (buzzer)
    - "acceso_denegado": Emite un sonido de error (buzzer)

    Tinkercad: https://www.tinkercad.com/things/2drDvAwTX2o-accionador-puerta/editel?returnTo=https%3A%2F%2Fwww.tinkercad.com%2Fdashboard%2Fdesigns%2Fcircuits&sharecode=hQqR65OFa_NWfJIdk4SUahVpY9dT9atpLgDn1JAIyWw
*/




#include <Servo.h>

Servo servo;
const int pinServo = 2;
const int pinBuzzer = 3;

String comando = "";

void setup() {
  Serial.begin(9600);
  servo.attach(pinServo);
  pinMode(pinBuzzer, OUTPUT);
  servo.write(0);  // Posición inicial
}

void loop() {
  // Si hay datos disponibles desde la PC
  if (Serial.available() > 0) {
    comando = Serial.readStringUntil('\n');  // Leer hasta salto de línea
    comando.trim();

    if (comando == "abrir_puerta") {
      abrirPuerta();
    } 
    else if (comando == "acceso_denegado") {
      errorAcceso();
    }
  }
}

void abrirPuerta() {
  Serial.println("Abriendo puerta...");
  servo.write(90);  // Gira el servo (puedes ajustar el ángulo)
  sonar_buzzer(50);
  sonar_buzzer(50);
  sonar_buzzer(50);
  delay(3000);      // Espera 3 segundos
  servo.write(0);   // Regresa a posición inicial
  Serial.println("Puerta cerrada.");
  sonar_buzzer(1000);
}

void errorAcceso() {
  Serial.println("Acceso denegado!");
  for (int i = 0; i < 3; i++) { // Hace 3 pitidos
    sonar_buzzer(600);
  }
}

void sonar_buzzer(int tiempo){
  digitalWrite(pinBuzzer, HIGH);
  delay(tiempo);
  digitalWrite(pinBuzzer, LOW);
  delay(tiempo);
  
}
