#include "esphome.h"
#include "esphome/core/log.h"
#include "esphome/core/helpers.h"
#include "DHTNew.h"


class MyDHT : public PollingComponent, public Sensor {
 public:
  Sensor *temperature_sensor = new Sensor();
  Sensor *humidity_sensor = new Sensor();
  // constructor.  Update interval set here to 10s
  MyDHT() : PollingComponent(10000) {}

  float get_setup_priority() const override { return esphome::setup_priority::DATA; }
  // Pin and model type set here
  DHT dht_dht{2, DHT_MODEL_DHT22};
  void setup() override {
    // This will be called by App.setup()
   
  }
  void update() override {
    // This will be called every "update_interval" milliseconds.
    float temperature = dht_dht.readTemperature();
    ESP_LOGD("custom", "The value of my temperature is: %f", temperature);
    temperature_sensor->publish_state(temperature);
    float humidity = dht_dht.readHumidity();
    ESP_LOGD("custom", "The value of my humidity is: %f", humidity);
    humidity_sensor->publish_state(humidity);
  }
};