set board_preset $board_path/config/board_preset.tcl
source $sdk_path/fpga/lib/starting_point.tcl

create_bd_port -dir I -from 13 -to 0 adc_dat_a_i
create_bd_port -dir I -from 13 -to 0 adc_dat_b_i
create_bd_port -dir I adc_clk_p_i
create_bd_port -dir I adc_clk_n_i

create_bd_port -dir O -from 13 -to 0 dac_dat_a_o
create_bd_port -dir O -from 13 -to 0 dac_dat_b_o
create_bd_port -dir O dac_clk_o
create_bd_port -dir O dac_rst_o
create_bd_port -dir O dac_sel_o
create_bd_port -dir O dac_wrt_o

create_bd_cell -type ip -vlnv koheron:user:red_pitaya_adc_dac:1.0 adc_dac

connect_pins [get_bd_pins adc_dac/aclk] [get_bd_pins ps_0/FCLK_CLK0]
connect_pins [get_bd_pins adc_dac/adc_dat_a_i] [get_bd_ports adc_dat_a_i]
connect_pins [get_bd_pins adc_dac/adc_dat_b_i] [get_bd_ports adc_dat_b_i]
connect_pins [get_bd_pins adc_dac/adc_clk_p_i] [get_bd_ports adc_clk_p_i]
connect_pins [get_bd_pins adc_dac/adc_clk_n_i] [get_bd_ports adc_clk_n_i]

connect_pins [get_bd_pins adc_dac/dac_dat_a_o] [get_bd_ports dac_dat_a_o]
connect_pins [get_bd_pins adc_dac/dac_dat_b_o] [get_bd_ports dac_dat_b_o]
connect_pins [get_bd_pins adc_dac/dac_clk_o]   [get_bd_ports dac_clk_o]
connect_pins [get_bd_pins adc_dac/dac_rst_o]   [get_bd_ports dac_rst_o]
connect_pins [get_bd_pins adc_dac/dac_sel_o]   [get_bd_ports dac_sel_o]
connect_pins [get_bd_pins adc_dac/dac_wrt_o]   [get_bd_ports dac_wrt_o]

source $sdk_path/fpga/lib/ctl_sts.tcl
add_ctl_sts

create_bd_cell -type ip -vlnv xilinx.com:ip:dds_compiler:6.0 dds

set_property -dict [list \
  CONFIG.Parameter_Entry {Hardware_Parameters} \
  CONFIG.Output_Width {14} \
  CONFIG.Phase_Width {32} \
  CONFIG.Phase_Increment {Streaming} \
  CONFIG.Latency {6} \
  CONFIG.Output_Selection {Sine} \
] [get_bd_cells dds]

connect_pins [get_bd_pins dds/aclk] [get_bd_pins ps_0/FCLK_CLK0]

connect_pins [get_bd_pins dds/s_axis_phase_tdata] [ctl_pin dds_freq_hz]
connect_pins [get_bd_pins dds/s_axis_phase_tvalid] [get_constant_pin 1 1]

connect_pins [get_bd_pins dds/m_axis_data_tdata] [get_bd_pins adc_dac/dac_dat_a_i]

create_bd_cell -type ip -vlnv xilinx.com:ip:mult_gen:12.0 squarer
set_property -dict [list \
  CONFIG.PortAWidth {14} \
  CONFIG.PortBWidth {14} \
] [get_bd_cells squarer]

connect_pins [get_bd_pins squarer/CLK] [get_bd_pins ps_0/FCLK_CLK0]

connect_pins [get_bd_pins squarer/A] [get_bd_pins adc_dac/adc_dat_a_o]
connect_pins [get_bd_pins squarer/B] [get_bd_pins adc_dac/adc_dat_a_o]

create_bd_cell -type ip -vlnv xilinx.com:ip:c_accum:12.0 averager
set_property -dict [list \
  CONFIG.Input_Width {28} \
  CONFIG.Output_Width {32} \
  CONFIG.Implementation {DSP48} \
] [get_bd_cells averager]

connect_pins [get_bd_pins averager/CLK] [get_bd_pins ps_0/FCLK_CLK0]
connect_pins [get_bd_pins averager/B] [get_bd_pins squarer/P]

# Reset-Logik für den Averager (optional, hier einfach dauerhaft laufend oder über Register resetten)
# Um es einfach zu halten: Wir schreiben das Ergebnis direkt in das Status Register.
# HINWEIS: Ein einfacher Accumulator läuft über. Für eine echte Anwendung bräuchte man einen 
# "Moving Average" oder einen Reset-Counter.
# Da dies Tcl ist und wir keine komplexe Verilog-State-Machine schreiben wollen,
# nehmen wir hier den einfachsten Weg: Wir verbinden den Ausgang des Multipliers (geglättet wäre besser)
# oder, wenn Sie keine DSP-Kenntnisse haben, direkt den ADC an das Statusregister
# und machen das Averaging in Python/TypeScript (CPU-lastig aber einfach).

# Bessere Lösung für Tcl-Only: Wir verbinden den Squarer-Output (Energie) mit den oberen Bits an Status.
# Aber Achtung: Das flackert mit 2*Frequenz.
# Um es funktionierend zu machen, brauchen wir einen Filter.
# Wir nehmen hier an, dass Sie in Software mitteln (einfachste Implementierung).

# Verbindung zum Status Register (damit Python/Web es lesen kann)
# Wir nehmen die oberen 32 Bits vom Squarer Output (max 28 bit), gefüllt mit Nullen
# Einfachheitshalber: Wir lesen den rohen ADC Wert und mitteln im Web-Interface (App.ts).
# Das ist bei < 1 kHz Anzeigerate machbar.
connect_pins [sts_pin adc_amplitude] [get_bd_pins adc_dac/adc_dat_a_o] 

# Falls Sie die LEDs behalten wollen (als Debug):
create_bd_port -dir O -from 7 -to 0 led_o
# Zeige die oberen 8 Bits des ADC auf den LEDs an (Visuelles Feedback)
connect_port_pin led_o [get_slice_pin [get_bd_pins adc_dac/adc_dat_a_o] 13 6]