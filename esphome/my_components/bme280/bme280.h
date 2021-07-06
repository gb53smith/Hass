#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/i2c/i2c.h"

// Using this external library
#include <SparkFunBME280.h>

namespace esphome {
namespace bme280 {

/** Enum listing all Oversampling values for the BME280.
 *
 * Oversampling basically means measuring a condition multiple times. Higher oversampling
 * values therefore increase the time required to read sensor values but increase accuracy.
 */
enum BME280Oversampling {
  BME280_OVERSAMPLING_NONE = 0,
  BME280_OVERSAMPLING_1X = 1,
  BME280_OVERSAMPLING_2X = 2,
  BME280_OVERSAMPLING_4X = 4,
  BME280_OVERSAMPLING_8X = 8,
  BME280_OVERSAMPLING_16X = 16,
};

/** Enum listing all Infinite Impulse Filter values for the BME280.
 *
 * Higher values increase accuracy, but decrease response time.
 */
enum BME280IIRFilter {
  BME280_IIR_FILTER_OFF = 0,
  BME280_IIR_FILTER_2X = 1,
  BME280_IIR_FILTER_4X = 2,
  BME280_IIR_FILTER_8X = 3,
  BME280_IIR_FILTER_16X = 4,
};

/// This class implements support for the BME280 Temperature+Pressure+Humidity i2c sensor.
class BME280Component : public PollingComponent, public i2c::I2CDevice {
 public:
  void set_temperature_sensor(sensor::Sensor *temperature_sensor) { temperature_sensor_ = temperature_sensor; }
  void set_pressure_sensor(sensor::Sensor *pressure_sensor) { pressure_sensor_ = pressure_sensor; }
  void set_humidity_sensor(sensor::Sensor *humidity_sensor) { humidity_sensor_ = humidity_sensor; }
  /// Set the oversampling value for the temperature sensor. Default is 16x.
  void set_temperature_oversampling(BME280Oversampling temperature_over_sampling);
  /// Set the oversampling value for the pressure sensor. Default is 16x.
  void set_pressure_oversampling(BME280Oversampling pressure_over_sampling);
  /// Set the oversampling value for the humidity sensor. Default is 16x.
  void set_humidity_oversampling(BME280Oversampling humidity_over_sampling);
  /// Set the IIR Filter used to increase accuracy, defaults to no IIR Filter.
  void set_iir_filter(BME280IIRFilter iir_filter);

  // ========== INTERNAL METHODS ==========
  // (In most use cases you won't need these)
  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;
  void update() override;

 protected:
  BME280Oversampling temperature_oversampling_{BME280_OVERSAMPLING_16X};
  BME280Oversampling pressure_oversampling_{BME280_OVERSAMPLING_16X};
  BME280Oversampling humidity_oversampling_{BME280_OVERSAMPLING_16X};
  BME280IIRFilter iir_filter_{BME280_IIR_FILTER_OFF};
  sensor::Sensor *temperature_sensor_;
  sensor::Sensor *pressure_sensor_;
  sensor::Sensor *humidity_sensor_;
  ::BME280 *bme280_sensor_;
};

}  // namespace bme280
}  // namespace esphome