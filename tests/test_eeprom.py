#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Unittest for MicroPython EEPROM"""

import logging
import sys
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from nose2.tools import params


class Pin(object):
    """Fake MicroPython Pin class"""
    def __init__(self, pin: int, mode: int = -1):
        self._pin = pin
        self._mode = mode
        self._value = 0


class I2C(object):
    """Fake MicroPython I2C class"""
    def __init__(self, id: int, *, scl: Pin, sda: Pin, freq: int = 400000):
        self._id = id
        self._scl = scl
        self._sda = sda
        self._freq = freq

    def writeto(addr: int, buf: bytearray, stop: bool = True) -> int:
        return 1

    def readfrom_mem(addr: int,
                     memaddr: int,
                     nbytes: int,
                     *,
                     addrsize: int = 8) -> int:
        return 1

    def writeto_mem(addr: int,
                    memaddr: int,
                    buf: bytearray,
                    *,
                    addrsize: int = 8):
        pass


# custom imports
sys.modules['machine.I2C'] = I2C
to_be_mocked = [
    'machine',
    'time.sleep_ms', 'time.sleep_us',
]
for module in to_be_mocked:
    sys.modules[module] = Mock()

from eeprom import EEPROM  # noqa: E402


class TestEEPROM(unittest.TestCase):
    """This class describes a TestEEPROM unittest."""

    def setUp(self) -> None:
        """Run before every test method"""
        # define a format
        custom_format = "[%(asctime)s][%(levelname)-8s][%(filename)-20s @" \
                        " %(funcName)-15s:%(lineno)4s] %(message)s"

        # set basic config and level for all loggers
        logging.basicConfig(level=logging.INFO,
                            format=custom_format,
                            stream=sys.stdout)

        # create a logger for this TestSuite
        self.test_logger = logging.getLogger(__name__)

        # set the test logger level
        self.test_logger.setLevel(logging.DEBUG)

        # enable/disable the log output of the device logger for the tests
        # if enabled log data inside this test will be printed
        self.test_logger.disabled = False

        self.i2c = I2C(1, scl=Pin(13), sda=Pin(12), freq=800_000)
        self._calls_counter: int = 0
        self._tracked_call_data: list = []
        self._mocked_read_data: bytes = b''

    def _tracked_call(self, *args, **kwargs) -> None:
        """Track function calls and the used arguments"""
        self._tracked_call_data.append({'args': args, 'kwargs': kwargs})

    def test_init(self) -> None:
        """Test EEPROM init function"""
        eeprom = EEPROM()
        self.assertEqual(eeprom.addr, 0x50)
        self.assertEqual(eeprom.pages, 128)
        self.assertEqual(eeprom.bpp, 32)
        # self.assertEqual(eeprom._i2c._id, 0)

        eeprom = EEPROM(i2c=self.i2c)
        self.assertEqual(eeprom.addr, 0x50)
        self.assertEqual(eeprom.pages, 128)
        self.assertEqual(eeprom.bpp, 32)
        self.assertEqual(eeprom._i2c._id, 1)

        eeprom = EEPROM(at24x=128)
        self.assertEqual(eeprom.addr, 0x50)
        self.assertEqual(eeprom.pages, 256)
        self.assertEqual(eeprom.bpp, 64)
        # self.assertEqual(eeprom._i2c._id, 0)

    @params(
        (0x50),
        (80),
    )
    def test_addr(self, addr: int) -> None:
        """Test address property"""
        eeprom = EEPROM(addr=addr)

        self.assertEqual(eeprom.addr, addr)

    @params(
        (128, 32, 4096),    # pages, bytes per page, total size in bytes
        (512, 64, 32768),
    )
    def test_capacity(self, pages: int, bpp: int, expectation: int) -> None:
        """Test capacity property"""
        eeprom = EEPROM(pages=pages, bpp=bpp)

        self.assertEqual(eeprom.capacity, expectation)

    @params(
        (128),
        (512),
    )
    def test_pages(self, pages: int) -> None:
        """Test pages property"""
        eeprom = EEPROM(pages=pages)

        self.assertEqual(eeprom.pages, pages)

    @params(
        (32),
        (64),
    )
    def test_bpp(self, bpp: int) -> None:
        """Test bpp property"""
        eeprom = EEPROM(bpp=bpp)

        self.assertEqual(eeprom.bpp, bpp)

    @params(
        (128, 32, 4096),    # pages, bytes per page, total size in bytes
        (512, 64, 32768),
    )
    def test_length(self, pages: int, bpp: int, expectation: int) -> None:
        """Test length, alias for capacity, following Arduino implementation"""
        eeprom = EEPROM(pages=pages, bpp=bpp)

        self.assertEqual(eeprom.length(), expectation)

    def test_read(self) -> None:
        """Test reading bytes from EEPROM"""
        eeprom = EEPROM(pages=128, bpp=32, i2c=self.i2c)

        with self.assertRaises(ValueError) as context:
            eeprom.read(addr=eeprom.pages + 1)

        self.assertEqual(str(context.exception),
                         "Read address outside of device address range")

        page_addr = 10
        with patch.object(I2C, 'readfrom_mem', wraps=self._tracked_call):
            eeprom.read(addr=page_addr)

        self.assertEqual(len(self._tracked_call_data), 1)
        self.assertEqual(self._tracked_call_data[0]['args'],
                         (eeprom.addr, page_addr, 1))

        self._tracked_call_data = []
        pages_to_read = 5
        with patch.object(I2C, 'readfrom_mem', wraps=self._tracked_call):
            eeprom.read(addr=page_addr, nbytes=pages_to_read)

        self.assertEqual(len(self._tracked_call_data), 1)
        self.assertEqual(self._tracked_call_data[0]['args'],
                         (eeprom.addr, page_addr, pages_to_read))

    def test_write(self) -> None:
        """Test writing bytes to EEPROM"""
        eeprom = EEPROM(pages=128, bpp=32, i2c=self.i2c)

        # write to a non existing page
        for addr in [-1, eeprom.capacity + 1]:
            with self.assertRaises(ValueError) as context:
                eeprom.write(addr=addr, buf=bytes([12]))

            self.assertEqual(str(context.exception),
                             "Write address outside of device address range")

        # write more data than fitting on last page
        addr = (eeprom.pages - 1) * eeprom.bpp
        with self.assertRaises(ValueError) as context:
            eeprom.write(addr=addr, buf=bytes([42] * (eeprom.bpp + 1)))

        self.assertEqual(str(context.exception),
                         "Data does not fit into device address range")

        # partial page write
        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            eeprom.write(addr=0, buf=bytes([93]))

        self.assertEqual(len(self._tracked_call_data), 1)
        self.assertEqual(self._tracked_call_data[0]['args'],
                         (eeprom.addr, 0, bytes([93])))

        self._tracked_call_data = []

        # exact full page write
        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            eeprom.write(addr=0, buf=bytes([93] * eeprom.bpp))

        self.assertEqual(len(self._tracked_call_data), 1)
        self.assertEqual(self._tracked_call_data[0]['args'],
                         (eeprom.addr, 0, bytes([93] * eeprom.bpp)))

        self._tracked_call_data = []

        # overhanging page write
        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            eeprom.write(addr=0, buf=bytes([93] * (eeprom.bpp + 1)))

        self.assertEqual(len(self._tracked_call_data), 2)
        self.assertEqual(self._tracked_call_data[0]['args'],
                         (eeprom.addr, 0, bytes([93] * eeprom.bpp)))
        self.assertEqual(self._tracked_call_data[1]['args'],
                         (eeprom.addr, eeprom.bpp, bytes([93] * 1)))

        self._tracked_call_data = []

        # with offset (write not to the begin of a page)
        offset = 5
        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            eeprom.write(addr=offset, buf=bytes([18]))

        self.assertEqual(len(self._tracked_call_data), 1)
        self.assertEqual(self._tracked_call_data[0]['args'],
                         (eeprom.addr, offset, bytes([18])))

        self._tracked_call_data = []

        # with offset + overhanging (write not to the begin of a page)
        offset = 5
        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            eeprom.write(addr=offset, buf=bytes([18] * (eeprom.bpp - offset)))

        self.assertEqual(len(self._tracked_call_data), 1)
        self.assertEqual(
            self._tracked_call_data[0]['args'],
            (eeprom.addr, offset, bytes([18] * (eeprom.bpp - offset)))
        )

    def _mocked_read_function(self, addr: int, nbytes: int = 1) -> bytes:
        """Mocked EEPROM read function"""
        if isinstance(self._mocked_read_data[addr], bytes):
            if nbytes == 1:
                return self._mocked_read_data[addr]
            else:
                return self._mocked_read_data[addr:addr + nbytes]
        else:
            return self._mocked_read_data[addr: addr + nbytes].encode()

    def test_update_str(self) -> None:
        """Test updating EEPROM cell with string"""
        eeprom = EEPROM(pages=128, bpp=32, i2c=self.i2c)

        # this will be the new data for the EEPROM
        update_buffer = 'hello world'

        # this is the old, existing data in the EEPROM
        self._mocked_read_data = 'hello carl'

        # ensure there is enough data to read
        self._mocked_read_data += \
            '\xff' * (len(update_buffer) - len(self._mocked_read_data))

        # patch the EEPROM read function with the mocked data
        with patch.object(
            EEPROM, 'read', side_effect=self._mocked_read_function
        ):
            with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
                eeprom.update(addr=0, buf=update_buffer)

        # difference is 'w', 'o', 'd'
        self.assertEqual(len(self._tracked_call_data), 3)
        for idx, (addr, val) in enumerate(zip([6, 7, 10], [b'w', b'o', b'd'])):
            self.assertEqual(
                self._tracked_call_data[idx]['args'],
                (eeprom.addr, addr, val)
            )

    def test_update_bytes(self) -> None:
        """Test updating EEPROM cell with bytes"""
        eeprom = EEPROM(pages=128, bpp=32, i2c=self.i2c)

        # this will be the new data for the EEPROM
        update_buffer = b'hello world'

        # this is the old, existing data in the EEPROM
        self._mocked_read_data = 'hello carl'

        # ensure there is enough data to read
        self._mocked_read_data += \
            '\xff' * (len(update_buffer) - len(self._mocked_read_data))

        # patch the EEPROM read function with the mocked data
        with patch.object(
            EEPROM, 'read', side_effect=self._mocked_read_function
        ):
            with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
                eeprom.update(addr=0, buf=update_buffer)

        # difference is 'w', 'o', 'd'
        self.assertEqual(len(self._tracked_call_data), 3)
        for idx, (addr, val) in enumerate(zip([6, 7, 10], [b'w', b'o', b'd'])):
            self.assertEqual(
                self._tracked_call_data[idx]['args'],
                (eeprom.addr, addr, val)
            )

    def test_update_int(self) -> None:
        """Test updating EEPROM cell with int"""
        eeprom = EEPROM(pages=128, bpp=32, i2c=self.i2c)

        # this will be the new data for the EEPROM
        update_buffer = [1, 93, 42, 23, 255, 7]

        # this is the old, existing data in the EEPROM
        self._mocked_read_data = [
            # 1, 95, 42, 22, 0, 7
            b'\x01', b'_', b'*', b'\x16', b'\x00', b'\x07',
        ]
        # ensure there is enough data to read
        self._mocked_read_data += \
            '\xff' * (len(update_buffer) - len(self._mocked_read_data))

        # patch the EEPROM read function with the mocked data
        with patch.object(
            EEPROM, 'read', side_effect=self._mocked_read_function
        ):
            with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
                eeprom.update(addr=0, buf=update_buffer)

        # difference is 93, 23, 255
        print(self._tracked_call_data)
        self.assertEqual(len(self._tracked_call_data), 3)
        for idx, (addr, val) in enumerate(zip([1, 3, 4],
                                              [b']', b'\x17', b'\xff'])):
            self.assertEqual(
                self._tracked_call_data[idx]['args'],
                (eeprom.addr, addr, val)
            )

    def test_wipe(self) -> None:
        """Test wiping EEPROM"""
        eeprom = EEPROM(pages=128, bpp=32, i2c=self.i2c)

        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            eeprom.wipe()

        self.assertEqual(len(self._tracked_call_data), 128)
        for idx, ele in enumerate(self._tracked_call_data):
            self.assertEqual(
                ele['args'],
                (eeprom.addr, idx * eeprom.bpp, bytes([255] * eeprom.bpp))
            )

    # @unittest.skip('bl')
    def test_print_pages(self) -> None:
        """Test print of EEPROM pages"""
        eeprom = EEPROM(pages=128, bpp=4, i2c=self.i2c)

        # this is the existing data in the EEPROM
        self._mocked_read_data = 'hello carl'

        # patch the EEPROM read function with the mocked data
        with patch.object(
            EEPROM, 'read', side_effect=self._mocked_read_function
        ):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                eeprom.print_pages(addr=0, nbytes=len(self._mocked_read_data))

        printed_lines = mock_stdout.getvalue().split('\n')
        self.assertEqual(len(printed_lines), 1 + 4)     # first line + x
        self.assertEqual(
            printed_lines[0],
            'Page ---x: 0 --- {}'.format(eeprom.bpp)
        )
        for x in range(0, 3):
            start_pos = x * eeprom.bpp
            end_pos = (x + 1) * eeprom.bpp

            data = self._mocked_read_data[start_pos:end_pos].encode()

            if end_pos > len(self._mocked_read_data):
                data += b'?' * (end_pos - len(self._mocked_read_data))

            self.assertEqual(
                printed_lines[x + 1],
                'Page ---{}: {}'.format(x, data)
            )

    def test_print_pages_offset(self) -> None:
        """Test print of EEPROM pages"""
        eeprom = EEPROM(pages=128, bpp=4, i2c=self.i2c)

        # this is the existing data in the EEPROM
        self._mocked_read_data = 'hello carl'
        offset = 1

        # patch the EEPROM read function with the mocked data
        with patch.object(
            EEPROM, 'read', side_effect=self._mocked_read_function
        ):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                eeprom.print_pages(
                    addr=offset,
                    nbytes=len(self._mocked_read_data)
                )

        printed_lines = mock_stdout.getvalue().split('\n')
        self.assertEqual(len(printed_lines), 1 + 4)     # first line + x
        self.assertEqual(
            printed_lines[0],
            'Page ---x: 0 --- {}'.format(eeprom.bpp)
        )
        for x in range(0, 3):
            start_pos = x * eeprom.bpp
            end_pos = (x + 1) * eeprom.bpp

            data = self._mocked_read_data[start_pos:end_pos].encode()
            if x == 0:
                data = b'?' * offset + data[offset:]

            if end_pos > len(self._mocked_read_data):
                data += b'?' * (end_pos - len(self._mocked_read_data) - offset)

            self.assertEqual(
                printed_lines[x + 1],
                'Page ---{}: {}'.format(x, data)
            )

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


if __name__ == '__main__':
    unittest.main()
