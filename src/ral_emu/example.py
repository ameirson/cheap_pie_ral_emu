import os
from ral_emu import gen_reg_emu_file
from cheap_pie.parsers.ipyxact_parse import ipxact_parse

ipxact_xml = os.path.join(os.path.dirname(__file__), "ipxact_dim_example.xml")
reg_emu_file_base = r'reg_emu.txt'

# Temporary hal without hif is used for:
# 1. Building an initial emulation file automatically
# 2. Creating the cp_reg_emu - with actual addresses and validating the provided emulation
# (useful since it is normally manually edited)
hal = ipxact_parse(ipxact_xml)

# Emulation with Single Value = 0
reg_emu_file = reg_emu_file_base.replace('.txt', '_zero_val.txt')
gen_reg_emu_file(reg_emu_file, hal, val=0)

# Emulation with Single Value - from ipxact reset value, if exists, 0xBAD0C0DE if missing
# NOT YET SUPPORTED
# reg_emu_file = reg_emu_file_base.replace('.txt', '_reset_val.txt')
# gen_reg_emu_file(reg_emu_file, hal, val_reset=True, val_reset_missing=0xBAD0C0DE)

# Emulation with Multiple Random Values, using default range
reg_emu_file = reg_emu_file_base.replace('.txt', '_3_random_vals_default_range.txt')
emu_values_per_reg = 3
gen_reg_emu_file(reg_emu_file, hal, rand_vals_count=emu_values_per_reg)

# Emulation with Multiple Random Values, using provided range
reg_emu_file = reg_emu_file_base.replace('.txt', '_4_random_vals_specific_range.txt')
emu_values_per_reg = 4
gen_reg_emu_file(reg_emu_file, hal, rand_vals_count=emu_values_per_reg, rand_vals_min=0xF, rand_vals_max=0xFFFF)
