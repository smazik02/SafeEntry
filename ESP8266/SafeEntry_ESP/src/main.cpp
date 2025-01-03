#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>

const char* ssid = "PiwnicaIT";
const char* password = "bW*5&72xz#kw";

const char* serverName = "http://stachurpi.local:5000/";

void setup() {
    Serial.begin(9600);

    WiFi.begin(ssid, password);
    Serial.println("#Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("#");
    Serial.println("#Connected to WiFi");
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("#WiFi Disconnected");
        while (true);
    }

    while (Serial.available() <= 0);

    String incoming = Serial.readStringUntil('\n');

    if (incoming[0] == '#') {
        return;
    }

    int separator = incoming.indexOf("|");
    if (separator == -1) {
        Serial.println("#" + incoming);
        Serial.println("#No sep found");
        return;
    }

    String command = incoming.substring(0, separator);
    if (!(command == "enter" || command == "exit")) {
        Serial.println("#Command not supported");
        return;
    }

    String cardId = incoming.substring(separator + 1);
    cardId.trim();
    if (cardId == "") {
        Serial.println("#No cardId");
        return;
    }

    WiFiClient client;
    HTTPClient http;

    String connectionUrl = String(serverName) + command + "?card=" + cardId;

    http.begin(client, connectionUrl);

    http.addHeader("Content-Type", "text/plain");
    int httpResponseCode = http.GET();

    if (httpResponseCode != 200) {
        Serial.println("#Response " + httpResponseCode);
        return;
    }

    Serial.print("#HTTP Response code: ");
    Serial.println(httpResponseCode);
    Serial.println(http.getString());

    http.end();
}