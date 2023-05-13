from cheap_pie.parsers.ipyxact_parse import ipxact_parse

from collections import namedtuple
from ast import literal_eval
from shutil import copyfile
import os


class ral_emu_entry():
    def __init__(self, addr, regname, values, next):
        self.addr = addr
        self.regname = regname
        self.values = values
        self.next = next

    def __repr__(self):
        values_hex = [f'0x{v:08X}' for v in self.values]
        values_str = ':'.join(values_hex)
        return f'0x{self.addr:08X} {self.next} {values_str}'

    @staticmethod
    def header():
        return f'Addr | Next Value | Values'

    def get(self):
        val = self.values[self.next]
        self.next = (self.next + 1) % len(self.values)

        return val

    def set(self, val):
        self.next = (self.next + 1) % len(self.values)
        for i in range(len(self.values)):
            self.values[i] = val

def _verify_hal_reg(hal, addr, name):
    if name and addr:   # Verify Both
        for reg in hal:
            if reg.regname == name and reg.addr == addr:
                return reg.addr, reg.regname

            raise Exception(f'addr 0x{addr:X} does not match name {name}')

    if name:
        for reg in hal:
            if reg.regname == name:
                return reg.addr, reg.regname

        error = f'{name} not found in hal'

    if addr:
        for reg in hal:
            if reg.addr == addr:
                return reg.addr, reg.regname

        error = f'0x{addr:X} not found in hal'

    raise Exception(error)

def _eval_address_or_name(address_or_name):
    if isinstance(address_or_name, str):
        try:
            addr = int(literal_eval(address_or_name))
            name = None
        except: # Assume reg name, not address
            name = address_or_name
            addr = None
    else:
        addr = address_or_name
        name = None

    return addr, name

def _verify_hal_reg_addr_or_name(hal, address_or_name):

    addr, name = _eval_address_or_name(address_or_name)

    return _verify_hal_reg(hal, addr, name)

# TODO: Optimize Verify Emulation File. Currently required building hal twice (once without hif)
#       Perhaps separate verify to after hal is built ?
#       Verify During Build allows for:
#       - Translating regname to address.
#       - Giving line numbers on Errors
#       However it required providing the reg_def_file or hal
#
def ral_emu_build_emu_map(file: str, **kwargs):
    """
    Parse and build a python db from the RAL Emulation Text file input file
    :param file:
    :param max_entries_per_reg: Limit Max Entries Per Register
    :param verify_name_only:
    :param kwargs
        reg_def_file = register definition file to be used for validating address / name
        reg_def_fmt  = format of reg_def_file for parsing. Default = ipxact

        hal = hal used for verifying reg address / name
                If hal is provided:
                - register names are verified to qualify those in hal
                - register address is also accepted
        verify_graceful : bool - Relevant only when hal is provided
                If False, exception is raised
                If True, Log + Skip line
    :return:
    """
    reg_def_file = kwargs.get('reg_def_file', None)
    reg_def_fmt  = kwargs.get('reg_def_fmt', None)
    hal = kwargs.get('hal', None)
    verify_graceful = kwargs.get('verify_graceful', False)

    if not hal and reg_def_file and reg_def_fmt == 'ipxact':
        hal = ipxact_parse(reg_def_file)

    entries = {}
    with open(file, 'rt') as fin:
        for line_number, line in enumerate(fin):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):  # Skip Comment Line
                continue
            if ':' not in line:
                print(f'[RAL EMU] Skipping Line {line_number}:{line}. [ Expected ":" ]')
                continue
            # Remove comment in End of Line
            if '#' in line:
                line = line.split('#')[0]

            addr_value = line.strip().split(':')
            address_or_name = addr_value[0]
            values = addr_value[1:]

            if hal: # Verify will Fail with un-handled exception on purpose
                try:
                    addr, name = _verify_hal_reg_addr_or_name(hal, address_or_name)
                except Exception as e:
                    if verify_graceful:
                        print(f'[RAL EMU] Skipping Line {os.path.basename(file)}:{line_number} [ {address_or_name} Not Found ]')
                    else:
                        raise Exception(f'[RAL EMU] Line {os.path.basename(file)}:{line_number} [ {address_or_name} Not Found ]')
            else:
                addr, name = _eval_address_or_name(address_or_name)

            # Key is Preferred to be ad Address, unless not possible:
            key = f'0x{addr:08X}' if addr is not None else name

            # Convert String Values to int
            values = [literal_eval(val) for val in values]
            entry = ral_emu_entry(addr, name, values, 0)
            entries[key] = entry

    return entries


def _reg_reset_val(reg, val_if_missing = 0xDEADC0DE):

    raise Exception(f'Reset Value Not Yet Supported')

    # TODO: Support build emulation file from Reset Values.
    #  Looks like reset values do not reach hal after ipxact_parse. All values are 0.

    reset_val = 0
    has_reset_val = False
    for field in reg:
        if hasattr(field, 'reset'):
            has_reset_val = True
            reset_val += ((field.reset << field.lsb) & field.mask)

    if not has_reset_val:
        reset_val = val_if_missing   # Default Reset Val, when not exist

    return reset_val

