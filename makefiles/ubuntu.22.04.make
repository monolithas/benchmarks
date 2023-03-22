########################################
# configuration
########################################

OPTIONS := -O3 -fomit-frame-pointer
TARGET  := $(MAKECMDGOALS)
BENCH   := $(firstword $(subst -, ,$(TARGET)))

# Environment Variables
#    Options
#    	ADA_OPTS 
#    	C_OPTS   
#    	RUST_OPTS
#    	CPP_OPTS 
#   
#    Extended Options
#    	ADA_OPTS_EXT 
#    	C_OPTS_EXT   
#    	RUST_OPTS_EXT
#    	CPP_OPTS_EXT 
#   
#    Tools
#    	ADA_TOOL 
#    	C_TOOL   
#    	RUST_TOOL
#    	CPP_TOOL 

########################################
# targets
########################################

# --------------------------------------
# rust

%.rs: %.rust 
	-@mv $< $@

%.rust_run: %.rs 
	$(RUST_TOOL) $(RUST_OPTS) $< -o $@ $(RUST_OPTS_EXT)

# --------------------------------------
# ada

%.ada_run: %.ada
	gnatchop -r -w $< && $(ADA_TOOL) -pipe -Wall $(OPTIONS) $(ADA_OPTS) -f $(BENCH).adb -o $@ $(ADA_OPTS_EXT)

# --------------------------------------
# c

%.c_run: %.c 
	-$(C_TOOL) -pipe -Wall $(OPTIONS) $(C_OPTS) $< -o $@ $(C_OPTS_EXT)

# --------------------------------------
# cpp

%.cpp_run: %.cpp
	-$(CPP_TOOL) $(CPP_OPTS) $< -o $<.o && $(CPP_TOOL) $<.o -o $@ $(CPP_OPTS_EXT)
