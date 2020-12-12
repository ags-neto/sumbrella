/**********************  WiFi SSID Name and Password **************************/

String Host_name = "Vodafone-165DB9";
String password = "<REDACTED>";

void RESET();
String Rain();

void setup(void) {
  Serial.begin(9600);
  Serial1.begin(9600);
}

void loop(void) {
  RESET();
  delay(1000);
  Serial.println(Rain());

}

void RESET()
{
  //Disconnecting previous networks
  sendData("AT+RST\r\n", 2000, DEBUG);
  sendData("AT+CWQAP\r\n", 5000, DEBUG); // Disconnect WiFi if connected.

  //Selecting Mode for WiFi
  sendData("AT+CWMODE=3\r\n", 1000, DEBUG); // configure as  both access point and station mode.

  //Searching for the wifi Connecrions.
  delay(3000);

  sendData("AT+CWQAP\r\n", 4000, DEBUG); // again quit the connection if any.

  String conn = "AT+CWJAP";
  char inv = '"';
  conn += "=";
  conn += inv;
  conn += Host_name;  // Host name
  conn += inv;
  conn += ",";
  conn += inv;
  conn += password; // Password
  conn += inv;
  conn += "\r\n\r\n";
  sendData(conn, 7000, DEBUG); // Join the connection.( AT+CWJAP = "Host_name","password" )
}


String Rain()
{
  char inv = '"';
  String add = "AT+CIPSTART";
  add += "=";
  add += inv;
  add += "TCP";
  add += inv;
  add += ",";
  add += inv;
  add += "api.thingspeak.com";  // Host_server_name
  add += inv;
  add += ",";
  add += "80";
  add += "\r\n";
  sendData(add, 3000, 0);  // Establishing a TCP Connection. ( AT+CIPSTART = "TCP","Host_server_name",80 )

  String rest = "AT+CIPSEND=90";
  rest += "\r\n";
  sendData(rest, 2000, 0); //Number of characters to send. ( "AT+CIPSEND=90" )


  String hostt = "GET /apps/thinghttp/send_request?api_key=<REDACTED>";
  hostt += "\r\n";
  hostt += "Host:api.thingspeak.com";
  hostt += "\r\n\r\n\r\n\r\n\r\n";
  String Rain = sendData(hostt, 2000, 1);  // GET request ( GET /apps/thinghttp/send_request?api_key=<REDACTED>
                                           // Host: Host_server_name )
  return (Rain);
}

String sendData(String command, const int Goldout, boolean debug)
{
  String response = "";

  Serial1.print(command); // send the read character to the Serial1

  long int Gold = millis();

  while ( (Gold + Goldout) > millis())
  {
    while (Serial1.available())
    {

      // The esp has data so display its output to the serial window
      char c = Serial1.read(); // read the next character.
      response += c;
    }
  }

  if (debug)
  {
    Serial.print(response);
  }

  return response;
}
