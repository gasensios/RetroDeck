CC ?= gcc
ARCH ?= $(shell uname -m)

# Base aggressive optimization flags for low-spec hardware (Raspberry Pi & PC)
CFLAGS ?= -O3 -fPIC -Wall -Wextra -fomit-frame-pointer -funroll-loops
LDFLAGS ?= -shared -lm

# Hardware-specific auto-tuning for ARM / Raspberry Pi
ifneq (,$(findstring arm,$(ARCH)))
    CFLAGS += -march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard
else ifneq (,$(findstring aarch64,$(ARCH)))
    CFLAGS += -march=armv8-a+crc -mtune=cortex-a72
endif

SNES_SOURCES = $(wildcard snes/*.c)
SNES_TARGET = libretrosnes.so

MD_SRC = megadrive_bridge.c
MD_TARGET = libmegadrive_bridge.so

NG_SRC = neogeo_bridge.c
NG_TARGET = libneogeo_bridge.so

all: $(SNES_TARGET) $(MD_TARGET) $(NG_TARGET)

$(SNES_TARGET): $(SNES_SOURCES)
	$(CC) $(CFLAGS) -I snes $(SNES_SOURCES) -o $(SNES_TARGET) $(LDFLAGS)

$(MD_TARGET): $(MD_SRC)
	$(CC) $(CFLAGS) $(MD_SRC) -L. -lmegadrive -Wl,-rpath,'$$ORIGIN' -o $(MD_TARGET) $(LDFLAGS)

$(NG_TARGET): $(NG_SRC)
	$(CC) $(CFLAGS) $(NG_SRC) fbalpha2012_neogeo_libretro.so -Wl,-rpath,'$$ORIGIN' -o $(NG_TARGET) $(LDFLAGS)

clean:
	rm -f $(SNES_TARGET) $(MD_TARGET) $(NG_TARGET)

.PHONY: all clean
