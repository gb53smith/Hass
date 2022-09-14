#include "esphome.h"

class MyCustomComponent : public Component, public CustomMQTTDevice {
 public:
  void setup() override {
    // This will be called once to set up the component
    // think of it as the setup() call in Arduino
    pinMode(2, OUTPUT);  // Wemos D1 Blue LED

    subscribe("the/topic", &MyCustomComponent::on_message);

    // also supports JSON messages
    subscribe_json("the/json/topic", &MyCustomComponent::on_json_message);
  }
  void on_message(const std::string &payload) {
    if (payload == "ON") {
      digitalWrite(2, HIGH);
      publish("the/other/topic", "Hello World!");
    } else {
      digitalWrite(2, LOW);
      publish("the/other/topic", 42);
    }
  }
 void on_json_message(JsonObject root) {
    if (!root.containsKey("key"))
      return;

    int value = root["key"];
    // do something with Json Object

    // publish JSON using lambda syntax
    publish_json("the/other/json/topic", [=](JsonObject root2) {
      root2["key"] = value;
    });
 }
};

