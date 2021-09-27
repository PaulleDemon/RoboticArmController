#include <string.h>
#include <Servo.h>
#include <SoftwareSerial.h>


#define RX 3
#define TX 4

SoftwareSerial Bluetooth(RX, TX);

Servo servo1;
Servo servo2;
Servo servo3;

void setup(){

    Serial.begin(9600);
    Serial.println("Starting...");

    Bluetooth.begin(38400);

    servo1.attach(8);
    servo2.attach(9);
    servo3.attach(10);

    Serial.println("Starting...");
}

void loop(){
   
    if (Bluetooth.available()){

        String instruction;
        int value, found=0, index = 0;

        String s = Bluetooth.readString();
        Serial.print("\nIN: ");
        Serial.print(s);

        for(index; index<s.length(); index++){ /* splits the sting format to inst and value, eg: S1:123 -> s1 123*/
            if (s[index] != ':' && found == 0)
                instruction[index] = s[index];
            
            else{
                value = s.substring(index+1, s.length()).toInt();
                found = 1;
                break;
            }
        }


        if (instruction.compareTo("S1")){
            servo1.write(value);
        }

        else if (instruction.compareTo("S2")){
            servo2.write(value);
        }
        
        else if (instruction.compareTo("S3")){
            servo3.write(value);
        }


        Bluetooth.write("Done");
    }

}
