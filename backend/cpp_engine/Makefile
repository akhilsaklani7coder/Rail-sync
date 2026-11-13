# RailSync C++ Engine Makefile
CXX ?= g++
CXXFLAGS = -std=c++17 -O3 -Wall -fPIC

ifeq ($(OS),Windows_NT)
    TARGET = railsync_engine.dll
    LDFLAGS = -shared -Wl,--out-implib,librailsync_engine.a
else
    TARGET = librailsync_engine.so
    LDFLAGS = -shared
endif

SRCS = core_logic.cpp
OBJS = $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $^

%.o: %.cpp core_logic.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) librailsync_engine.a
