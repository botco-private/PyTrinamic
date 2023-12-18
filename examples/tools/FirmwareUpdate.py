################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

import argparse
import sys
import time
import math
import re
import struct
import logging
import intelhex

import pytrinamic
from pytrinamic.connections.connection_manager import ConnectionManager
from pytrinamic.tmcl import TMCLCommand

# Timeout in seconds for reconnecting to the module after sending the TMCL_BOOT
# command.
SERIAL_BOOT_TIMEOUT = 100
# ################################ Commandline ##################################
parser = argparse.ArgumentParser()

# Mandatory arguments
parser.add_argument("hex_file", metavar="hex-file", help="Hex file to be uploaded")

# Optional arguments
parser.add_argument('-v', '--verbose', action="count", default=0, help="Verbosity level")

# ConnectionManager arguments
ConnectionManager.argparse(parser)

args = parser.parse_args()

# ################################ Preparation ##################################
pytrinamic.show_info()

connectionManager = ConnectionManager(sys.argv)

if args.verbose == 0:
    log_level = logging.ERROR
elif args.verbose == 1:
    log_level = logging.WARNING
elif args.verbose == 2:
    log_level = logging.INFO
else:
    log_level = logging.DEBUG

logging.basicConfig(stream=sys.stdout, level=log_level)

############################### Hex file parsing ###############################
print("Opening hex file (" + args.hex_file + ")")
file = intelhex.IntelHex(args.hex_file)
file.padding = 0x00
# ########################## Binary data preparation ############################

# Get the boundaries and size of the data
start_address = file.minaddr()
end_address = file.maxaddr()
length = end_address - start_address

# Calculate the checksum
checksum = 0
for addr in file.addresses():
    checksum += file[addr]
    checksum &= 0xFFFFFFFF

logging.info("Start address: 0x{0:08X}".format(start_address))
logging.info("End address:   0x{0:08X}".format(end_address))
logging.info("Length:        0x{0:08X}".format(length))
logging.info("Checksum:      0x{0:08X}".format(checksum))

# ############################# Bootloader entry ################################
# Connect to the evaluation board
print("Connecting")
myInterface = connectionManager.connect()

# If not already in bootloader, enter it
if not "B" in myInterface.get_version_string().upper():
    # Send the boot command
    print("Switching to bootloader mode")
    myInterface.send_boot(1)
    myInterface.close()

    # Reconnect after a small delay
    print("Reconnecting")
    timestamp = time.time()
    while (time.time() - timestamp) < SERIAL_BOOT_TIMEOUT:
        try:
            # Attempt to connect
            myInterface = connectionManager.connect()
            # If no exception occurred, exit the retry loop
            break
        except (ConnectionError, TypeError):
            myInterface = None

    if not myInterface:
        print("Error: Timeout when attempting to reconnect to bootloader")
        exit(1)

time.sleep(1)

# Retrieve the bootloader version
bootloaderVersion = myInterface.get_version_string(1)
found = re.search("\d\d\d\dB\d\d\d", bootloaderVersion)
if found:
    pattern = found.group(0)[0:4] + "V\d\d\d"
    logging.info(f"Scanning new firmware data for correct module string ({found.group(0)[0:4]}V###)")
else:
    found = re.search("\d\d\dB\d\.\d\d", bootloaderVersion)
    if found:
        pattern = found.group(0)[0:3] + "V\d\.\d\d"
        logging.info(f"Scanning new firmware data for correct module string ({found.group(0)[0:3]}V#.##)")
    else:
        logging.error(f"GetVersion returned invalid answer ({bootloaderVersion})")
        exit(1)

# Scan for the module string
found = None
for segment in file.segments():
    print(segment)
    start = segment[0]
    length = segment[1] - segment[0]
    firmware_bytes = file.gets(start, length)
    firmware_string = str(firmware_bytes, encoding="ascii", errors="ignore")

    found = re.search(pattern, firmware_string)
    if found:
        break
