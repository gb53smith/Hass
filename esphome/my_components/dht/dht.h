#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
/*
Using Platformio library: "diaoul/DHTNew @ 1.0.0"
*/
#include "DHTNew.h"

namespace esphome {
namespace dht {

/// Component for reading temperature/humidity measurements from DHT11/DHT22 sensors.
class DHT : public PollingComponent {
 public:
  void set_pin(GPIOPin *pin) { dhtPin_ = pin->get_pin(); }
  void set_dht_model(DHTModel_t model);
  void set_temperature_sensor(sensor::Sensor *temperature_sensor) { temperature_sensor_ = temperature_sensor; }
  void set_humidity_sensor(sensor::Sensor *humidity_sensor) { humidity_sensor_ = humidity_sensor; }

  /// Set up the pins and check connection.
  void setup() override;
  void dump_config() override;
  /// Update sensor values and push them to the front end.
  void update() override;
  /// HARDWARE_LATE setup priority.
  float get_setup_priority() const override;

 protected:
  //Read sensor and return error message;
  const char* readSensor();

  uint8_t dhtPin_;
  DHTModel_t model_{};

  sensor::Sensor *temperature_sensor_{nullptr};
  sensor::Sensor *humidity_sensor_{nullptr};

  //Object from DHTNew library
  // Using pointer to set parameters later in setup method when they are available.
  ::DHT *dhtnew_;
 
  float _temperature;
  float _humidity;

 private:
  DHTModel_t _model; // from DHTNEw
  DHTError_t _error; // from DHTNEw
  unsigned long _lastReadTime;
};

}  // namespace dht
}  // namespace esphome
