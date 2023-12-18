################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

from pytrinamic.evalboards import TMCLEval
from pytrinamic.ic import TMC5072
from pytrinamic.features import MotorControlModule

# from pytrinamic.features.linear_ramp_module import LinearRampModule
# from pytrinamic.features.stallguard2_module import StallGuard2Module
# from pytrinamic.features.CurrentModule import CurrentModule


class TMC5072_eval(TMCLEval):
    """
    This class represents a TMC5072 Evaluation board.
    """
    def __init__(self, connection, module_id=1):
        """
        Constructor for the TMC5130 evalboard instance.

        Parameters:
        connection: TMCL connection interface instance.
        module_id: Module ID to identify the evalboard module. This is used to differentiate
        between different modules on shared busses. Default is set to 1, different
        values have to be configured with the module first.
        """
        TMCLEval.__init__(self, connection, module_id)
        self.motors = [self._MotorTypeA(self, 0), self._MotorTypeA(self, 1)]
        self.ics = [TMC5072(self)]

    # Use the driver controller functions for register access

    def write_register(self, register_address, value):
        return self._connection.write_mc(register_address, value, self._module_id)

    def read_register(self, register_address, signed=False):
        return self._connection.read_mc(register_address, self._module_id, signed)

    # Motion control functions

    def rotate(self, motor, value):
        self._connection.rotate(motor, value)

    def stop(self, motor):
        self._connection.stop(motor)

    def move_to(self, motor, position, velocity=None):
        if velocity and velocity != 0:
            # Set maximum positioning velocity
            self.motors[motor].set_axis_parameter(self.motors[motor].AP.MaxVelocity, velocity)
        self._connection.move_to(motor, position, self._module_id)

    class _MotorTypeA(MotorControlModule):
        """
        Motor class for the generic motor.
        """
        def __init__(self, eval_board, axis):
            MotorControlModule.__init__(self, eval_board, axis, self.AP)
            # LinearRampModule.__init__(self)
            # StallGuard2Module.__init__(self)
            # CurrentModule.__init__(self)

        class AP:
            TargetPosition                 = 0
            ActualPosition                 = 1
            TargetVelocity                 = 2
            ActualVelocity                 = 3
            MaxVelocity                    = 4
            MaxAcceleration                = 5
            MaxCurrent                     = 6
            StandbyCurrent                 = 7
            PositionReachedFlag            = 8
            RightEndstop                   = 10
            LeftEndstop                    = 11
            AutomaticRightStop             = 12
            AutomaticLeftStop              = 13
            SW_MODE                        = 14
            A1                             = 15
            V1                             = 16
            MaxDeceleration                = 17
            D1                             = 18
            StartVelocity                  = 19
            StopVelocity                   = 20
            RampWaitTime                   = 21
            smartEnergyThresholdSpeed      = 22
            THIGH                          = 23
            VDCMIN                         = 24
            HighSpeedFullstepMode          = 28
            MicrostepResolution            = 140
            ChopperBlankTime               = 162
            ConstantTOffMode               = 163
            DisableFastDecayComparator     = 164
            ChopperHysteresisEnd           = 165
            ChopperHysteresisStart         = 166
            TOff                           = 167
            SEIMIN                         = 168
            SECDS                          = 169
            smartEnergyHysteresis          = 170
            SECUS                          = 171
            smartEnergyHysteresisStart     = 172
            SG2FilterEnable                = 173
            SG2Threshold                   = 174
            VSense                         = 179
            smartEnergyActualCurrent       = 180
            smartEnergyStallVelocity       = 181
            RandomTOffMode                 = 184
            ChopperSynchronization         = 185
            LoadValue                      = 206
            EncoderPosition                = 209
            EncoderResolution              = 210
