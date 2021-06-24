#include "esphome.h"

class MyFlash : public PollingComponent, public Sensor {
 public:
  Sensor *flash_sensor = new Sensor();

  // constructor.  Update interval set here to 60s
  MyFlash() : PollingComponent(60000) {}
  EspClass ESP;
  
   

  float get_setup_priority() const override { return esphome::setup_priority::DATA; }

  void setup() override {
    // This will be called by App.setup()  
  }
  void update() override {
    // This will be called every "update_interval" milliseconds.
    float flashsize = float(ESP.getFlashChipRealSize());
    flash_sensor->publish_state(flashsize);
    ESP_LOGD("custom", "The flash size is: %f", flashsize);
   uint8_t data2 = 0x80;
   uint8_t data3 = 0xFF;
   uint16_t raw_temperature = (uint16_t(data2 & 0xFF) << 8) | (data3 & 0xFF);
    
    if ((raw_temperature & 0x8000) != 0)
         raw_temperature = ~(raw_temperature & 0x7FFF);
   
   float temperature = int16_t(raw_temperature) * 0.1f;
    
    
    ESP_LOGD("custom", "The temperature is: %f", temperature );
  }
};