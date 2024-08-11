CC=gcc
CFLAGS=-Iinclude -Wall -Wextra -g
DEPS=include/scanner.h include/alert.h include/config.h include/utils.h
OBJ=main.o scanner.o alert.o config.o utils.o

# Rule to compile each .c file into a .o object file
%.o: src/%.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

# Rule to link all .o files into the final executable
device_manager: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

# Phony target to clean up generated files
.PHONY: clean
clean:
	rm -f *.o device_manager
