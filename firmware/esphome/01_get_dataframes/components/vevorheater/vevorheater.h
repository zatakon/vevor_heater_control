#pragma once

#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/core/preferences.h"
#include "esphome/components/sensor/sensor.h"
// #include "esphome/components/switch/switch.h"
#include "esphome/components/number/number.h"
#include "esphome/components/i2c/i2c.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace vevorheater {

class VevorHeater : public PollingComponent, public sensor::Sensor {
  public:
    // void set_sensor_speed(sensor::Sensor *speed) { sensor_speed_ = speed; }
    // void set_number_power(number::Number *power) { number_power_ = power; }
    void set_uart_bus(uart::UARTComponent *uart) { uart_ = uart; }

    void setup() override;
    void update() override;
    void dump_config() override;
    float get_setup_priority() const override;

  protected:
      // void uart_callback_();
      uart::UARTComponent *uart_{nullptr};
      std::vector<uint8_t> frame_buffer_;
      uint32_t last_received_time_ = 0;
      void process_frame(const std::vector<uint8_t> &frame);
};

}  // namespace vevorheater
}  // namespace esphome
