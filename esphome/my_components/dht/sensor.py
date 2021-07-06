import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import sensor
from esphome.const import (
    CONF_HUMIDITY,
    CONF_ID,
    CONF_MODEL,
    CONF_PIN,
    CONF_TEMPERATURE,
    ICON_EMPTY,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_PERCENT,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
)

from esphome.cpp_helpers import gpio_pin_expression

dht_ns = cg.esphome_ns.namespace("dht")
#GBS Modified to use DHT models defined in DHTNew.h
dhtnew_ns = cg.esphome_ns.namespace("")
DHTModel_t = dhtnew_ns.enum("DHTModel")

DHT_MODELS = {
    "DHT11": DHTModel_t.DHT_MODEL_DHT11,
    "DHT22": DHTModel_t.DHT_MODEL_DHT22
}
DHT = dht_ns.class_("DHT", cg.PollingComponent)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(DHT),
        cv.Required(CONF_PIN): pins.gpio_input_pin_schema,
        cv.Optional(CONF_TEMPERATURE): sensor.sensor_schema(
            UNIT_CELSIUS,
            ICON_EMPTY,
            1,
            DEVICE_CLASS_TEMPERATURE,
            STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_HUMIDITY): sensor.sensor_schema(
            UNIT_PERCENT, ICON_EMPTY, 0, DEVICE_CLASS_HUMIDITY, STATE_CLASS_MEASUREMENT
        ),
        cv.Optional(CONF_MODEL, default="dht22"): cv.enum(
            DHT_MODELS, upper=True, space="_"
        ),
    }
).extend(cv.polling_component_schema("60s"))


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    pin = await gpio_pin_expression(config[CONF_PIN])
    cg.add(var.set_pin(pin))

    if CONF_TEMPERATURE in config:
        sens = await sensor.new_sensor(config[CONF_TEMPERATURE])
        cg.add(var.set_temperature_sensor(sens))
    if CONF_HUMIDITY in config:
        sens = await sensor.new_sensor(config[CONF_HUMIDITY])
        cg.add(var.set_humidity_sensor(sens))

    cg.add(var.set_dht_model(config[CONF_MODEL]))
    cg.add_library("diaoul/DHTNew", "1.0.0")