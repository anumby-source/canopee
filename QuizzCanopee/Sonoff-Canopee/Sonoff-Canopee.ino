/*
  actionneur Canopee pour Sonoff
  on s'abonne au topic mqtt Canopee/etat message Bon  ou  Nul

  Version 0.01 : Creation.
          0.02 : Gestion de la led : allumée apres le Wifi- clignotte 2 fois à la fi du setup.
                 Gestion du button poussoir : ouvre le relais.

*/
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>

#define timeDelayOn  2000
#define timeDelayOff 500

//parametre Wifi
#define ssid      "Anumby-Canopee"                  // Nom du reseau WIFI utilise
#define password  "AnumbyPwd"                       // Mot de passe du reseau WIFI utilise
#define mqtt_server "192.168.1.100"


const char *mqttTopic = "canopee/etat";
const char *mqttTrace = "trace/can";                  // topic pour les traces

// Sonoff pins
const int led       = 13;                             // LOW  = Allumée;  HIGH = eteinte
const int pinRelais = 12;                             // HIGH = Fermé;    LOW  = ouvert
const int bouton    =  0;                             // pin du bouton poussoir

// Buffer pour décoder les messages MQTT reçus
char message_buff[100];

WiFiClient espClient;
PubSubClient client(espClient);

// Nom externe OTA
char extID[30];                                     // Nom externa OTA, mqtt, ..."Canope-(mac address)"
String macAdresse = "";

//  "5C:CF:7F:E7:05:4B"   sonoff bon (julio)
//  "5C:CF:7F:AF:93:1E"              (julio)


//
//  "5C:CF:7F:AF:9C:B2"   sonoff Nul (julio)
//  "C4:4F:33:B3:83:6F"   R3         (julio)

//-------------------------------------------------------------------------------------------------

int nbtent = 0;                 // nombre de tentatives de conexion wifi

bool debug = true;

void setup_wifi() {
  // We start by connecting to a WiFi network
  if (debug) {
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
  }
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    if (nbtent < 20) {
      nbtent++ ;
      delay(1000);
      Serial.print(".");
    }
    else {
      Serial.println("Reset");
      ESP.restart();
    }
  }
}


void setup(void) {
  Serial.begin(115200);

  pinMode (pinRelais, OUTPUT);
  digitalWrite (pinRelais, LOW);          // relais ouvert

  pinMode (led, OUTPUT);
  digitalWrite (led, HIGH);               // led  eteinte

  // Connexion au WiFi
  setup_wifi();

  // on allume la led apres la cconnexion wifi:
  digitalWrite (led, LOW);                // led alumée


  if (debug) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }

  client.setServer(mqtt_server, 1883);    // Configuration de la connexion au serveur MQTT
  client.setCallback(callback);           // La fonction de callback qui est executée à chaque réception de message

  macAdresse = WiFi.macAddress();
  Serial.println(macAdresse);

  if (!client.connected())
    reconnectMQTT();

  String exName = String ("Canopee-") + macAdresse;
  exName.toCharArray(extID, exName.length() + 1);

  // Hostname defaults
  ArduinoOTA.setHostname(extID);

  // Authentication by default
  ArduinoOTA.setPassword("11223344");     // un peu de sécurité :-)

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH)
      type = "sketch";
    else // U_SPIFFS
      type = "filesystem";

    Serial.println("Update ...");
    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
    //Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("Reboot ...");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {

  });
  ArduinoOTA.onError([](ota_error_t error) {

  });
  ArduinoOTA.begin();

  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());


  // message de connection :
  String Message = macAdresse + String (" Sonoff connecte -  Version 0.02");

  Message.toCharArray(message_buff, Message.length() + 1);
  client.publish(mqttTopic, message_buff);
  delay (100);

  // on signale la fin du setup:
  for (int i = 0; i < 2; i++) {
    digitalWrite (led, HIGH);               // led  eteinte
    delay (300);
    digitalWrite (led, LOW);               // led  allumée
    delay (300);
  }
}

//Reconnexion MQTT
void reconnectMQTT() {

  char monClient[30];
  macAdresse.toCharArray(monClient, macAdresse.length() + 1);

  if (WiFi.status() != WL_CONNECTED)
    setup_wifi();

  //Boucle jusqu'à obtenur une reconnexion
  while (!client.connected()) {
    Serial.print("Connexion au serveur MQTT...");
    if (client.connect(monClient)) {
      client.subscribe(mqttTopic);
      Serial.println("OK");
    } else {
      Serial.print("KO, erreur : ");
      Serial.print(client.state());
      Serial.println(" On attend 1 seconde avant de recommencer");
      delay(1000);
    }
  }
}

// Déclenche les actions à la réception d'un message
void callback(char* topic, byte* payload, unsigned int length) {
  int i = 0;

  if ( debug ) {
    //Serial.println("Message recu");
  }

  // create character buffer with ending null terminator (string)
  for (i = 0; i < length; i++) {
    message_buff[i] = payload[i];
  }
  message_buff[i] = '\0';

  String msgString = String(message_buff);

  if ( debug ) {
    Serial.println("Message: " + msgString);
  }

  gestionActionneur (macAdresse, msgString) ;

}


void gestionActionneur (String actionneur, String niveau) {

  if (actionneur == "5C:CF:7F:E7:05:4B" ||
      actionneur == "5C:CF:7F:AF:93:1E") {
    Serial.println("Actionneur bon");
    if (niveau == String ("Bon"))
      digitalWrite (pinRelais, HIGH);          // relais fermé
    //clignote(pinRelais);
    else
      digitalWrite (pinRelais, LOW);          // relais ouvert

  }
  if (actionneur == "5C:CF:7F:AF:9C:B2" ||
      actionneur == "C4:4F:33:B3:83:6F"  ) {
    Serial.println("Actionneur Nul");
    if (niveau == String ("Nul"))
      digitalWrite (pinRelais, HIGH);          // relais fermé
    //clignote(pinRelais);
    else
      digitalWrite (pinRelais, LOW);          // relais ouvert
  }

}

void clignote(int pin) {

  for (int i = 0; i < 10; i++) {
    digitalWrite (pin, HIGH);
    delay (timeDelayOn);
    digitalWrite (pin, LOW);
    delay (timeDelayOff);
  }
  Serial.println ("je clignote");
}

void loop(void) {

  // Surveillance des demandes de mise à jour en OTA
  ArduinoOTA.handle();

  // gestion du bouton poussoir sur le Sonoff
  if (digitalRead(bouton) == LOW) {
    Serial.println ("Bouton poussoir presse");
    digitalWrite (pinRelais, LOW);          // relais ouvert
    delay (1000);
  }

  if (!client.connected())
  {
    reconnectMQTT();
  }

  client.loop();

  delay (100);

}
