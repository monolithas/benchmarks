########################################
# configuration
########################################

COPTS  := -O3 -fomit-frame-pointer
TARGET := $(MAKECMDGOALS)
BENCH  := $(firstword $(subst -, ,$(TARGET)))

########################################
# targets
########################################

# --------------------------------------
# rust

%.rs: %.rust 
	-@mv $< $@

%.rust_run: %.rs 
	$(RUST) $(RUSTOPTS) $< -o $@

# --------------------------------------
# ada

%.ada_run: %.ada
	gnatchop -r -w $< && $(ADA) -pipe -Wall $(COPTS) $(ADAOPTS) -f $(BENCH).adb -o $@

# --------------------------------------
# c

%.c_run: %.c 
	-$(GCC) -pipe -Wall $(COPTS) $< -o $@ $(GCCOPTS)

# --------------------------------------
# cpp

%.cpp_run: %.cpp
	-$(GXX) -c -pipe $(COPTS) $(GXXOPTS) $< -o $<.o && $(GXX) $<.o -o $@ $(GXXLDOPTS) 
