################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################
"""
Move a motor back and forth using pwm mode of the TMC6140-eval

Author: ASU

"""

import time
import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.evalboards import TMC6140_eval

pytrinamic.show_info()

with ConnectionManager().connect() as my_interface:
    print(my_interface)

    eval_board = TMC6140_eval(my_interface)
    motor = eval_board.motors[0]

    # configure
    motor.set_commutation_mode(1)
    motor.set_hall_order(0)

    print("Rotating...")
    motor.set_target_pwm(8000)
    time.sleep(3)

    print("Stopping...")
    motor.set_target_pwm(0)
    time.sleep(2)

    print("Rotating back...")
    motor.set_target_pwm(-8000)
    time.sleep(3)

    print("Stopping...")
    motor.set_target_pwm(0)

print("\nReady.")
