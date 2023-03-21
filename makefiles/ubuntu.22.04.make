########################################
# configuration
########################################

OPTIONS := -O3 -fomit-frame-pointer
TARGET  := $(MAKECMDGOALS)
BENCH   := $(firstword $(subst -, ,$(TARGET)))

# Options
# 	ADA_OPTS 
# 	C_OPTS   
# 	RUST_OPTS
# 	CPP_OPTS 

# Tools
# 	ADA_TOOL 
# 	C_TOOL   
# 	RUST_TOOL
# 	CPP_TOOL 

########################################
# targets
########################################

# --------------------------------------
# rust

%.rs: %.rust 
	-@mv $< $@

%.rust_run: %.rs 
	$(RUST_TOOL) $(RUST_OPTS) $< -o $@

# --------------------------------------
# ada

%.ada_run: %.ada
	gnatchop -r -w $< && $(ADA_TOOL) -pipe -Wall $(OPTIONS) $(ADA_OPTS) -f $(BENCH).adb -o $@

# --------------------------------------
# c

%.c_run: %.c 
	-$(C_TOOL) -pipe -Wall $(OPTIONS) $< -o $@ $(C_OPTS)

# --------------------------------------
# cpp

%.cpp_run: %.cpp
	-$(CPP_TOOL) -c -pipe $(OPTIONS) $(CPP_OPTS) $< -o $<.o && $(GXX) $<.o -o $@ 
