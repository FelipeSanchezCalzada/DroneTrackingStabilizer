
#include <CPPM.h>

void setup(){
	Serial.begin(250000);
  Serial.setTimeout(1);
	CPPM.begin();
}

void loop(){
     if(Serial.available()){
      
      String str = Serial.readString();
            
      String ch1_str = str.substring(0, str.indexOf(' '));
      int ch1 = ch1_str.toInt();
      int ch2 = str.substring(ch1_str.length() + 1).toInt();
   
      Serial.print(ch1);
      Serial.print(" ");
      Serial.print(ch2);
      Serial.println("");
      CPPM.write_us(0, ch1);
      CPPM.write_us(1, ch2);
      
     }
}

