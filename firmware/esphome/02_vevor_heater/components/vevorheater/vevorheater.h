// vevorheater.h

#pragma once

#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/core/preferences.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/uart/uart.h"

#include <vector>

namespace esphome {
namespace vevorheater {

class VevorHeater : public PollingComponent {
 public:
  void set_uart_bus(uart::UARTComponent *uart) { uart_ = uart; }

  // Setters for Long Frame Sensors
  void set_voltage_sensor(sensor::Sensor *sensor) { voltage_sensor_ = sensor; }
  void set_temperature_sensor(sensor::Sensor *sensor) { temperature_sensor_ = sensor; }
  void set_state_sensor(sensor::Sensor *sensor) { state_sensor_ = sensor; }
  void set_state_text_sensor(text_sensor::TextSensor *sensor) { state_text_sensor_ = sensor; }
  void set_power_level_sensor(sensor::Sensor *sensor) { power_level_sensor_ = sensor; }
  void set_fan_speed_sensor(sensor::Sensor *sensor) { fan_speed_sensor_ = sensor; }
  void set_pump_frequency_sensor(sensor::Sensor *sensor) { pump_frequency_sensor_ = sensor; }
  void set_input_voltage_sensor(sensor::Sensor *sensor) { input_voltage_sensor_ = sensor; }
  void set_glow_plug_current_sensor(sensor::Sensor *sensor) { glow_plug_current_sensor_ = sensor; }
  void set_cooling_down_sensor(sensor::Sensor *sensor) { cooling_down_sensor_ = sensor; }
  void set_fan_voltage_sensor(sensor::Sensor *sensor) { fan_voltage_sensor_ = sensor; }
  void set_heat_exchanger_temp_sensor(sensor::Sensor *sensor) { heat_exchanger_temp_sensor_ = sensor; }
  void set_state_duration_sensor(sensor::Sensor *sensor) { state_duration_sensor_ = sensor; }
  void set_glow_plug_voltage_sensor(sensor::Sensor *sensor) { glow_plug_voltage_sensor_ = sensor; }
  void set_glow_plug_current_2_sensor(sensor::Sensor *sensor) { glow_plug_current_2_sensor_ = sensor; }
  void set_glow_plug_temperature_sensor(sensor::Sensor *sensor) { glow_plug_temperature_sensor_ = sensor; }

  // Setters for Short Frame Sensors
  void set_short_power_level_sensor(sensor::Sensor *sensor) { short_power_level_sensor_ = sensor; }
  void set_short_state_sensor(sensor::Sensor *sensor) { short_state_sensor_ = sensor; }
  void set_short_state_text_sensor(text_sensor::TextSensor *sensor) { short_frame_state_text_sensor_ = sensor; }

  // Public methods to control heater externally
  void set_heater_on(bool on);
  void set_heater_level(float level);

  void setup() override;
  void update() override;
  void dump_config() override;
  float get_setup_priority() const override;

 protected:
  uart::UARTComponent *uart_{nullptr};
  std::vector<uint8_t> frame_buffer_;
  uint32_t last_received_time_ = 0;
  void process_frame(const std::vector<uint8_t> &frame);

  // Sensor pointers for Long Frame
  sensor::Sensor *voltage_sensor_{nullptr};
  sensor::Sensor *temperature_sensor_{nullptr};
  sensor::Sensor *state_sensor_{nullptr};
  text_sensor::TextSensor *state_text_sensor_{nullptr};
  sensor::Sensor *power_level_sensor_{nullptr};
  sensor::Sensor *fan_speed_sensor_{nullptr};
  sensor::Sensor *pump_frequency_sensor_{nullptr};
  sensor::Sensor *input_voltage_sensor_{nullptr};
  sensor::Sensor *glow_plug_current_sensor_{nullptr};
  sensor::Sensor *cooling_down_sensor_{nullptr};
  sensor::Sensor *fan_voltage_sensor_{nullptr};
  sensor::Sensor *heat_exchanger_temp_sensor_{nullptr};
  sensor::Sensor *state_duration_sensor_{nullptr};
  sensor::Sensor *glow_plug_voltage_sensor_{nullptr};
  sensor::Sensor *glow_plug_current_2_sensor_{nullptr};
  sensor::Sensor *glow_plug_temperature_sensor_{nullptr};

  // Sensor pointers for Short Frame
  sensor::Sensor *short_power_level_sensor_{nullptr};
  sensor::Sensor *short_state_sensor_{nullptr};
  text_sensor::TextSensor *short_frame_state_text_sensor_{nullptr};

  // Internal State Variables
  bool heater_requested_on_ = false;
  uint8_t heater_level_percentage_ = 0;

  // Utility functions
  uint16_t read_uint16(const std::vector<uint8_t> &frame, size_t index);
  uint8_t read_uint8(const std::vector<uint8_t> &frame, size_t index);
};

}  // namespace vevorheater
}  // namespace esphome
