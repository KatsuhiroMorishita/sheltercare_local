/*****************************************************************************

******************************************************************************/
#include <Wire.h>
#include <RPR-0521RS.h>

#define byte uint8_t // add for error of byte

RPR0521RS rpr0521rs;

void setup() {
  byte rc;

  Serial.begin(38400);
  while (!Serial);
  
  Wire.begin();
  
  rc = rpr0521rs.init();
}

float _als_val = 0;
void loop() {
  byte rc;
  unsigned short ps_val;
  float als_val;
  byte near_far;
  
  rc = rpr0521rs.get_psalsval(&ps_val, &als_val);
  if (rc == 0) {    
    if (als_val != RPR0521RS_ERROR) {
      float diff = (_als_val - als_val) / 1023;
      Serial.println(diff);
      _als_val = als_val;
    }
  }
  
  delay(500);

}