else:
    print("Error: No matching version string found in firmware image")
    exit(1)

start = file.minaddr()
length = file.maxaddr() - start

print("Bootloader version: " + bootloaderVersion)
print("Firmware version:   " + found.group(0))

print()

# Get the memory parameters
reply = myInterface.send(TMCLCommand.BOOT_GET_INFO, 0, 0, 0)
mem_page_size = reply.value
reply = myInterface.send(TMCLCommand.BOOT_GET_INFO, 1, 0, 0)
mem_start_address = reply.value
reply = myInterface.send(TMCLCommand.BOOT_GET_INFO, 2, 0, 0)
mem_size = reply.value

logging.debug(f"Bootloader memory page size:      0x{mem_page_size:08X}")
logging.debug(f"Bootloader Memory start address:  0x{mem_start_address:08X}")
logging.debug(f"Bootloader Memory size:           0x{mem_size:08X}")

# Check if the page size is a power of two
if not(((mem_page_size & (mem_page_size - 1)) == 0) and mem_page_size != 0):
    print("Error: Page size of module is not a power of two")
    print("Reported page size: {0:X}".format(mem_page_size))
    exit(1)

# Check if the start addresses match
if start_address != mem_start_address:
    print("Error: Start address of firmware (0x{0:08X}) does not match start address of bootloader (0x{1:08X})".format(start_address, mem_start_address))
    exit(1)

# ############################## Firmware upload ################################

# Erase the old firmware
print("Erasing the old firmware")
reply = myInterface.send(TMCLCommand.BOOT_ERASE_ALL, 0, 0, 0)

# Calculate the starting page
current_page = math.floor(start_address/mem_page_size) * mem_page_size
# Store the internal page buffer state
current_page_dirty = False


# Helper function: BOOT_WRITE_PAGE safety wrapper
def writePage(page):
    if page == 0:
        raise ValueError

    print("Writing page 0x{0:08X}".format(page))
    myInterface.send(TMCLCommand.BOOT_WRITE_PAGE, 0, 0, current_page)


# Helper function: Write a 32 bit data block
def write32Bit(address, write_data):
    global current_page
    global current_page_dirty

    # Split the address of the entry into page/offset values
    page = math.floor(address/mem_page_size) * mem_page_size
    offset = address - page

    if page != current_page:
        writePage(current_page)
        current_page = page
        current_page_dirty = False

    # print("Writing {0:08X} to offset {1:04X} on page {2:08X}".format(writeData, offset, page))
    myInterface.send(TMCLCommand.BOOT_WRITE_BUFFER, math.floor(offset / 4) % 256, math.floor(math.floor(offset / 4) / 256), write_data)
    current_page_dirty = True

print("Uploading new firmware...")
for addr in range(start_address, end_address, 4):
    value = file[addr+3] << 24 | file[addr+2] << 16 | file[addr+1] << 8 | file[addr]
    write32Bit(addr, value)

# If the last page didn't get written yet, write it
if current_page_dirty:
    writePage(current_page)

print()

# Checksum verification
reply = myInterface.send(TMCLCommand.BOOT_GET_CHECKSUM, 0, 0, end_address - 1)
if reply.value != checksum:
    print("Error: Checksums don't match! (Checksum: 0x{0:08X}, received: 0x{1:08X}".format(checksum, reply.value))
    exit(1)

print("Checksum of the uploaded firmware matches")
print("Finalizing upload (Writing length and checksum)")
# Write firmware length
myInterface.send(TMCLCommand.BOOT_WRITE_LENGTH, 0, 0, length)
# Write firmware checksum
myInterface.send(TMCLCommand.BOOT_WRITE_LENGTH, 1, 0, checksum)

# Restart the firmware
print("Starting the firmware")
myInterface.send(TMCLCommand.BOOT_START_APPL, 0, 0, 0)
