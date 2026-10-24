/*
 * Mega Drive / Genesis Bridge for RetroSNES/RetroMultiSystem.
 * Bridges Genesis-Plus-GX libretro core to a simple high-level API.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

// Libretro headers/definitions
struct retro_game_info {
   const char *path;
   const void *data;
   size_t      size;
   const char *meta;
};

typedef bool (*retro_environment_t)(unsigned cmd, void *data);
typedef void (*retro_video_refresh_t)(const void *data, unsigned width, unsigned height, size_t pitch);
typedef void (*retro_audio_sample_t)(int16_t left, int16_t right);
typedef size_t (*retro_audio_sample_batch_t)(const int16_t *data, size_t frames);
typedef void (*retro_input_poll_t)(void);
typedef int16_t (*retro_input_state_t)(unsigned port, unsigned device, unsigned index, unsigned id);

// Functions from Genesis-Plus-GX core
extern void retro_set_environment(retro_environment_t);
extern void retro_set_video_refresh(retro_video_refresh_t);
extern void retro_set_audio_sample(retro_audio_sample_t);
extern void retro_set_audio_sample_batch(retro_audio_sample_batch_t);
extern void retro_set_input_poll(retro_input_poll_t);
extern void retro_set_input_state(retro_input_state_t);
extern void retro_init(void);
extern void retro_deinit(void);
extern bool retro_load_game(const struct retro_game_info *game);
extern void retro_unload_game(void);
extern void retro_reset(void);
extern void retro_run(void);
extern size_t retro_serialize_size(void);
extern bool retro_serialize(void *data, size_t size);
extern bool retro_unserialize(const void *data, size_t size);
extern void* retro_get_memory_data(unsigned id);
extern size_t retro_get_memory_size(unsigned id);

#define RETRO_MEMORY_SAVE_RAM 0

// Bridge state
static uint16_t joypad_state[2] = {0, 0};
static uint8_t frame_rgbx[1024 * 512 * 4];
static int current_width = 320;
static int current_height = 224;
static bool is_game_loaded = false;

static bool bridge_env(unsigned cmd, void *data) {
    if (cmd == 10) { // RETRO_ENVIRONMENT_SET_PIXEL_FORMAT
        return true; // We accept RGB565
    }
    return false;
}

static void bridge_video(const void *data, unsigned width, unsigned height, size_t pitch) {
    if (!data) return;
    current_width = width;
    current_height = height;

    const uint8_t *src_bytes = (const uint8_t*)data;
    uint8_t *dst = frame_rgbx;

    for (unsigned y = 0; y < height; y++) {
        const uint16_t *src_row = (const uint16_t*)(src_bytes + y * pitch);
        for (unsigned x = 0; x < width; x++) {
            uint16_t pixel = src_row[x];
            // RGB565 -> RGB8888
            uint8_t r = (pixel >> 11) & 0x1F;
            uint8_t g = (pixel >> 5) & 0x3F;
            uint8_t b = pixel & 0x1F;

            dst[0] = (r << 3) | (r >> 2); // R
            dst[1] = (g << 2) | (g >> 4); // G
            dst[2] = (b << 3) | (b >> 2); // B
            dst[3] = 255;                 // X/A
            dst += 4;
        }
    }
}

// Audio buffer for 16-bit stereo PCM
#define AUDIO_BUF_SAMPLES 16384
static int16_t audio_buffer[AUDIO_BUF_SAMPLES];
static int audio_sample_count = 0;

static void bridge_audio_sample(int16_t left, int16_t right) {
    if (audio_sample_count + 2 <= AUDIO_BUF_SAMPLES) {
        audio_buffer[audio_sample_count++] = left;
        audio_buffer[audio_sample_count++] = right;
    }
}

static size_t bridge_audio_batch(const int16_t *data, size_t frames) {
    if (!data || frames == 0) return 0;
    int samples = (int)frames * 2;
    if (audio_sample_count + samples <= AUDIO_BUF_SAMPLES) {
        memcpy(audio_buffer + audio_sample_count, data, samples * sizeof(int16_t));
        audio_sample_count += samples;
    }
    return frames;
}
static void bridge_input_poll(void) {}

static int16_t bridge_input_state(unsigned port, unsigned device, unsigned index, unsigned id) {
    if (port > 1 || device != 1) return 0;
    return (joypad_state[port] & (1 << id)) ? 1 : 0;
}

// Public API for Python ctypes
bool md_init(void) {
    audio_sample_count = 0;
    retro_set_environment(bridge_env);
    retro_set_video_refresh(bridge_video);
    retro_set_audio_sample(bridge_audio_sample);
    retro_set_audio_sample_batch(bridge_audio_batch);
    retro_set_input_poll(bridge_input_poll);
    retro_set_input_state(bridge_input_state);

    retro_init();
    return true;
}

void md_deinit(void) {
    if (is_game_loaded) {
        retro_unload_game();
        is_game_loaded = false;
    }
    retro_deinit();
}

bool md_load_rom(const char *path, const uint8_t *data, size_t size) {
    if (is_game_loaded) {
        retro_unload_game();
        is_game_loaded = false;
    }

    struct retro_game_info info;
    info.path = path;
    info.data = data;
    info.size = size;
    info.meta = NULL;

    is_game_loaded = retro_load_game(&info);
    if (is_game_loaded) {
        audio_sample_count = 0;
    }
    return is_game_loaded;
}

void md_run_frame(void) {
    if (is_game_loaded) {
        retro_run();
    }
}

void md_reset(void) {
    if (is_game_loaded) {
        retro_reset();
    }
}

void md_get_frame_info(int *w, int *h) {
    if (w) *w = current_width;
    if (h) *h = current_height;
}

const uint8_t* md_get_pixels(void) {
    return frame_rgbx;
}

int md_get_samples(int16_t *out_data, int max_samples) {
    if (!out_data || max_samples <= 0) return 0;
    int count = audio_sample_count;
    if (count > max_samples) count = max_samples;
    if (count > 0) {
        memcpy(out_data, audio_buffer, count * sizeof(int16_t));
        if (audio_sample_count > count) {
            memmove(audio_buffer, audio_buffer + count, (audio_sample_count - count) * sizeof(int16_t));
            audio_sample_count -= count;
        } else {
            audio_sample_count = 0;
        }
    }
    return count;
}

/*
 * Button IDs (Libretro standard):
 * 0: B, 1: Y (MD A), 2: SELECT (MD MODE), 3: START
 * 4: UP, 5: DOWN, 6: LEFT, 7: RIGHT
 * 8: A (MD C), 9: X, 10: L (MD Y), 11: R (MD Z)
 */
