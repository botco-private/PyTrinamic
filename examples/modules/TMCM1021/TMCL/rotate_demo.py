################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.modules import TMCM1021
import time

pytrinamic.show_info()

with ConnectionManager("--interface serial_tmcl --port COM8 --data-rate 9600").connect() as my_interface:
    print(my_interface)
    module = TMCM1021(my_interface)
    motor = module.motors[0]

    # The configuration is based on our PD28-x-1021-TMCL
    # If you use a different motor be sure you have the right configuration setup otherwise the script may not working.

    print("Preparing parameters...")

    # preparing drive settings
    motor.drive_settings.max_current = 1000
    motor.drive_settings.standby_current = 0
    motor.drive_settings.boost_current = 0
    motor.drive_settings.microstep_resolution = motor.ENUM.MicrostepResolution256Microsteps
    print(motor.drive_settings)

    # preparing linear ramp settings
    motor.linear_ramp.max_acceleration = 25600
    motor.linear_ramp.max_velocity = 51200
    print(motor.linear_ramp)

    time.sleep(1.0)

    # clear position counter
    motor.actual_position = 0

    # start rotating motor for 5 sek
    print("Rotating...")
    motor.rotate(102400)
    time.sleep(5)

    # stop rotating motor
    print("Stopping...")
    motor.stop()

    # read actual position
    print("ActualPosition = {}".format(motor.actual_position))
    time.sleep(2)

    print("Doubling moved distance.")
    motor.move_by(motor.actual_position)

    # wait till position_reached
    while not motor.get_position_reached():
        print("target position: " + str(motor.target_position) + " actual position: " + str(motor.actual_position))
        time.sleep(0.2)

    print("Furthest point reached.")
    print("ActualPosition = {}".format(motor.actual_position))

    # short delay and move back to start
    time.sleep(3)
    print("Moving back to 0...")
    motor.move_to(0)

    # wait until position 0 is reached
    while not motor.get_position_reached():
        print("target position: " + str(motor.target_position) + " actual position: " + str(motor.actual_position))
        time.sleep(0.2)

    print("Reached position 0.")

print("\nReady.")