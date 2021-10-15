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
    Bluetooth.begin(38400);

    servo1.attach(8);
    servo2.attach(10);
    servo3.attach(11); // Base

    Serial.println("Starting...");
}

void loop(){
   
    if (Bluetooth.available()){

        String instruction;
        int value, index = 0;

        String s = Bluetooth.readString();
        Serial.print("\nIN: "+s);


        for(index; index<s.length(); index++){ /* splits the sting format to inst and value, eg: S1:123 -> s1 123*/
            if (s[index] == ':')
                break;
        }
        instruction = s.substring(0, index);
        value = s.substring(index+1, s.length()).toInt();
           
        Serial.println("VALUE: "+(String)value+" instruction:"+instruction);


        if (instruction.equals("S1")){

            servo1.write(value);
        }

        else if (instruction.equals("S2")){
            servo2.write(value);
        }
        
        else if (instruction.equals("B1")){
            servo3.write(value);
        }


        Bluetooth.write("Done");
    }

}
