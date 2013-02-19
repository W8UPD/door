//*************Mike Swaisgood************Ricky Elrod************Jimmy Carter*****************************//
//A program to read RFID tags from a HID ProxPoint Plus. Uses Data0 (GRN) for 1s and Data1 (WHT) for 0s.  //
//Our cards use 16 bit numbers to identify different cards. Checks to match these numbers.                //
//Writes a 1 to srike pin for 3 seconds when card is found to exsist in card array.                       //
//Intrrupt based program. Reads bits by calling an intrrupt when they're seen on the data lines.          //
//Waits for data to be recieved, throws out parity bit and pharses last 16bits.                           //
//********************************************************************************************************//


#include <avr/io.h>
#include <avr/wdt.h>

#define Reset_AVR() wdt_enable(WDTO_30MS); while(1) {}

int pin = 7;                           //strike pin
String binary;                         //string used to store bit pharse

void setup() {                         //Initialize Arduino
  pinMode(pin, OUTPUT);                //Set strike pin to output
  Serial.begin(9600);                  //Serial baud rate and initialize
  Serial.println("S");                 //Let user know program started
  attachInterrupt(0, incScanA, LOW);   //white 1 bits
  attachInterrupt(1, incScanB, LOW);   //green 0 bits
}

void loop() {                          //int main function
  digitalWrite(pin, LOW);              //write strike low
  while(true) {                        //loop this for ever
  delay(1000);                         //delay one second
  check();                             //check for data
  };
}

void incScanA() {                      //intrrupt for 1 bits
  binary += 1;                         //add one to binary string
}

void incScanB() {                      //intrrupt for 0 bits
  binary += 0;                         //add zero to binary string
}

void check() {                         //check data recieved from RFID
  int len = binary.length();           //get length of bit stream
  if (len < 16) return;                //if random bits ignore
  int lenb = len-1;                    //length one from end
  String getit;                        //declare string for 16bit number from card
  for(int i = len-17;i < lenb;i++){    //pharse bit stream 16 ending bits excluding the very last bit
    getit += binary[i];                //add pharsed char to 16 bit number
  }

    
  for (int i = 0; i <= sizeof(cards); i++){              //run through card values
    if (getit == cards[i] && auth[i] == 1){              //if one matches, and is authorized
      Serial.println(i + ":" + names[i] + "1");    //indicate the strie is open
      digitalWrite(pin, HIGH);                           //open the strike
      delay(3000);                                       //leave for 3 seconds
      digitalWrite(pin, LOW);                            //close the strike
      Serial.println(i + ":" + names[i] + "0");    //indicate the strike is closed
      Reset_AVR();
    }
  }

  binary = "";        //clear the data recieved
  getit = "";         //clear the pharsed data
}

