#include <DS3231.h>

DS3231 rtc(SDA, SCL);     // real time clock variable
void rgLed(int redValue, int greenValue);     // simple red and green led display funct

void setup() {
  Serial.begin(9600);
  
  rtc.begin();            // rtc setup
  pinMode(5, OUTPUT);     // red pin
  pinMode(6, OUTPUT);     // green pin
}

void loop() {
  Serial.println(rtc.getTimeStr());     // show clock on monitor
  
  Time t = rtc.getTime();       // gets struct from rtc
  int timewindow = t.hour;      // gets hour from struct
  if (timewindow > 7 && timewindow < 14) {
    rgLed(150, 150);
    delay(1000);
  } else {
    rgLed(0, 0);
    delay(1000);
  }
}

void rgLed(int redValue, int greenValue) {
  analogWrite(5, redValue);
  analogWrite(6, greenValue);
}
