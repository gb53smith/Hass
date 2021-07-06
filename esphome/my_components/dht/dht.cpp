#include "dht.h"
#include "esphome/core/log.h"
#include "esphome/core/helpers.h"

namespace esphome {
namespace dht {

static const char *const TAG = "dht";

void DHT::setup() {
  // Create DHT object using pointer.  This is after parameters are available.
  dhtnew_ = new ::DHT(this->pin_, this->model_);
}

void DHT::dump_config() {
  ESP_LOGCONFIG(TAG, "DHT:");
  ESP_LOGCONFIG(TAG, "  Pin: %d", this->pin_);
  if (this->model_ == DHT_MODEL_DHT11) {
    ESP_LOGCONFIG(TAG, "  Model: DHT11");
  } else {
    ESP_LOGCONFIG(TAG, "  Model: DHT22 (or equivalent)");
  }
  LOG_UPDATE_INTERVAL(this);
  LOG_SENSOR("  ", "Temperature", this->temperature_sensor_);
  LOG_SENSOR("  ", "Humidity", this->humidity_sensor_);
}

void DHT::update() {
  const char *error_string = this->readSensor();
  const char *success = "none";

  if (strcmp(error_string, success) == 0) {
    ESP_LOGD(TAG, "Got Temperature=%.1f°C Humidity=%.1f%%", _temperature, _humidity);
    if (this->temperature_sensor_ != nullptr)
      this->temperature_sensor_->publish_state(_temperature);
    if (this->humidity_sensor_ != nullptr)
      this->humidity_sensor_->publish_state(_humidity);
    this->status_clear_warning();
  } else {
      ESP_LOGD(TAG, "Got this DHT error: %s.", error_string);
    if (this->temperature_sensor_ != nullptr)
      this->temperature_sensor_->publish_state(NAN);
    if (this->humidity_sensor_ != nullptr)
      this->humidity_sensor_->publish_state(NAN);
    this->status_set_warning();
  }
}

float DHT::get_setup_priority() const { return setup_priority::DATA; }

void DHT::set_dht_model(DHTModel_t model) {
  this->model_ = model;
} 

//Read sensor and return error message;
const char* DHT::readSensor() {

  _temperature = NAN;
  _humidity = NAN;

  _temperature = dhtnew_->readTemperature();
  _humidity = dhtnew_->readHumidity();
    
  const char* error_string = dhtnew_->getErrorString();
    
  return error_string;
}

}  // namespace dht
}  // namespace esphome
