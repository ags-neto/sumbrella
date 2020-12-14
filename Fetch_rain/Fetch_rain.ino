#include <ESP8266WiFi.h>
#include <Wire.h>  // This library is already built in to the Arduino IDE
#include <LiquidCrystal_I2C.h> //This library you can add via Include Library > Manage Library >  

#include "secrets.h"

LiquidCrystal_I2C lcd(0x27, 16, 2);


const char* ssid = WIFI_SSID; // defined in secrets.h (not versioned)
const char* password = WIFI_PASSWORD; // defined in secrets.h (not versioned)

const char* host = "api.thingspeak.com";

void setup() {
  Serial.begin(115200);
  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("");
  delay(500);
}


void loop() {

  int t = today();
  if (t != -1 ) {
    Serial.print("Today: ");
    Serial.println(t);
    delay(500);
  } else {
    Serial.println("Something went wrong, resetting...");
    setup();
  }

  int tm = tmrw();
  if (tm != -1 ) {
    Serial.print("Tomorrow: ");
    Serial.println(tm);
    delay(500);
  } else {
    Serial.println("Something went wrong, resetting...");
    setup();
  }

  int aft = aftmrw();
  if (aft != -1 ) {
    Serial.print("After tomorrow: ");
    Serial.println(aft);
    delay(500);
  } else {
    Serial.println("Something went wrong, resetting...");
    setup();
  }

  Serial.println("");
}

















int today() {


  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 80;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return -1;
  }

  // We now create a URI for the request
  String url = "/apps/thinghttp/send_request?api_key=" + String(THINGHTTP_KEY_TODAY);

  // This will send the request to the server
  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "Connection: close\r\n\r\n");
  delay(500);

  // Read all the lines of the reply from server and print them to Serial
  String line = client.readStringUntil('\r');
  for (int i = 0; i < 18; i++) {
    line = client.readStringUntil('\r');
  }
  line = client.readStringUntil('%');
  int rain = line.toInt();
  return rain;
}

int tmrw() {

  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 80;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return -1;
  }

  // We now create a URI for the request
  String url = "/apps/thinghttp/send_request?api_key=" + String(THINGHTTP_KEY_TMRW);
  // This will send the request to the server
  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "Connection: close\r\n\r\n");
  delay(500);

  // Read all the lines of the reply from server and print them to Serial
  String line = client.readStringUntil('\r');
  for (int i = 0; i < 18; i++) {
    line = client.readStringUntil('\r');
  }
  line = client.readStringUntil('%');

  int rain = line.toInt();
  return rain;
}

int aftmrw() {
  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 80;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return -1;
  }

  // We now create a URI for the request
  String url = "/apps/thinghttp/send_request?api_key=" + String(THINGHTTP_KEY_AFTMRW);
  // This will send the request to the server
  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "Connection: close\r\n\r\n");
  delay(500);

  // Read all the lines of the reply from server and print them to Serial
  String line = client.readStringUntil('\r');
  for (int i = 0; i < 18; i++) {
    line = client.readStringUntil('\r');
  }
  line = client.readStringUntil('%');

  int rain = line.toInt();
  return rain;
}
