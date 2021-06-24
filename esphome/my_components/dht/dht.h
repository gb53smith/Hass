#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace dht {

typedef enum DHTModel {
  DHT_MODEL_AUTO_DETECT = 0,
  DHT_MODEL_DHT11,
  DHT_MODEL_DHT22,
  DHT_MODEL_DHT21,
  DHT_MODEL_AM2302,
  DHT_MODEL_RHT03,
  DHT_MODEL_SI7021,
  DHT_MODEL_DHT22_TYPE2
} DHTModel_t;

// DHTError_t
typedef enum {
    DHT_ERROR_NONE = 0,
    DHT_ERROR_TIMEOUT_START,
    DHT_ERROR_TIMEOUT_DATA,
    DHT_ERROR_CHECKSUM
} DHTError_t;

/// Component for reading temperature/humidity measurements from DHT11/DHT22 sensors.
class DHT : public PollingComponent {
 public:
  /** Manually select the DHT model.
   *
   * Valid values are:
   *
   *  - DHT_MODEL_AUTO_DETECT (default)
   *  - DHT_MODEL_DHT11
   *  - DHT_MODEL_DHT22
   *  - DHT_MODEL_AM2302
   *  - DHT_MODEL_RHT03
   *  - DHT_MODEL_SI7021
   *  - DHT_MODEL_DHT22_TYPE2
   *
   * @param model The DHT model.
   */
  void set_dht_model(DHTModel model);

  void set_pin(GPIOPin *pin) { pin_ = pin; }
  void set_model(DHTModel model) { model_ = model; }
  void set_temperature_sensor(sensor::Sensor *temperature_sensor) { temperature_sensor_ = temperature_sensor; }
  void set_humidity_sensor(sensor::Sensor *humidity_sensor) { humidity_sensor_ = humidity_sensor; }

  /// Set up the pins and check connection.
  void setup() override;
  void dump_config() override;
  /// Update sensor values and push them to the frontend.
  void update() override;
  /// HARDWARE_LATE setup priority.
  float get_setup_priority() const override;
  int getMinimumSamplingPeriod() {return _model == DHT_MODEL_DHT11 ? 1000 : 2000;}

 protected:
  //bool read_sensor_(float *temperature, float *humidity, bool report_errors);
  bool read(bool force);

  GPIOPin *pin_;
  DHTModel model_{DHT_MODEL_AUTO_DETECT};
  bool is_auto_detect_{false};
  sensor::Sensor *temperature_sensor_{nullptr};
  sensor::Sensor *humidity_sensor_{nullptr};
 
  uint8_t _pin;
  float _temperature;
  float _humidity;

 private:
  DHTModel_t _model;
  DHTError_t _error;
  unsigned long _lastReadTime;
};

}  // namespace dht
}  // namespace esphome
