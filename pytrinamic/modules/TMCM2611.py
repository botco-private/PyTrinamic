# features
from ..features import (
    ABNEncoderModule,
    DigitalHallModule,
    DriveSettingModule,
    LinearRampModule,
    MotorControlModule,
    PIDModule,
)
from . import TMCLModule


class TMCM2611(TMCLModule):
    """
    The TMCM-2611-AGV is a dual axis servo drive module for three phase BLDC motors
        * Supply Voltage: 24-48V
    """

    def __init__(self, connection, module_id=1):
        super().__init__(connection, module_id)

        self.name = "TMCM-2611-AGV"
        self.desc = self.__doc__
        self.motors = [self._MotorTypeA(self, 0), self._MotorTypeA(self, 1)]

    def rotate(self, axis, velocity):
        self.connection.rotate(axis, velocity, self.module_id)

    def stop(self, axis):
        self.connection.stop(axis, self.module_id)

    def move_to(self, axis, position, velocity=None):
        if velocity:
            self.motors[axis].linear_ramp.max_velocity = velocity
        self.connection.move_to(axis, position, self.module_id)

    def move_by(self, axis, difference, velocity=None):
        if velocity:
            self.motors[axis].linear_ramp.max_velocity = velocity
        self.connection.move_by(axis, difference, self.module_id)

    class _MotorTypeA(MotorControlModule):
        def __init__(self, module, axis):
            MotorControlModule.__init__(self, module, axis, self.AP)
            self.drive_settings = DriveSettingModule(module, axis, self.AP)
            self.linear_ramp = LinearRampModule(module, axis, self.AP)
            self.abn_encoder = ABNEncoderModule(module, axis, self.AP)
            self.digital_hall = DigitalHallModule(module, axis, self.AP)
            self.pid = PIDModule(module, axis, self.AP)

        def get_position_reached(self):
            return self.get_axis_parameter(self.AP.PositionReachedFlag)

        class AP:
            # ADC Measurement
            AdcI0Raw = 0
            AdcI1Raw = 1
            CurrentPhaseU = 2
            CurrentPhaseV = 3
            CurrentPhaseW = 4

            # ADC Settings
            AdcOffsetPhaseA = 5
            AdcOffsetPhaseB = 6

            # Motor settings
            MotorPolePairs = 10
            MaxCurrent = 11
            OpenLoopCurrent = 12
            MotorDirection = 13
            MotorType = 14
            CommutationMode = 15
            ActualOpenLoopAngle = 16
            ActualEncoderAngle = 17
            ActualHallAngle = 18
            ActualEncoderOpenLoopAngleDiff = 20
            ActualHallOpenLoopAngleDigg = 21
            VelocityUnitSelection = 27

            # Torque mode settings
            TargetTorque = 30
            ActualTorque = 31
            TargetFlux = 32
            ActualFlux = 33
            ActualTorqueUnfiltered = 34

            # Velocity mode settings
            TargetVelocity = 40
            RampVelocity = 41
            ActualVelocity = 42
            MaxVelocity = 43
            MaxAcceleration = 44
            EnableRamp = 45
            VelocityFilter = 46
            MotorHaltedVelocity = 47
            ActualVelocityUnfiltered = 48

            # Position mode settings
            ActualAbsoluteEncoderAngle = 19
            PositionSensorSelection = 25
            TargetPosition = 50
            RampPosition = 51
            ActualPosition = 52
            TargetReachedDistance = 53
            TargetReachedVelocity = 54
            PositionReachedFlag = 55
            PositionScaler = 56
            UseFeedForwardPosition = 57

            # PI parameters
            TorqueP = 70
            TorqueI = 71
            VelocityP = 72
            VelocityI = 73
            PositionP = 74
            TorqueISUM = 75
            FluxIntegralSUM = 76
            VelocityIntegralSUM = 77
            TorquePIDError = 78
            FluxPIDError = 79
            VelocityPIDError = 80
            PositionPIDError = 81

            # Hall settings
            HallSensorPolarity = 90
            HallSensorDirection = 91
            HallSensorInterpolation = 92
            HallSensorOffset = 93
            HallSensorInputs = 94

            # Encoder settings
            EncoderSteps = 100
            EncoderDirection = 101
            EncoderInitMode = 102
            EncoderInitState = 103
            EncoderInitDelay = 104
            EncoderInitVelocity = 105
            EncoderOffset = 106
            ClearOnNull = 107
            ClearOnce = 108
            EncoderInputs = 109
            EncoderRawValue = 111

            # Chopper settings
            PWMFrequency = 110

            # Brake control
            BrakeRelease = 120
            BrakeReleaseDuty = 121
            BrakeHoldDuty = 122
            BrakeReleaseDuration = 132
            BrakeEnable = 124
            BrakeInvert = 125

            # Brake Chopper control
            BrakeChopperVoltage = 141
            BrakeChopperHyteresis = 142
            BrakeChopperActive = 144

            # General APs
            StatusFlags = 156
            SupplyVoltage = 220
            DriverTemperature = 221
            MainLoopsPerSecond = 230
            TorqueLoopsPerSecond = 231
            VelocityLoopsPerSecond = 232

            # Ref switches
            ReferenceSwitchEnable = 209
            ReferenceSwitchPolarity = 210
            RightStopSwitch = 211
            LeftStopSwitch = 212
            HomeStopSwitch = 213
            SwitchPullupEnable = 214

            # Debug values
            DebugValue0 = 240
            DebugValue1 = 241
            DebugValue2 = 242
            DebugValue3 = 243
            DebugValue4 = 244
            DebugValue5 = 245
            DebugValue6 = 246
            DebugValue7 = 247
            DebugValue8 = 248
            DebugValue9 = 249
            EnableDriver = 255

        class ENUM:
            COMM_MODE_DISABLED = 0
            COMM_MODE_OPENLOOP = 1
            COMM_MODE_DIGITAL_HALL = 2
            COMM_MODE_ABN_ENCODER = 3

            ENCODER_INIT_ESTIMATE_OFFSET = 0
            ENCODER_INIT_USE_HALL = 2

    class GP:
        SerialBaudRate = 65
        SerialAddress = 66
        CANBitRate = 69
        CANsendID = 70
        CANreceiveID = 71
        TelegramPauseTime = 75
        SerialHostAddress = 76
        AutoStartMode = 77