void md_set_button(int player, int button_id, bool pressed) {
    if (player < 1 || player > 2) return;
    int p = player - 1;
    if (pressed) {
        joypad_state[p] |= (1 << button_id);
    } else {
        joypad_state[p] &= ~(1 << button_id);
    }
}

int md_save_state(uint8_t *buffer, size_t max_size) {
    if (!is_game_loaded) return 0;
    size_t sz = retro_serialize_size();
    if (sz == 0 || sz > max_size) return 0;
    if (retro_serialize(buffer, sz)) {
        return (int)sz;
    }
    return 0;
}

bool md_load_state(const uint8_t *buffer, size_t size) {
    if (!is_game_loaded) return false;
    return retro_unserialize(buffer, size);
}

int md_save_sram(uint8_t *buffer, size_t max_size) {
    void *ram = retro_get_memory_data(RETRO_MEMORY_SAVE_RAM);
    size_t sz = retro_get_memory_size(RETRO_MEMORY_SAVE_RAM);
    if (!ram || sz == 0 || sz > max_size) return 0;
    memcpy(buffer, ram, sz);
    return (int)sz;
}

bool md_load_sram(const uint8_t *buffer, size_t size) {
    void *ram = retro_get_memory_data(RETRO_MEMORY_SAVE_RAM);
    size_t sz = retro_get_memory_size(RETRO_MEMORY_SAVE_RAM);
    if (!ram || sz == 0 || sz < size) return false;
    memcpy(ram, buffer, size);
    return true;
}
