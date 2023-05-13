# cheap_pie_ral_emu - for from cheap_pie

A fork from original cheap_pie: https://github.com/bat52/cheap_pie
Many thanks for Marco Merlin for this awesome package !
See original README.md for operation of the original package (https://github.com/bat52/cheap_pie/blob/master/README.md)


This fork provides an addition hif transport layer for register access emulation & logging. 
The emulation is very basic, but useful for implementing pre-silicon flows without a real hardware emulation.
The emulation is based on providing a list of values for each register, these values will be used one after the other 
when a register read (hifread) is done. When the list is exhausted, the next read wil start over from the first value. 

# ral_emu
Implements register emulation which is then used in the new hif transport called cp_reg_emu.py

# Example using IP-Xact xml:
Full example can be found inside cp_ral_emu_test()

        reg_emu_file = r'emu_example.txt'
        ral_log_file = f'log_exmaple.txt'
        ipxact_xml = r'ipxact_example.xml'
    
        # Temporary hal without hif is used for:
        # 1. Building an initial emulation file automatically
        # 2. Creating the cp_reg_emu - with actual addresses and validating the provided emulation
        # (useful since it is normally manually edited)
        hal = ipxact_parse(ipxact_xml)
         
        # Generate Emulation File with Multiple, Random Values
        emu_values_per_reg = 3
        gen_reg_emu_file(reg_emu_file, hal, rand_vals_count=emu_values_per_reg)
    
        # Generate the register emulation hif 
        hif = cp_reg_emu(reg_emu_file, ral_log_file, hal=hal)
        hal = ipxact_parse(ipxact_xml, hif=hif)


# Generate of reg_emu_file:
Full example can also be found inside ral_emu.example.py

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

# Example of ral emulation log file
        # regname | [ts] | addr | lsb | width | access | value
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x1
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x31
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x61
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x1
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x31
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x61
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x1
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x31
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x61
        reg_dim_reg_2 [0] [0x00000000] 0 32 HW_READ  0x1
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x11
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x59
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0xC
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x11
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x59
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0xC
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x11
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x59
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0xC
        reg_dim_reg_with_dim [0] [0x00000004] 0 32 HW_READ  0x11
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x60
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x22
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x55
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x60
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x22
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x55
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x60
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x22
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x55
        reg_dim_reg_3 [0] [0x00000020] 0 32 HW_READ  0x60
