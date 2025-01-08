// vevorheater.cpp

#include "vevorheater.h"

#include "esphome/core/log.h"
#include "esphome/core/hal.h"
#include <cinttypes>

namespace esphome {
namespace vevorheater {

static const char *const TAG = "vevorheater.component";

void VevorHeater::setup() {
    ESP_LOGD(TAG, "VevorHeater setup");
    this->uart_->set_baud_rate(4800);
    this->last_received_time_ = millis(); // Initialize the timestamp
}

void VevorHeater::update() {
    bool received_data = false;

    // Read available bytes and add them to the frame buffer
    while (this->uart_->available()) {
        uint8_t data;
        this->uart_->read_byte(&data);
        this->frame_buffer_.push_back(data);
        this->last_received_time_ = millis(); // Update the timestamp
        // ESP_LOGD(TAG, "Received byte: 0x%02X", data);
        received_data = true;
    }

    // Check if the timeout has been exceeded and there is data in the buffer
    if (!this->frame_buffer_.empty()) {
        uint32_t current_time = millis();
        if ((current_time - this->last_received_time_) > 10) { // 10 ms timeout
            // ESP_LOGD(TAG, "Frame complete. Processing frame of %d bytes.", this->frame_buffer_.size());
            process_frame(this->frame_buffer_);
            this->frame_buffer_.clear(); // Clear the buffer for the next frame
        }
    }
}

void VevorHeater::process_frame(const std::vector<uint8_t> &frame) {
    // Implement your frame processing logic here
    // For example, you can parse the frame and update sensor values

    // Example: Log the entire frame
    std::string frame_str = "Frame: ";
    for (auto byte : frame) {
        char buf[5];
        snprintf(buf, sizeof(buf), " %02X ", byte);
        frame_str += buf;
    }
    ESP_LOGI(TAG, "%s", frame_str.c_str());

    // TODO: Add your specific frame parsing and handling here
}

void VevorHeater::dump_config() { 
    LOG_SENSOR("", "VevorHeater Sensor", this);
}

float VevorHeater::get_setup_priority() const { return setup_priority::DATA; }

}   // namespace vevorheater
}   // namespace esphome
