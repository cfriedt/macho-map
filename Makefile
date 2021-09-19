# Copyright (c) 2021 Friedt Professional Engineering Services, Inc
# SPDX-License-Identifier: MIT

CC := clang
CXX := clang++

CFLAGS :=
CPPFLAGS :=
CXXFLAGS :=
LDFLAGS :=

CPPFLAGS += -Iinclude

CFLAGS += -Wall -Wextra -Werror
CFLAGS += -Wno-unused-parameter
CFLAGS += -Wno-unused-function
CFLAGS += -O0 -g

CXXFLAGS += $(CFLAGS)

CFLAGS += -std=c11
CXXFLAGS += -std=c++14

LDFLAGS += -L.

TAG = macho_map
BIN = $(TAG)
EXE = $(TAG).exe
LIBNAME = lib$(TAG)

SRC = main.c zephyr.c macho_map.c
OBJ = $(SRC:.c=.o)
HDR := $(shell find * -name '*.h')

.PHONY: all info check clean $(BIN)_info $(LIBNAME)_info

all: $(EXE)

%.o: %.c $(HDR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ -c $<

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -Wl,-undefined,dynamic_lookup -o $@ $^

# TODO: create C source, start[] and end[] symbols from harvested symbol data
$(TAG).inc: $(BIN) gen_map.py
	./gen_map.py -o $@ -i $<

$(LIBNAME).dylib: $(TAG)_dyn.c $(TAG).inc
	$(CC) $(CPPFLAGS) $(CFLAGS) -shared -dynamiclib -o $@ $<

$(EXE): $(OBJ) $(LIBNAME).dylib
	$(CC) $(LDFLAGS) -o $@ $(OBJ) -l$(TAG)

info: $(BIN)_info $(LIBNAME)_info

$(BIN)_info: $(BIN)
	nm $<
	objdump --headers --full-contents $<

$(LIBNAME)_info: $(LIBNAME).dylib
	otool -vVT $<

check: $(EXE)
	./$<

clean:
	rm -Rf $(BIN) $(EXE) $(TAG).inc *.o *.dSYM/ *.dylib $(shell find * -name '__pycache__')
