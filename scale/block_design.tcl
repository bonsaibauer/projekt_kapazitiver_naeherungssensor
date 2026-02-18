source $board_path/config/ports.tcl

# Add PS and AXI interconnect
set board_preset $board_path/config/board_preset.tcl
source $sdk_path/fpga/lib/starting_point.tcl

# Add Red Pitaya ADC / DAC subsystem
source $sdk_path/fpga/lib/redp_adc_dac.tcl
set adc_dac_name adc_dac
add_redp_adc_dac $adc_dac_name

# Reset synchronized to ADC clock
set adc_clk $adc_dac_name/adc_clk
set rst_adc_clk_name proc_sys_reset_adc_clk

cell xilinx.com:ip:proc_sys_reset:5.0 $rst_adc_clk_name {} {
  ext_reset_in $ps_name/FCLK_RESET0_N
  slowest_sync_clk $adc_clk
}

# Add control / status registers on ADC clock domain
source $sdk_path/fpga/lib/ctl_sts.tcl
add_ctl_sts $adc_clk $rst_adc_clk_name/peripheral_aresetn

# DDS for excitation signal
cell xilinx.com:ip:dds_compiler:6.0 dds {
  Parameter_Entry Hardware_Parameters
  Output_Width 14
  Phase_Width 32
  Phase_Increment Streaming
  Latency 6
  Output_Selection Sine
} {
  aclk $adc_clk
  s_axis_phase_tdata [ctl_pin dds_freq_hz]
  s_axis_phase_tvalid [get_constant_pin 1 1]
}

# Drive DAC1 with DDS output
connect_pins [get_bd_pins dds/m_axis_data_tdata] [get_bd_pins adc_dac/dac1]

# Expose ADC1 raw value to status register for software averaging/calibration
connect_pins [sts_pin adc_amplitude] [get_bd_pins adc_dac/adc1]

# Debug LEDs: show upper ADC bits
connect_port_pin led_o [get_slice_pin [get_bd_pins adc_dac/adc1] 13 6]
