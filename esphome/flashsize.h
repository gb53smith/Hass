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
  }
};