def gen_rand_vals(rand_vals_count, rand_vals_min, rand_vals_max):
    from random import randint
    return [randint(rand_vals_min, rand_vals_max) for i in range(rand_vals_count)]

def gen_reg_emu_file(reg_emu_file, hal, **kwarg):
    """
    kwargs:
        val         : int   - The default value to be used. 0 is not provided
        reset       : bool  - Use reset value from xml, if exist. Otherwise use 0 or 'reset_missing_val' if provided
        reset_missing_val : int - When reset=True and reset value missing from hal, use this value
        val_fmt : str   - 'hex' | 'dec'. String format of value
        rand_vals_count
        rand_vals_min
        rand_vals_max
    """
    val = kwarg.get('val', 0)
    reset = kwarg.get('val_reset', False)
    reset_missing_val = kwarg.get('val_reset_missing', 0)
    val_fmt = kwarg.get('val_fmt', 'hex')
    rand_vals_count = kwarg.get('rand_vals_count', None)
    rand_vals_min = kwarg.get('rand_vals_min', 0)
    rand_vals_max = kwarg.get('rand_vals_max', 100)

    with open(reg_emu_file, 'wt') as fout:
        for reg in hal:
            if rand_vals_count:
                values = gen_rand_vals(rand_vals_count, rand_vals_min, rand_vals_max)
            elif reset:
                values = (_reg_reset_val(reg, reset_missing_val) ,)
            else:
                values = (val, )

            if val_fmt == 'hex':
                values_str = ':'.join([f'0x{val:X}' for val in values])
            else:
                values_str = ':'.join([f'{val}' for val in values])

            fout.write(f'{reg.regname}:{values_str}\n')


def test_gen_reg_emu_file():
    xml = r'ipxact_dim_example.xml'
    hal = ipxact_parse(fname=xml)

    test_item = namedtuple('test_item', 'reg_emu_file use_reg_reset_val reset_missing_val')
    tests = [
        test_item(reg_emu_file=xml.replace('.xml', '_reg_emu_example.txt'), use_reg_reset_val=None, reset_missing_val=None),
        test_item(reg_emu_file=xml.replace('.xml', '_reg_emu_example_rst_vals.txt'), use_reg_reset_val=True, reset_missing_val=0xDEADC0DE),
    ]

    emu_files_generated = []
    for test in tests:
        gen_reg_emu_file(test.reg_emu_file, hal, val_reset=test.use_reg_reset_val, val_reset_missing=test.reset_missing_val)
        emu_files_generated.append(test.reg_emu_file)

    # For Re-usage in Other Tests
    return emu_files_generated, hal

def test_ral_emu_build_emu_map(hal, emu_files):
    # Normal Build - Success
    for file in emu_files:
        emu_map = ral_emu_build_emu_map(file, hal=hal, verify_graceful=True)

        print(f'ral emu map generated from {file}')
        print(f'key | {ral_emu_entry.header()}')
        for key, entry in emu_map.items():
            print(f'{key} : {entry}')

    # Invalid Address Name - Expected Failure - Success
    emu_with_invalid_name = emu_files[0].replace('.txt', '_t_inv_name.txt')
    copyfile(emu_files[0], emu_with_invalid_name)
    with open(emu_with_invalid_name, "at") as fout:
        fout.write(f'invalid_reg_name:0\n')
    emu_files.extend(emu_with_invalid_name)

    file = emu_with_invalid_name
    try:
        ral_emu_build_emu_map(file, hal=hal)
    except Exception as e:
        # verify_graceful=False --> Expected Exception
        print(f'Success - ral_emu_build_emu_map raised exception for invalid reg name, by default')
        print(f'Exception Raised: {e}')

    else:
        print(f'FAIL - ral_emu_build_emu_map DID NOT raise exception for invalid reg name, by default')


    # Invalid Address Value - Expected Pass due to "verify_gracefull=True" - Success
    emu_with_invalid_name = emu_files[0].replace('.txt', '_t_inv_addr.txt')
    copyfile(emu_files[0], emu_with_invalid_name)
    with open(emu_with_invalid_name, "at") as fout:
        fout.write(f'0x0BAD0BAD:0\n')
    emu_files.extend(emu_with_invalid_name)

    file = emu_with_invalid_name
    try:
        ral_emu_build_emu_map(file, hal=hal, verify_graceful=True)
    except Exception as e:
        # verify_graceful=False --> Expected Exception
        print(f'FAIL - ral_emu_build_emu_map raised exception for invalid reg name, despite verify_gracefull=True')
        print(f'Exception Raised: {e}')
    else:
        print(f'Success - ral_emu_build_emu_map failed graceful for invalid reg name, thanks to verify_gracefull=True')


if __name__ == '__main__':
    cleanup = False # For Observing Files

    files, hal = test_gen_reg_emu_file()

    test_ral_emu_build_emu_map(hal, files)

    # Cleanup
    if cleanup:
        for f in files:
            if os.path.exists(f):
                os.remove(f)


