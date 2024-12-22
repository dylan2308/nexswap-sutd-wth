#include <SPI.h>
#include <PN532_SPI.h>
#include <NfcAdapter.h>

#define pinPing 16
#define pinPong 4

PN532_SPI pn532spi(SPI, 5);
NfcAdapter nfc = NfcAdapter(pn532spi);

void setup() {
  pinMode(pinPing, OUTPUT);
  pinMode(pinPong, OUTPUT);
  Serial.begin(115200);
  Serial.println("NDEF Reader");
  nfc.begin();
}

void loop() {

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove any trailing whitespace or newline
    if (command == "PING") {
      Serial.println("PONG");
      digitalWrite(pinPong,HIGH);
    }
  }

  nfcReader(1500);
}

void nfcReader(int timeDelay) {

  //Serial.println("Waiting for incoming");

  if (nfc.tagPresent()) {
    NfcTag tag = nfc.read();
    if (tag.hasNdefMessage()) {
      NdefMessage message = tag.getNdefMessage();
      extractAndPrintUri(message);
    } else {
      Serial.println("No NDEF message found.");
      digitalWrite(pinPing,LOW);
    }
  }
  delay(timeDelay);
  digitalWrite(pinPing,LOW);
}

// Function to extract and print URI from NDEF message
void extractAndPrintUri(NdefMessage message) {
  for (int i = 0; i < message.getRecordCount(); i++) {
    NdefRecord record = message.getRecord(i);
    if (record.getTnf() == 0x01 && record.getType()[0] == 'U') {
      // URI record
      int payloadLength = record.getPayloadLength();
      byte payload[payloadLength];
      record.getPayload(payload);

      switch (payload[0]) {                  // Decode the URI prefix
        case 0x00: Serial.print(""); break;  // No prefix
        case 0x01: Serial.print("http://www."); break;
        case 0x02: Serial.print("https://www."); break;
        case 0x03: Serial.print("http://"); break;
        case 0x04: Serial.print("https://"); break;
        // Add more prefixes as needed based on NFC Forum specifications
        default: Serial.print("Unknown Prefix"); break;
      }

      for (int j = 1; j < payloadLength; j++) {
        Serial.print((char)payload[j]);
      }
      Serial.println();
      digitalWrite(pinPing,HIGH);
    } else {
      Serial.println("Not a URI record.");
      digitalWrite(pinPing,LOW);
    }
  }
}
