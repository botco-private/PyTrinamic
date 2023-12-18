################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

import time
import statistics
import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.evalboards import TMC4671_eval, TMC6100_eval
from pytrinamic.ic import TMC4671, TMC6100

pytrinamic.show_info()

with ConnectionManager().connect() as my_interface:
    print(my_interface)

    # Create a TMC4671-EVAL and TMC6100-EVAL which communicates over the Landungsbrücke via TMCL
    mc_eval = TMC4671_eval(my_interface)
    drv_eval = TMC6100_eval(my_interface)

    # Configure TMC6100 pwm for use with TMC4671 (disable singleline)
    drv_eval.write_register_field(TMC6100.FIELD.SINGLELINE, 0)

    # Configure TMC4671 for a BLDC motor in open loop mode

    # Motor type & PWM configuration
    mc_eval.write_register_field(TMC4671.FIELD.MOTOR_TYPE, TMC4671.ENUM.MOTOR_TYPE_BLDC)
    mc_eval.write_register_field(TMC4671.FIELD.N_POLE_PAIRS, 4)
    mc_eval.write_register(TMC4671.REG.PWM_POLARITIES, 0x00000000)
    mc_eval.write_register(TMC4671.REG.PWM_MAXCNT, int(0x00000F9F))
    mc_eval.write_register(TMC4671.REG.PWM_BBM_H_BBM_L, 0x00001414)
    mc_eval.write_register_field(TMC4671.FIELD.PWM_CHOP, TMC4671.ENUM.PWM_CENTERED_FOR_FOC)
    mc_eval.write_register_field(TMC4671.FIELD.PWM_SV, 1)

    # ADC configuration
    mc_eval.write_register(TMC4671.REG.ADC_I_SELECT, 0x24000100)
    mc_eval.write_register(TMC4671.REG.dsADC_MCFG_B_MCFG_A, 0x00100010)
    mc_eval.write_register(TMC4671.REG.dsADC_MCLK_A, 0x20000000)
    mc_eval.write_register(TMC4671.REG.dsADC_MCLK_B, 0x00000000)
    mc_eval.write_register(TMC4671.REG.dsADC_MDEC_B_MDEC_A, int(0x014E014E))
    # ADC offset compensation
    adc_i0_samples = []
    adc_i1_samples = []
    mc_eval.write_register(TMC4671.REG.ADC_I0_SCALE_OFFSET, 0xFF000000)
    mc_eval.write_register(TMC4671.REG.ADC_I1_SCALE_OFFSET, 0xFF000000)
    for _ in range(50):
        adc_i0_samples.append(mc_eval.read_register_field(TMC4671.FIELD.ADC_I0_RAW))
        adc_i1_samples.append(mc_eval.read_register_field(TMC4671.FIELD.ADC_I0_RAW))
    adc_i0_offset = statistics.mean(adc_i0_samples)
    adc_i1_offset = statistics.mean(adc_i1_samples)
    mc_eval.write_register(TMC4671.REG.ADC_I0_SCALE_OFFSET, 0xFF000000 + int(adc_i0_offset))
    mc_eval.write_register(TMC4671.REG.ADC_I1_SCALE_OFFSET, 0xFF000000 + int(adc_i1_offset))

    # Open loop settings
    mc_eval.write_register(TMC4671.REG.OPENLOOP_MODE, 0x00000000)
    mc_eval.write_register(TMC4671.REG.OPENLOOP_ACCELERATION, 100)

    # Feedback selection
    mc_eval.write_register(TMC4671.REG.PHI_E_SELECTION, TMC4671.ENUM.PHI_E_OPEN_LOOP)
    mc_eval.write_register(TMC4671.REG.UQ_UD_EXT, 2000)

    # ===== Open loop test drive =====

    # Switch to open loop velocity mode
    mc_eval.write_register(TMC4671.REG.MODE_RAMP_MODE_MOTION, TMC4671.ENUM.MOTION_MODE_UQ_UD_EXT)

    # Rotate right
    print("Rotate right...")
    mc_eval.write_register(TMC4671.REG.OPENLOOP_VELOCITY_TARGET, 200)
    time.sleep(3)

    # Rotate left
    print("Rotate left...")
    mc_eval.write_register(TMC4671.REG.OPENLOOP_VELOCITY_TARGET, -200)
    time.sleep(6)

    # Stop
    print("Stop...")
    mc_eval.write_register(TMC4671.REG.OPENLOOP_VELOCITY_TARGET, 0)
    time.sleep(3)

    # Unpower
    print("Unpowered...")
    mc_eval.write_register(TMC4671.REG.UQ_UD_EXT, 0)

print("\nReady.")
