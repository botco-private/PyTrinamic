################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.modules import TMCC160
import time

pytrinamic.show_info()

# please select your CAN adapter
# my_interface = ConnectionManager("--interface pcan_tmcl").connect()
my_interface = ConnectionManager("--interface kvaser_tmcl").connect()

with my_interface:
    module = TMCC160(my_interface)
    motor = module.motors[0]

    # Define motor configuration for the TMCC160-EVAL.
    #
    # The configuration is based on our standard BLDC motor (QBL4208-61-04-013-1024-AT).
    # If you use a different motor be sure you have the right configuration setup otherwise the script may not work.

    # drive configuration
    motor.drive_settings.poles = 8
    motor.drive_settings.max_current = 2000
    motor.drive_settings.target_reached_velocity = 500
    motor.drive_settings.target_reached_distance = 5
    motor.drive_settings.open_loop_current = 1000

    # encoder configuration
    motor.abn_encoder.resolution = 4096
    # motor.abn_encoder.resolution = 16384
    motor.abn_encoder.direction = 0
    motor.abn_encoder.init_mode = motor.ENUM.ENCODER_INIT_MODE_0
    print(motor.abn_encoder)

    # motion settings
    motor.linear_ramp.max_velocity = 1000
    motor.linear_ramp.max_acceleration = 2000
    motor.linear_ramp.enabled = 1
    print(motor.linear_ramp)

    # PI configuration
    motor.pid.torque_p = 600
    motor.pid.torque_i = 600
    motor.pid.velocity_p = 800
    motor.pid.velocity_i = 500
    motor.pid.position_p = 300
    print(motor.pid)

    time.sleep(1.0)

    # set commutation mode to FOC based on encoder feedback
    motor.drive_settings.commutation_mode = motor.ENUM.COMM_MODE_FOC_ENCODER
    print(motor.drive_settings)

    # clear actual position
    motor.actual_position = 0

    print("move to first position")
    motor.move_to(motor.abn_encoder.resolution * 50)

    # wait for position reached
    while not motor.get_position_reached():
        print("target position: " + str(motor.target_position) + " actual position: " + str(motor.actual_position))
        time.sleep(0.2)

    print("move back to zero")
    motor.move_to(0)

    # wait for position reached
    while not motor.get_position_reached():
        print("target position: " + str(motor.target_position) + " actual position: " + str(motor.actual_position))
        time.sleep(0.2)

print("\nReady.")
