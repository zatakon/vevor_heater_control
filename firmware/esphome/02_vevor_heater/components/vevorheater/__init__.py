import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart, text_sensor, binary_sensor, number
from esphome.const import (
    CONF_ID,
    CONF_UART_ID,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ICON,
    CONF_DEVICE_CLASS,
    CONF_ACCURACY_DECIMALS,
)

AUTO_LOAD = ["sensor", "number", "text_sensor", "binary_sensor"]

vevorheater_ns = cg.esphome_ns.namespace("vevorheater")
VevorHeater = vevorheater_ns.class_("VevorHeater", cg.PollingComponent)

# Define configuration keys
CONF_VOLTAGE_SENSOR = "voltage_sensor"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_STATE_SENSOR = "state_sensor"
CONF_STATE_TEXT_SENSOR = "state_text_sensor"
CONF_POWER_LEVEL_SENSOR = "power_level_sensor"
CONF_FAN_SPEED_SENSOR = "fan_speed_sensor"
CONF_PUMP_FREQUENCY_SENSOR = "pump_frequency_sensor"
CONF_INPUT_VOLTAGE_SENSOR = "input_voltage_sensor"
CONF_GLOW_PLUG_CURRENT_SENSOR = "glow_plug_current_sensor"
CONF_COOLING_DOWN_SENSOR = "cooling_down_sensor"
CONF_FAN_VOLTAGE_SENSOR = "fan_voltage_sensor"
CONF_HEAT_EXCHANGER_TEMP_SENSOR = "heat_exchanger_temp_sensor"
CONF_STATE_DURATION_SENSOR = "state_duration_sensor"
CONF_GLOW_PLUG_VOLTAGE_SENSOR = "glow_plug_voltage_sensor"
CONF_GLOW_PLUG_CURRENT_2_SENSOR = "glow_plug_current_2_sensor"
CONF_GLOW_PLUG_TEMPERATURE_SENSOR = "glow_plug_temperature_sensor"

