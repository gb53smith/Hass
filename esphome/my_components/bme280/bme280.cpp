#include "bme280.h"
#include "esphome/core/log.h"

namespace esphome {
namespace bme280 {

static const char *const TAG = "bme280.sensor";


static const char *oversampling_to_str(BME280Oversampling oversampling) {
  switch (oversampling) {
    case BME280_OVERSAMPLING_NONE:
      return "None";
    case BME280_OVERSAMPLING_1X:
      return "1x";
    case BME280_OVERSAMPLING_2X:
      return "2x";
    case BME280_OVERSAMPLING_4X:
      return "4x";
    case BME280_OVERSAMPLING_8X:
      return "8x";
    case BME280_OVERSAMPLING_16X:
      return "16x";
    default:
      return "UNKNOWN";
  }
}

static const char *iir_filter_to_str(BME280IIRFilter filter) {
  switch (filter) {
    case BME280_IIR_FILTER_OFF:
      return "OFF";
    case BME280_IIR_FILTER_2X:
      return "2x";
    case BME280_IIR_FILTER_4X:
      return "4x";
    case BME280_IIR_FILTER_8X:
      return "8x";
    case BME280_IIR_FILTER_16X:
      return "16x";
    default:
      return "UNKNOWN";
  }
}

void BME280Component::setup() {
  ESP_LOGCONFIG(TAG, "Setting up BME280...");
  bme280_sensor_ =  new ::BME280;
  bme280_sensor_->beginI2C();
  bme280_sensor_->setHumidityOverSample(this->humidity_oversampling_);
  bme280_sensor_->setTempOverSample(this->temperature_oversampling_);
  bme280_sensor_->setPressureOverSample(this->pressure_oversampling_);
  bme280_sensor_->setFilter(this->iir_filter_);
}

void BME280Component::dump_config() {
  ESP_LOGCONFIG(TAG, "BME280:");
  ESP_LOGCONFIG(TAG, "  IIR Filter: %s", iir_filter_to_str(this->iir_filter_));
  LOG_UPDATE_INTERVAL(this);
  LOG_SENSOR("  ", "Temperature", this->temperature_sensor_);
  ESP_LOGCONFIG(TAG, "    Oversampling: %s", oversampling_to_str(this->temperature_oversampling_));
  LOG_SENSOR("  ", "Pressure", this->pressure_sensor_);
  ESP_LOGCONFIG(TAG, "    Oversampling: %s", oversampling_to_str(this->pressure_oversampling_));
  LOG_SENSOR("  ", "Humidity", this->humidity_sensor_);
  ESP_LOGCONFIG(TAG, "    Oversampling: %s", oversampling_to_str(this->humidity_oversampling_));
}

float BME280Component::get_setup_priority() const { return setup_priority::DATA; }

void BME280Component::update() {
  // Enable sensor
  ESP_LOGV(TAG, "Sending conversion request...");
 
  float temperature = bme280_sensor_->readTempC();
  
  if (isnan(temperature)) {
    ESP_LOGW(TAG, "Invalid temperature, cannot read pressure & humidity values.");
    this->status_set_warning();
    return;
  }

  float pressure = bme280_sensor_->readFloatPressure() / 100.0;
  float humidity = bme280_sensor_->readFloatHumidity();
  
  /* // Start of test 
  //Read registers to confirm yaml options are getting to the right registers
  // Board needs power reset to get the right values
  uint8_t cmr = bme280_sensor_->readRegister(BME280_CTRL_MEAS_REG);
  uint8_t chr = bme280_sensor_->readRegister(BME280_CTRL_HUMIDITY_REG);
  uint8_t cfgr = bme280_sensor_->readRegister(BME280_CONFIG_REG);
  
  ESP_LOGD(TAG, "BME280_CTRL_MEAS_REG: %d ", cmr);
  ESP_LOGD(TAG, "BME280_CTRL_HUMIDITY_REG: %d ", chr);
  ESP_LOGD(TAG, "BME280_CONFIG_REG): %d ", cfgr);
  
  ESP_LOGD(TAG, "Temperature Oversampling: %d ", this->temperature_oversampling_);
  ESP_LOGD(TAG, "Pressure Oversampling: %d ", this->pressure_oversampling_);
  // End of test */
  
  ESP_LOGD(TAG, "Got temperature=%.1f°C pressure=%.1fhPa humidity=%.1f%%", temperature, pressure, humidity);
  if (this->temperature_sensor_ != nullptr)
    this->temperature_sensor_->publish_state(temperature);
  if (this->pressure_sensor_ != nullptr)
    this->pressure_sensor_->publish_state(pressure);
  if (this->humidity_sensor_ != nullptr)
    this->humidity_sensor_->publish_state(humidity);
  this->status_clear_warning();
}

void BME280Component::set_temperature_oversampling(BME280Oversampling temperature_oversampling) {
  this->temperature_oversampling_ = temperature_oversampling; 
}

void BME280Component::set_pressure_oversampling(BME280Oversampling pressure_oversampling) {
  this->pressure_oversampling_ = pressure_oversampling;
}

void BME280Component::set_humidity_oversampling(BME280Oversampling humidity_oversampling) {
  this->humidity_oversampling_ = humidity_oversampling;
}

void BME280Component::set_iir_filter(BME280IIRFilter iir_filter) { this->iir_filter_ = iir_filter; }

}  // namespace bme280
}  // namespace esphome