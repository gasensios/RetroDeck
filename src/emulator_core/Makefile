CC ?= gcc
CFLAGS ?= -O3 -fPIC -Wall -Wextra
LDFLAGS ?= -shared -lm

SNES_SOURCES = $(wildcard snes/*.c)
SNES_TARGET = libretrosnes.so

MD_SRC = megadrive_bridge.c
MD_TARGET = libmegadrive_bridge.so

all: $(SNES_TARGET) $(MD_TARGET)

$(SNES_TARGET): $(SNES_SOURCES)
	$(CC) $(CFLAGS) -I snes $(SNES_SOURCES) -o $(SNES_TARGET) $(LDFLAGS)

$(MD_TARGET): $(MD_SRC)
	$(CC) $(CFLAGS) $(MD_SRC) -L. -lmegadrive -Wl,-rpath,'$$ORIGIN' -o $(MD_TARGET) $(LDFLAGS)

clean:
	rm -f $(SNES_TARGET) $(MD_TARGET)

.PHONY: all clean