# Short Frame Sensors
CONF_SHORT_POWER_LEVEL_SENSOR = "short_power_level_sensor"
CONF_SHORT_STATE_SENSOR = "short_state_sensor"
CONF_SHORT_STATE_TEXT_SENSOR = "short_state_text_sensor"

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(VevorHeater),
            cv.Required(CONF_UART_ID): cv.use_id(uart.UARTComponent),
            
            # Optional Sensors for Long Frame
            cv.Optional(CONF_VOLTAGE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="V",
                accuracy_decimals=2,
            ),
            cv.Optional(CONF_TEMPERATURE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="°C",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_STATE_SENSOR): sensor.sensor_schema(
                device_class="power",
                icon="mdi:power",
            ),
            cv.Optional(CONF_STATE_TEXT_SENSOR): text_sensor.text_sensor_schema(
            ),
            cv.Optional(CONF_POWER_LEVEL_SENSOR): sensor.sensor_schema(
                unit_of_measurement="%",
                accuracy_decimals=0,
            ),
            cv.Optional(CONF_FAN_SPEED_SENSOR): sensor.sensor_schema(
                unit_of_measurement="RPM",
                accuracy_decimals=0,
            ),
            cv.Optional(CONF_PUMP_FREQUENCY_SENSOR): sensor.sensor_schema(
                unit_of_measurement="Hz",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_INPUT_VOLTAGE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="V",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_GLOW_PLUG_CURRENT_SENSOR): sensor.sensor_schema(
                unit_of_measurement="A",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_COOLING_DOWN_SENSOR): sensor.sensor_schema(
                unit_of_measurement="Status",
                icon="mdi:fan-off",
            ),
            cv.Optional(CONF_FAN_VOLTAGE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="V",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_HEAT_EXCHANGER_TEMP_SENSOR): sensor.sensor_schema(
                unit_of_measurement="°C",
                accuracy_decimals=2,
            ),
            cv.Optional(CONF_STATE_DURATION_SENSOR): sensor.sensor_schema(
                unit_of_measurement="s",
                accuracy_decimals=0,
            ),
            cv.Optional(CONF_GLOW_PLUG_VOLTAGE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="V",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_GLOW_PLUG_CURRENT_2_SENSOR): sensor.sensor_schema(
                unit_of_measurement="A",
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_GLOW_PLUG_TEMPERATURE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="°C",
                accuracy_decimals=1,
            ),
            
            # Optional Sensors for Short Frame
            cv.Optional(CONF_SHORT_POWER_LEVEL_SENSOR): sensor.sensor_schema(
                unit_of_measurement="%",
                accuracy_decimals=0,
            ),
            cv.Optional(CONF_SHORT_STATE_SENSOR): sensor.sensor_schema(
                unit_of_measurement="State",
                icon="mdi:power",
            ),
            cv.Optional(CONF_SHORT_STATE_TEXT_SENSOR): text_sensor.text_sensor_schema(
            ),
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
    
    # Handle optional sensors for Long Frame
    if CONF_VOLTAGE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_SENSOR])
        cg.add(var.set_voltage_sensor(sens))
    
    if CONF_TEMPERATURE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_TEMPERATURE_SENSOR])
        cg.add(var.set_temperature_sensor(sens))
    
    if CONF_STATE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_STATE_SENSOR])
        cg.add(var.set_state_sensor(sens))
    
    if CONF_POWER_LEVEL_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_POWER_LEVEL_SENSOR])
        cg.add(var.set_power_level_sensor(sens))
    
    if CONF_FAN_SPEED_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_FAN_SPEED_SENSOR])
        cg.add(var.set_fan_speed_sensor(sens))
    
    if CONF_PUMP_FREQUENCY_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_PUMP_FREQUENCY_SENSOR])
        cg.add(var.set_pump_frequency_sensor(sens))
    
    if CONF_INPUT_VOLTAGE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_INPUT_VOLTAGE_SENSOR])
        cg.add(var.set_input_voltage_sensor(sens))
    
    if CONF_GLOW_PLUG_CURRENT_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_GLOW_PLUG_CURRENT_SENSOR])
        cg.add(var.set_glow_plug_current_sensor(sens))
    
    if CONF_COOLING_DOWN_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_COOLING_DOWN_SENSOR])
        cg.add(var.set_cooling_down_sensor(sens))
    
    if CONF_FAN_VOLTAGE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_FAN_VOLTAGE_SENSOR])
        cg.add(var.set_fan_voltage_sensor(sens))
    
    if CONF_HEAT_EXCHANGER_TEMP_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_HEAT_EXCHANGER_TEMP_SENSOR])
        cg.add(var.set_heat_exchanger_temp_sensor(sens))
    
    if CONF_STATE_DURATION_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_STATE_DURATION_SENSOR])
        cg.add(var.set_state_duration_sensor(sens))
    
    if CONF_GLOW_PLUG_VOLTAGE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_GLOW_PLUG_VOLTAGE_SENSOR])
        cg.add(var.set_glow_plug_voltage_sensor(sens))
    
    if CONF_GLOW_PLUG_CURRENT_2_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_GLOW_PLUG_CURRENT_2_SENSOR])
        cg.add(var.set_glow_plug_current_2_sensor(sens))
    
    if CONF_GLOW_PLUG_TEMPERATURE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_GLOW_PLUG_TEMPERATURE_SENSOR])
        cg.add(var.set_glow_plug_temperature_sensor(sens))
    
    # Handle optional sensors for Short Frame
    if CONF_SHORT_POWER_LEVEL_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_SHORT_POWER_LEVEL_SENSOR])
        cg.add(var.set_short_power_level_sensor(sens))
    
    if CONF_SHORT_STATE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_SHORT_STATE_SENSOR])
        cg.add(var.set_short_state_sensor(sens))

    if CONF_SHORT_STATE_TEXT_SENSOR in config:
        sens = await text_sensor.new_text_sensor(config[CONF_SHORT_STATE_TEXT_SENSOR])
        cg.add(var.set_short_state_text_sensor(sens))
    
    # Add more sensors handling as needed
