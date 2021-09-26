#include <SoftwareSerial.h>

#define RX 10
#define TX 11

SoftwareSerial Bluetooth(RX, TX);

void setup(){

    Serial.begin(9600);
    Bluetooth.begin(38400);
    Serial.println("Starting...");
}

void loop(){
    
}
