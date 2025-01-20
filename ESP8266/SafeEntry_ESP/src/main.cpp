#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>

const char* ssid = "PiwnicaIT";
const char* password = "bW*5&72xz#kw";

const char* serverName = "http://stachurpi.local:5000/";

void setup() {
    Serial.begin(9600);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        while (true);
    }

    while (Serial.available() <= 0);

    String incoming = Serial.readStringUntil('\n');

    if (incoming[0] == '#') {
        return;
    }

    int separator = incoming.indexOf("|");
    if (separator == -1) {
        return;
    }

    String command = incoming.substring(0, separator);
    command.toLowerCase();
    if (!(command == "enter" || command == "exit")) {
        return;
    }

    String cardId = incoming.substring(separator + 1);
    cardId.trim();
    if (cardId == "") {
        return;
    }

    WiFiClient client;
    HTTPClient http;

    String connectionUrl = String(serverName) + command + "?card=" + cardId;

    http.begin(client, connectionUrl);

    http.addHeader("Content-Type", "text/plain");
    int httpResponseCode = http.GET();

    if (httpResponseCode != 200) {
        return;
    }

    Serial.println(http.getString());

    http.end();
}