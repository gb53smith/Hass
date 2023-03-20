#include "esphome.h"

class MyCPU : public PollingComponent, public Sensor {
 public:
  Sensor *cpu_sensor = new Sensor();

  // constructor.  Update interval set here to 60s
  MyCPU() : PollingComponent(60000) {}

  float get_setup_priority() const override { return esphome::setup_priority::DATA; }

  void setup() override {
    // This will be called by App.setup()  
  }
  void update() override {
    // This will be called every "update_interval" milliseconds.
	uint32_t freq = getCpuFrequencyMhz();
	//uint32_t freq = getXtalFrequencyMhz();
    cpu_sensor->publish_state(freq);
    ESP_LOGD("custom", "CPU Frequency is: %d", freq);
  }
};