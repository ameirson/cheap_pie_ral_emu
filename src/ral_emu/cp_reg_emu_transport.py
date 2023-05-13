"""
cheap_pie Transport Layer that interfaces a RAL (Register Access Layer) Emulation
"""

import os
from ast import literal_eval
from cheap_pie.parsers.ipyxact_parse import ipxact_parse
from src.ral_emu.ral_emu import ral_emu_entry, ral_emu_build_emu_map, gen_reg_emu_file
import time


class cp_reg_emu(object):
    """ A transport mockup to use RAL Emulation """
    READ = True
    WRITE = False
    def __init__(self, ral_emu_file, ral_log_file = None, log_append = True, **kwargs):
        """
        :param kwargs
            reg_def_file = register definition file to be used for validating address / name
            reg_def_fmt  = format of reg_def_file for parsing. Default = ipxact
        """
        self.reg_emu = ral_emu_build_emu_map(ral_emu_file, **kwargs)
        self.reg_emu_file = ral_emu_file
        self.ral_log_file = ral_log_file
        if log_append:
            with open(self.ral_log_file, 'at') as fout:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                fout.write(f'Emulation Log Append @ {timestamp}\n')
        else:
            with open(self.ral_log_file, 'wt') as fout:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                fout.write(f'Emulation Log Create @ {timestamp}\n')

    # TODO - Support for Verify Regs after created
    def verify_regs(self, hal):
        pass

    def log_hif_access(self, read, addr_string, regname, value, offset = 0, bits = 32):
        with open(self.ral_log_file, 'at') as fout:
            access = 'HW_READ ' if read else 'HW_WRITE'
            value_str = f'0x{value:X}'
            timestamp = 0
            log = f'{regname} [{timestamp}] [{addr_string}] {offset} {bits} {access} {value_str}\n'
            fout.write(log)

    def hifread(self, addr="0x40000888"):

        # make sure string format is always the same
        if isinstance(addr, str):
            addr = int(literal_eval(addr))

        addrstr = f'0x{addr:08X}'

        if not addrstr in self.reg_emu.keys():
            raise ValueError(f'address {addrstr} not found. Consider adding '
                             f'"{register_addr2name(addrstr)}" to RAL Emu {self.reg_emu_file}')

        ret = self.reg_emu[addrstr].get()

        if self.ral_log_file:
            regname = self.reg_emu[addrstr].regname
            self.log_hif_access(self.READ, addrstr, regname, ret)

        return (ret)


    def hifwrite(self, addr="0x40000888", val="0x00000352"):
        # make sure string format is always the same
        if isinstance(addr, str):
            addr = int(literal_eval(addr))

        if isinstance(val, str):
            val = int(literal_eval(val))

        addrstr = f'0x{addr:08X}'

        if self.ral_log_file:
            regname = self.reg_emu[addrstr].regname
            self.log_hif_access(self.WRITE, addrstr, regname, val)

        if not addrstr in self.reg_emu.keys():
            print (f'hifwrite WARNING ! Address {addrstr} not found. Consider adding '
                             f'"{register_addr2name(addrstr)}" to RAL Emu {self.reg_emu_file}')
            print (f'Ignore If Write Only.')
            return

        self.reg_emu[addrstr].set(val)

        return int(val)

def get_ral_emu_hif(ral_emu_file, ral_log_file_suffix = None, ral_log_append = False):
    if not ral_log_file_suffix:
        ral_log_file_suffix = ''

    ral_log_file = ral_emu_file.removesuffix('.txt') + f'_ral_log{ral_log_file_suffix}.txt'
    hif = cp_reg_emu(ral_emu_file, ral_log_file, ral_log_append)

    return hif

def cp_ral_emu_test_read_repeats(hal, emu_values_per_reg):
    # Emulation Read - Values Traversed one after the other, and
    # Verify that read values are repeated for every emu_values_per_reg reads
    reg_read_count = 10
    fail_report = []
    for reg in hal:
        reg_read_values = []
        for i in range(reg_read_count):
            reg_read_values.append(f'{reg.getreg()}')

        expected_values = reg_read_values[0:emu_values_per_reg] * (int(reg_read_count / emu_values_per_reg))
        expected_values.extend(reg_read_values[0:reg_read_count % emu_values_per_reg])

        success = all([expected_values[i] == reg_read_values[i] for i in range(reg_read_count)])
        if not success:
            fail_report.append((f'FAIL - Reg Read Values SHOULD Repeat (every {emu_values_per_reg} in this test)\n'
                              f' expected: {expected_values}\n'
                              f' read    : {reg_read_values}'))
        values_str = ':'.join(reg_read_values)
        print(f'{reg.regname} READ = {values_str}')

    if fail_report:
        print('\n'.join(fail_report))
    else:
        print(f'PASS - Reg Read Values Repeat (every {emu_values_per_reg} in this test)')

def cp_ral_emu_test_write_is_to_all(hal, emu_values_per_reg):
    reg_read_count = 10
    write_value = 15

    fail_report = []

    # Write Single Value
    for reg in hal:
        reg.setreg(write_value)

    # All Reads Should be the same
    for reg in hal:
        reg_read_values = []
        for i in range(reg_read_count):
            reg_read_values.append(reg.getreg())

        expected_values = reg_read_count * [write_value]

        success = all([expected_values[i] == reg_read_values[i] for i in range(reg_read_count)])
        if not success:
            fail_report.append((f'FAIL - Reg Read Values SHOULD be SAME after single Write\n'
                              f' expected: {expected_values}\n'
                              f' read    : {reg_read_values}'))
        values_str = ':'.join([f'{v}' for v in reg_read_values])
        print(f'{reg.regname} READ = {values_str}')

    if fail_report:
        print('\n'.join(fail_report))
    else:
        print(f'PASS - Reg Read Values SAME after single Write')


def cp_ral_emu_test():
    reg_emu_file = r'emu_test.txt'
    ral_log_file = f'log_test.txt'
    ipxact_xml = os.path.join(os.path.dirname(__file__), 'ipxact_dim_example.xml')

    # Temporary hal without hif is used for:
    # 1. Building a test emulation file automatically
    # 2. Creating the cp_reg_emu - with actual addresses and validating the provided emulation
    # (useful since it is normally manually edited)
    hal = ipxact_parse(ipxact_xml)

    # Single Value Emulation
    # gen_reg_emu_file(reg_emu_file, hal, val=0)

    # Multiple - Random Values Emulation
    emu_values_per_reg = 3
    gen_reg_emu_file(reg_emu_file, hal, rand_vals_count=emu_values_per_reg)

    hif = cp_reg_emu(reg_emu_file, ral_log_file, hal=hal)
    hal = ipxact_parse(ipxact_xml, hif=hif)

    # Verify that read values are repeated for every emu_values_per_reg reads
    cp_ral_emu_test_read_repeats(hal, emu_values_per_reg)

    # Verify that after single write all are the same
    cp_ral_emu_test_write_is_to_all(hal, emu_values_per_reg)




if __name__ == '__main__':
    cp_ral_emu_test()
    pass