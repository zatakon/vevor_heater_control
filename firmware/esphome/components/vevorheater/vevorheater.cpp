// vevorheater.cpp
#include "vevorheater.h"

#include "esphome/core/log.h"
#include "esphome/core/hal.h"
#include <cinttypes>

uint8_t calculateChecksum(const std::vector<uint8_t>& frame) {
    // Ensure the frame has at least 3 bytes:
    // - Byte 0: Identifier (0xAA)
    // - Byte 1: Device ID
    // - Byte 2: Start of data
    // - Byte (N-1): Checksum
    if (frame.size() < 4) {
        return 0;
    }
    uint32_t sum = 0;
    // Sum all bytes from index 2 to index (size - 2) inclusive
    for (size_t i = 2; i < frame.size() - 1; ++i) {
        sum += frame[i];
    }
    // Calculate checksum as sum modulo 256
    uint8_t checksum = static_cast<uint8_t>(sum % 256);
    return checksum;
}

namespace esphome {
namespace vevorheater {

static const char *const TAG = "vevorheater.component";

void VevorHeater::setup() {
  ESP_LOGD(TAG, "VevorHeater setup");
  if (!this->uart_) {
    ESP_LOGE(TAG, "UART bus not set!");
    return;
  }
  this->uart_->set_baud_rate(4800);
  this->last_received_time_ = millis(); // Initialize the timestamp

  this->state_ = VevorHeaterState::OFF;
  this->heater_requested_on_ = false;
  this->heater_level_percentage_ = 100;
  this->last_send_time = millis();
}

void VevorHeater::update() {
  bool received_data = false;

  // Read available bytes and add them to the frame buffer
  while (this->uart_->available()) {
    uint8_t data;
    this->uart_->read_byte(&data);
    this->frame_buffer_.push_back(data);
    this->last_received_time_ = millis(); // Update the timestamp
    ESP_LOGD(TAG, "Received byte: 0x%02X", data);
    received_data = true;
  }

  // Check if the timeout has been exceeded and there is data in the buffer
  if (!this->frame_buffer_.empty()) {
    uint32_t current_time = millis();
    if ((current_time - this->last_received_time_) > 10) { // 10 ms timeout
      ESP_LOGD(TAG, "Frame complete. Processing frame of %d bytes.", this->frame_buffer_.size());
      process_frame(this->frame_buffer_);
      this->frame_buffer_.clear(); // Clear the buffer for the next frame
    }
  }

  uint32_t now = millis();
  if (now - last_send_time >= 1000) {
    last_send_time = now;
    
    std::vector<uint8_t> short_frame;
    // if heater is requested to be off
    if (!heater_requested_on_) {
      if (this->state_ == VevorHeaterState::OFF) {
        return;
      } else if (this->state_ != VevorHeaterState::STOPPING_COOLING) {
        // Send short frame to turn heater OFF
        short_frame.push_back(0xAA); 
        short_frame.push_back(0x66); 
        short_frame.push_back(0x06); 
        short_frame.push_back(0x0B);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(10);
        short_frame.push_back(0x05);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        uint8_t checksum = calculateChecksum(short_frame);
        short_frame.push_back(checksum);
        
        this->uart_->write_array(short_frame.data(), short_frame.size());
        ESP_LOGD(TAG, "Sent short frame to set level %u%%", this->heater_level_percentage_);
      } else {
        // Send short frame to keep heater shutting OFF
        short_frame.push_back(0xAA); 
        short_frame.push_back(0x66); 
        short_frame.push_back(0x02); 
        short_frame.push_back(0x0B);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(10);
        short_frame.push_back(0x02);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        uint8_t checksum = calculateChecksum(short_frame);
        short_frame.push_back(checksum);
        
        this->uart_->write_array(short_frame.data(), short_frame.size());
        ESP_LOGD(TAG, "Sent short frame to set level %u%%", this->heater_level_percentage_);
      }
    // if heater is requested to be on
    } else {
      if (this->state_ == VevorHeaterState::OFF) {
        // Send short frame to turn heater ON
        short_frame.push_back(0xAA); 
        short_frame.push_back(0x66); 
        short_frame.push_back(0x06); 
        short_frame.push_back(0x0B);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(this->heater_level_percentage_/10);
        short_frame.push_back(0x06);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        uint8_t checksum = calculateChecksum(short_frame);
        short_frame.push_back(checksum);

        this->uart_->write_array(short_frame.data(), short_frame.size());
        ESP_LOGD(TAG, "Sent short frame to turn heater ON with level %u%%", this->heater_level_percentage_);
      } else {
        // Send short frame to keep heater ON
        short_frame.push_back(0xAA); 
        short_frame.push_back(0x66); 
        short_frame.push_back(0x02); 
        short_frame.push_back(0x0B);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(this->heater_level_percentage_/10);
        short_frame.push_back(0x08);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        short_frame.push_back(0x00);
        uint8_t checksum = calculateChecksum(short_frame);
        short_frame.push_back(checksum);
        
        this->uart_->write_array(short_frame.data(), short_frame.size());
        ESP_LOGD(TAG, "Sent short frame to set level %u%%", this->heater_level_percentage_);
      }
    }
  }

  // Handle Heater Control based on internal state
//   if (heater_requested_on_) {
//         // Send short frame once per second with current heater level
//         static uint32_t last_send_time = 0;
//         uint32_t now = millis();
//         if (now - last_send_time >= 1000) { // 1 second interval
//         last_send_time = now;
//         std::vector<uint8_t> short_frame;

//         // TODO: Populate with appropriate short frame data based on heater_level_percentage_
//         // Example short frame structure (replace with actual frame format)
//         short_frame.push_back(0xAA); 
//         short_frame.push_back(0x66); 
//         short_frame.push_back(0x02); 
//         short_frame.push_back(0x0B);
//         short_frame.push_back(0x00);
//         short_frame.push_back(0x00);
//         short_frame.push_back(0x00);
//         short_frame.push_back(0x00);
//         short_frame.push_back(this->heater_level_percentage_/10);
//         short_frame.push_back(0x08);
//         short_frame.push_back(0x00);
//         short_frame.push_back(0x00);
//         short_frame.push_back(0x00);
//         uint8_t checksum = calculateChecksum(short_frame);
//         short_frame.push_back(checksum);

//         this->uart_->write_array(short_frame.data(), short_frame.size());
//         ESP_LOGD(TAG, "Sent short frame to turn heater ON with level %u%%", this->heater_level_percentage_);
// }
//   } else {
//     // Heater is requested to be off, but continue sending frames until main unit confirms off
//     // Check the state_sensor_ to determine if heater is still on
//     if (this->state_sensor_ && this->state_sensor_->state != 0) { // Assuming 0 is OFF
//       std::vector<uint8_t> short_frame;

//       short_frame.push_back(0xAA); 
//       short_frame.push_back(0x66); 
//       short_frame.push_back(0x02); 
//       short_frame.push_back(0x0B);
//       short_frame.push_back(0x00);
//       short_frame.push_back(0x00);
//       short_frame.push_back(0x00);
//       short_frame.push_back(0x00);
//       short_frame.push_back(this->heater_level_percentage_/10);
//       short_frame.push_back(0x02);
//       short_frame.push_back(0x00);
//       short_frame.push_back(0x00);
//       short_frame.push_back(0x00);
//       uint8_t checksum = calculateChecksum(short_frame);
//       short_frame.push_back(checksum);

//       this->uart_->write_array(short_frame.data(), short_frame.size());
//       ESP_LOGD(TAG, "Sent short frame to turn heater OFF");
//     }
//   }
}

void VevorHeater::process_frame(const std::vector<uint8_t> &frame) {
  if (frame.empty()) {
    ESP_LOGW(TAG, "Empty frame received.");
    return;
  }

  // Determine frame type based on length field (byte 3)
  uint8_t length_field = 0;
  if (frame.size() > 3) {
    length_field = frame[3];
  } else {
    ESP_LOGW(TAG, "Frame too short to determine type.");
    return;
  }

  if (length_field == 0x0B && frame.size() >= 15) {
    // Short Frame: controller -> main unit
    ESP_LOGD(TAG, "Processing Short Frame");
    
    // Byte 8: Power Level (1-10)
    uint8_t power_level = read_uint8(frame, 8)*10;
    if (this->short_power_level_sensor_) {
      this->short_power_level_sensor_->publish_state(power_level);
      ESP_LOGD(TAG, "Short Frame - Power Level: %u%%", power_level);
    }

    // Byte 9: Requested State (0x02: off, 0x06: start, 0x08: running)
    uint8_t requested_state = read_uint8(frame, 9);
    if (this->short_state_sensor_) {
      this->short_state_sensor_->publish_state(requested_state);
      ESP_LOGD(TAG, "Short Frame - Requested State: 0x%02X", requested_state);
    }
    if (this->short_frame_state_text_sensor_) {
      if (requested_state == 0x02) {
        this->short_frame_state_text_sensor_->publish_state("Off");
      } else if (requested_state == 0x05) {
        this->short_frame_state_text_sensor_->publish_state("Set Off");
      } else if (requested_state == 0x06) {
        this->short_frame_state_text_sensor_->publish_state("Set On");
      } else if (requested_state == 0x08) {
        this->short_frame_state_text_sensor_->publish_state("Running");
      } else {
        this->short_frame_state_text_sensor_->publish_state("Unknown");
      }
    }

    // Byte 14: Checksum (1-255)
    uint8_t checksum = read_uint8(frame, 14);
    // Optionally, implement checksum verification here

  }
  else if (length_field == 0x33 && frame.size() >= 56) {
    // Long Frame: main unit -> controller
    ESP_LOGD(TAG, "Processing Long Frame");

    // Existing Long Frame processing logic...
    // [Keep all existing code here without changes]

    // Byte 4: Heater Enabled? (0-1)
    uint8_t heater_enabled = read_uint8(frame, 4);
    if (this->voltage_sensor_) { // Example: Use heater_enabled to influence voltage sensor
      // Implement logic if needed
      ESP_LOGD(TAG, "Long Frame - Heater Enabled: %u", heater_enabled);
    }

    // Byte 5: State (0x00: off, 0x01: glow plug pre heat, 0x02: ignited, 0x03: stable combustion, 0x04: stoping, cooling) [state]
    uint8_t state = read_uint8(frame, 5);
    this->state_ = static_cast<VevorHeaterState>(state);
    if (this->state_sensor_) {
      this->state_sensor_->publish_state(state);
      ESP_LOGD(TAG, "Long Frame - State: %u", state);
    }
    if (this->state_text_sensor_) {
      if (state == 0x00) {
        this->state_text_sensor_->publish_state("Off");
      } else if (state == 0x01) {
        this->state_text_sensor_->publish_state("Glow Plug Pre Heat");
      } else if (state == 0x02) {
        this->state_text_sensor_->publish_state("Ignited");
      } else if (state == 0x03) {
        this->state_text_sensor_->publish_state("Stable Combustion");
      } else if (state == 0x04) {
        this->state_text_sensor_->publish_state("Stopping, Cooling");
      } else {
        this->state_text_sensor_->publish_state("Unknown");
      }
    }

    // Byte 6: Power Level (0x01-0x0A)
    uint8_t power_level = read_uint8(frame, 6)*10;
    if (this->power_level_sensor_) {
      this->power_level_sensor_->publish_state(power_level);
      ESP_LOGD(TAG, "Long Frame - Power Level: %u%%", power_level);
    }

    // Byte 11: Input Voltage [V * 10] (153-158)
    uint8_t input_voltage_raw = read_uint8(frame, 11);
    float input_voltage = input_voltage_raw / 10.0;
    if (this->input_voltage_sensor_) {
      this->input_voltage_sensor_->publish_state(input_voltage);
      ESP_LOGD(TAG, "Long Frame - Input Voltage: %.1f V", input_voltage);
    }

    // Byte 13: Glow Plug Current [A] (0-12)
    uint8_t glow_plug_current = read_uint8(frame, 13);
    if (this->glow_plug_current_sensor_) {
      this->glow_plug_current_sensor_->publish_state(glow_plug_current);
      ESP_LOGD(TAG, "Long Frame - Glow Plug Current: %u A", glow_plug_current);
    }

    // Byte 14: Cooling Down [0/1]
    uint8_t cooling_down = read_uint8(frame, 14);
    if (this->cooling_down_sensor_) {
      this->cooling_down_sensor_->publish_state(cooling_down);
      ESP_LOGD(TAG, "Long Frame - Cooling Down: %u", cooling_down);
    }

    // Byte 15: Fan Voltage? Some temperature? [V] (0-16)
    uint8_t fan_voltage_raw = read_uint8(frame, 15);
    float fan_voltage = fan_voltage_raw / 1.0; // Assuming V
    if (this->fan_voltage_sensor_) {
      this->fan_voltage_sensor_->publish_state(fan_voltage);
      ESP_LOGD(TAG, "Long Frame - Fan Voltage: %.1f V", fan_voltage);
    }

    // Bytes 16-17: Heat Exchanger Temperature [°C * 100] (480-1630)
    int16_t heat_exchanger_temp_raw = read_uint16(frame, 16);
    float heat_exchanger_temp = heat_exchanger_temp_raw / 10.0;
    if (this->heat_exchanger_temp_sensor_) {
      this->heat_exchanger_temp_sensor_->publish_state(heat_exchanger_temp);
      ESP_LOGD(TAG, "Long Frame - Heat Exchanger Temperature: %.2f °C", heat_exchanger_temp);
    }

    // Bytes 20-21: State Duration [s] (0-325)
    uint16_t state_duration_raw = read_uint16(frame, 20);
    if (this->state_duration_sensor_) {
      this->state_duration_sensor_->publish_state(state_duration_raw);
      ESP_LOGD(TAG, "Long Frame - State Duration: %us", state_duration_raw);
    }

    // Byte 23: Pump Frequency [Hz * 10] (0-51)
    uint8_t pump_freq_raw = read_uint8(frame, 23);
    float pump_frequency = pump_freq_raw / 10.0;
    if (this->pump_frequency_sensor_) {
      this->pump_frequency_sensor_->publish_state(pump_frequency);
      ESP_LOGD(TAG, "Long Frame - Pump Frequency: %.1f Hz", pump_frequency);
    }

    // Bytes 24-27: Glow Plug Voltage/Current/Temperature (0-66, 0-86, 0-56, 0-12)
    uint8_t glow_plug_voltage = read_uint8(frame, 24);
    uint8_t glow_plug_current_2 = read_uint8(frame, 25);
    uint8_t glow_plug_temperature = read_uint8(frame, 26);
    uint8_t glow_plug_misc = read_uint8(frame, 27);

    if (this->glow_plug_voltage_sensor_) {
      this->glow_plug_voltage_sensor_->publish_state(glow_plug_voltage);
      ESP_LOGD(TAG, "Long Frame - Glow Plug Voltage: %u V", glow_plug_voltage);
    }

    if (this->glow_plug_current_2_sensor_) {
      this->glow_plug_current_2_sensor_->publish_state(glow_plug_current_2);
      ESP_LOGD(TAG, "Long Frame - Glow Plug Current 2: %u A", glow_plug_current_2);
    }

    if (this->glow_plug_temperature_sensor_) {
      this->glow_plug_temperature_sensor_->publish_state(glow_plug_temperature);
      ESP_LOGD(TAG, "Long Frame - Glow Plug Temperature: %u °C", glow_plug_temperature);
    }

    // Bytes 28-29: Fan Speed [rpm] (0-3939)
    uint16_t fan_speed_raw = read_uint16(frame, 28);
    if (this->fan_speed_sensor_) {
      this->fan_speed_sensor_->publish_state(fan_speed_raw);
      ESP_LOGD(TAG, "Long Frame - Fan Speed: %u RPM", fan_speed_raw);
    }

    // Bytes 52-53: Something glow plug related (0-420)
    uint16_t glow_plug_related = read_uint16(frame, 52);
    // Implement if needed

    // Byte 55: Checksum (1-254)
    uint8_t checksum = read_uint8(frame, 55);
    // Optionally, implement checksum verification here

  }
  else {
    ESP_LOGW(TAG, "Unknown frame type or incorrect frame length. Length field: 0x%02X, Frame size: %d", length_field, frame.size());
  }
}

void VevorHeater::dump_config() { 
  LOG_SENSOR("", "Vevor Heater Voltage", this->voltage_sensor_);
  LOG_SENSOR("", "Vevor Heater Temperature", this->temperature_sensor_);
  LOG_SENSOR("", "Vevor Heater State", this->state_sensor_);
  LOG_SENSOR("", "Vevor Heater Power Level", this->power_level_sensor_);
  LOG_SENSOR("", "Vevor Heater Fan Speed", this->fan_speed_sensor_);
  LOG_SENSOR("", "Vevor Heater Pump Frequency", this->pump_frequency_sensor_);
  LOG_SENSOR("", "Vevor Heater Input Voltage", this->input_voltage_sensor_);
  LOG_SENSOR("", "Vevor Heater Glow Plug Current", this->glow_plug_current_sensor_);
  LOG_SENSOR("", "Vevor Heater Cooling Down", this->cooling_down_sensor_);
  LOG_SENSOR("", "Vevor Heater Fan Voltage", this->fan_voltage_sensor_);
  LOG_SENSOR("", "Vevor Heater Heat Exchanger Temperature", this->heat_exchanger_temp_sensor_);
  LOG_SENSOR("", "Vevor Heater State Duration", this->state_duration_sensor_);
  LOG_SENSOR("", "Vevor Heater Glow Plug Voltage", this->glow_plug_voltage_sensor_);
  LOG_SENSOR("", "Vevor Heater Glow Plug Current 2", this->glow_plug_current_2_sensor_);
  LOG_SENSOR("", "Vevor Heater Glow Plug Temperature", this->glow_plug_temperature_sensor_);

  LOG_SENSOR("", "Vevor Heater Short Frame Power Level", this->short_power_level_sensor_);
  LOG_SENSOR("", "Vevor Heater Short Frame State", this->short_state_sensor_);
  
  // No switch and number to dump
}

float VevorHeater::get_setup_priority() const { return setup_priority::DATA; }

// Public method to set heater on/off
void VevorHeater::set_heater_on() {
  this->heater_requested_on_ = true;
  ESP_LOGD(TAG, "Heater set to ON");
}

void VevorHeater::set_heater_off() {
  this->heater_requested_on_ = false;
  ESP_LOGD(TAG, "Heater set to OFF");
}

// Public method to set heater level
void VevorHeater::set_heater_level(float level) {
  uint8_t new_level = static_cast<uint8_t>(level);
  if (this->heater_level_percentage_ == new_level) {
    return; // No change
  }
  this->heater_level_percentage_ = new_level;
  ESP_LOGD(TAG, "Heater level set to %u%%", this->heater_level_percentage_);
}

uint16_t VevorHeater::read_uint16(const std::vector<uint8_t> &frame, size_t index) {
  if (index + 1 >= frame.size()) {
    return 0;
  }
  return (static_cast<uint16_t>(frame[index]) << 8) | frame[index + 1];
}

uint8_t VevorHeater::read_uint8(const std::vector<uint8_t> &frame, size_t index) {
  if (index >= frame.size()) {
    return 0;
  }
  return frame[index];
}

}   // namespace vevorheater
}   // namespace esphome
