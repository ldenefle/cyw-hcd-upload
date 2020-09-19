#!/usr/bin/env python3

import sys
import time
import serial
import click
import struct
import logging

RESET_CMD = 0x0C03
WRITE_RAM = 0xFC4C
LAUNCH_RAM = 0xFC4E

EXPECTED_RESPONSE = {
    RESET_CMD : [ 0x04, 0x0E, 0x04, 0x01, 0x03, 0x0C, 0x00 ],
    WRITE_RAM : [ 0x04, 0x0E, 0x04, 0x01, 0x4C, 0xFC, 0x00 ],
    LAUNCH_RAM : [ 0x04, 0x0E, 0x04, 0x01, 0x4E, 0xFC, 0x00 ],
}

prettier = lambda byte_array: ''.join(format(x, '02x') for x in byte_array)

class UnexpectedResponse(Exception):
    """A command did not receive the expected response"""
    def __init__(self, command, expected, response):
        self.message = "Expected {} but received {} when sending {:X}".format(prettier(expected), prettier(response), command)
        super().__init__(self.message)

class HCDCommand():
    """HCI Commands contained in a hcd file"""
    def __init__(self, command, payload, expected):
        self.command = command
        self.payload = payload
        self.expected = expected

    def send(self, transport):
        data = bytearray([0x01]) + struct.pack("H", self.command) + bytearray([len(self.payload)]) + self.payload
        transport.write(data)
        response = transport.read(len(self.expected))
        if bytearray(self.expected) != response:
            raise UnexpectedResponse(self.command, self.expected, response)

    def dumps(self):
        def get_address(payload):
            (address, ) = struct.unpack('<I', payload[:4])
            return address
        if self.command == WRITE_RAM:
            return "Write RAM | 0x{:08X} | {}".format(get_address(self.payload), prettier(self.payload))
        elif self.command == LAUNCH_RAM:
            return "Launch RAM | 0x{:08X}".format(get_address(self.payload))

class HCDFirmware():
    """Iterator over the commands of a HCD file"""
    def __init__(self, fw):
        self.fw = fw

    def __iter__(self):
        return self

    def __next__(self):
        header = self.fw.read(3)
        if len(header) < 3:
            raise StopIteration
        (command_id, size) = struct.unpack("HB", header)
        data = self.fw.read(size)
        return HCDCommand(command_id, data, EXPECTED_RESPONSE[command_id])

class Transport():
    def __init__(self, transport):
        self.transport = transport

    def read(self, length):
        logging.debug("Reading {}".format(length))
        return self.transport.read(length)

    def write(self, payload):
        logging.debug("Writing {}".format(prettier(payload)))
        return self.transport.write(payload)

@click.command()
@click.option('--fw', required=True, type=click.File('rb'), help="HCD Firmware file path")
@click.option('--port', '-p', required=True, help="Serial port to use to communicate HCI commands")
@click.option('--verbose', '-v', is_flag=True, help="Make the output verbose")
def load_ram_hcd(fw, port, verbose):
    """Load a cypress firmware in hcd format in ram"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    reset_command = HCDCommand(RESET_CMD, bytearray(), EXPECTED_RESPONSE[RESET_CMD])

    with serial.Serial(port, 115200, timeout=2) as ser:
        transport = Transport(ser)
        commands = HCDFirmware(fw)
        reset_command.send(transport)
        for command in commands:
            try:
                command.send(transport)
                logging.debug(command.dumps())
                logging.debug("Successfully sent command")
                time.sleep(0.01)
            except UnexpectedResponse as e:
                logging.error(e)
                logging.error(command.dumps())
                time.sleep(1)

if __name__ == '__main__':
    load_ram_hcd()


