import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, switch, text_sensor, ntc, uart, number
from esphome.components.esp32 import get_esp32_variant
from esphome.const import (
    CONF_TEXT_SENSORS,
    CONF_ID,
    CONF_HARDWARE_UART,
    CONF_UART_ID,
    CONF_SENSOR_ID,
    CONF_BINARY,
    CONF_AUTO_MODE,
    CONF_TEMPERATURE,
    CONF_VOLTAGE,
    CONF_CURRENT,
    CONF_PIN,
    CONF_NUMBER,
    CONF_LAMBDA,
    CONF_UPDATE_INTERVAL,
    DEVICE_CLASS_TEMPERATURE,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
)
# from . import (
#     ATTENUATION_MODES,
#     ESP32_VARIANT_ADC1_PIN_TO_CHANNEL,
#     ESP32_VARIANT_ADC2_PIN_TO_CHANNEL,
#     validate_adc_pin,
# )

AUTO_LOAD = ["number", "i2c", "sensor"]

vevorheater_ns = cg.esphome_ns.namespace("vevorheater")
VevorHeater = vevorheater_ns.class_("VevorHeater", cg.PollingComponent)

CONFIG_SCHEMA = (
    cv.Schema(
        {
        cv.GenerateID(CONF_ID): cv.declare_id(VevorHeater),
        # cv.Optional(CONF_SPEED): SPEED_SCHEMA,
        # cv.Optional(CONF_POWER): POWER_SCHEMA
        }
    )   
    .extend(
        {   
            cv.Required(CONF_UART_ID): cv.use_id(uart.UARTComponent),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(cv.polling_component_schema('10ms'))
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    
    uart_device = await cg.get_variable(config[CONF_UART_ID])
    cg.add(var.set_uart_bus(uart_device))

    # speed = config.get(CONF_SPEED)
    # sensor_speed = await sensor.new_sensor(speed)
    # cg.add(var.set_sensor_speed(sensor_speed))

    # power = config.get(CONF_POWER)
    # number_component = await cg.get_variable(power[NUMBER_ID])
    # cg.add(var.set_number_power(number_component))