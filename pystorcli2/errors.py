from enum import Enum

from typing import Union

# Got from: https://techdocs.broadcom.com/us/en/storage-and-ethernet-connectivity/enterprise-storage-solutions/12gbs-megaraid-tri-mode-software/1-0/v11685216/v11685227.html


class StorcliError(Enum):
    """ StorCLI error codes """
    SERROR_0 = (
        0, '', 'Command completed successfully.')
    SERROR_1 = (
        1, '', 'Invalid command.')
    SERROR_2 = (
        2, '', 'DCMD opcode is invalid.')
    SERROR_3 = (
        3, '', 'Input parameters are invalid.')
    SERROR_4 = (
        4, '', 'Invalid sequence number.')
    SERROR_5 = (
        5, '', 'Abort is not possible for the requested command.')
    SERROR_6 = (
        6, '', 'Application \'host\' code not found.')
    SERROR_7 = (
        7, '', 'Application already in use - try later.')
    SERROR_8 = (
        8, '', 'Application not initialized.')
    SERROR_9 = (
        9, '', 'Given array index is invalid.')
    SERROR_10 = (
        10, '', 'Unable to add the missing drive to array, as row has no empty slots.')
    SERROR_11 = (
        11, '', 'Some of the CFG resources conflict with each other or the current config.')
    SERROR_12 = (
        12, '', 'Invalid device ID / select-timeout.')
    SERROR_13 = (
        13, '', 'Drive is too small for the requested operation.')
    SERROR_14 = (
        14, '', 'Flash memory allocation failed.')
    SERROR_15 = (
        15, '', 'Flash download already in progress.')
    SERROR_16 = (
        16, '', 'Flash operation failed.')
    SERROR_17 = (
        17, '', 'Flash image was bad.')
    SERROR_18 = (
        18, '', 'Downloaded flash image is incomplete.')
    SERROR_19 = (
        19, '', 'Flash OPEN was not done.')
    SERROR_20 = (
        20, '', 'Flash sequence is not active.')
    SERROR_21 = (
        21, '', 'Flush command failed.')
    SERROR_22 = (
        22, '', 'Specified application does not have host-resident code.')
    SERROR_23 = (
        23, '', 'LD operation not possible - CC is in progress.')
    SERROR_24 = (
        24, '', 'LD initialization in progress.')
    SERROR_25 = (
        25, '', 'LBA is out of range.')
    SERROR_26 = (
        26, '', 'Maximum LDs are already configured.')
    SERROR_27 = (
        27, '', 'LD is not OPTIMAL.')
    SERROR_28 = (
        28, '', 'LD Rebuild is in progress.')
    SERROR_29 = (
        29, '', 'LD is undergoing reconstruction.')
    SERROR_30 = (
        30, '', 'LD RAID level is wrong for the requested operation.')
    SERROR_31 = (
        31, '', 'Too many spares assigned.')
    SERROR_32 = (
        32, '', 'Scratch memory not available, try the command again later.')
    SERROR_33 = (
        33, '', 'Error writing MFC data to SEEPROM.')
    SERROR_34 = (
        34, '', 'Required HW is missing (for example, Alarm or BBU).')
    SERROR_35 = (
        35, '', 'Item not found.')
    SERROR_36 = (
        36, '', 'LD drives are not within an enclosure.')
    SERROR_37 = (
        37, '', 'PD CLEAR operation is in progress.')
    SERROR_38 = (
        38, '', 'Unable to use SATA(SAS) drive to replace SAS(SATA).')
    SERROR_39 = (
        39, '', 'Patrol Read is disabled.')
    SERROR_40 = (
        40, '', 'Given row index is invalid.')
    SERROR_45 = (
        45, '', 'SCSI command done, but non-GOOD status was received-see mf.hdr.extStatus for SCSI_STATUS.')
    SERROR_46 = (
        46, '', 'IO request for MFI_CMD_OP_PD_SCSI failed - see extStatus for DM error.')
    SERROR_47 = (
        47, '', 'Matches SCSI RESERVATION_CONFLICT.')
    SERROR_48 = (
        48, '', 'One or more of the flush operations failed.')
    SERROR_49 = (
        49, '', 'Firmware real-time currently not set.')
    SERROR_50 = (
        50, '', 'Command issues while firmware is in the wrong state (for example, GET RECON when op not active).')
    SERROR_51 = (
        51, '', 'LD is not OFFLINE - IO not possible.')
    SERROR_52 = (
        52, '', 'Peer controller rejected request (possibly due to a resource conflict).')
    SERROR_53 = (
        53, '', 'Unable to inform peer of communication changes (retry might be appropriate).')
    SERROR_54 = (
        54, '', 'LD reservation already in progress.')
    SERROR_55 = (
        55, '', 'I2C errors were detected.')
    SERROR_56 = (
        56, '', 'PCI errors occurred during XOR/DMA operation.')
    SERROR_57 = (
        57, '', 'Diagnostics failed, see the event log for details.')
    SERROR_58 = (
        58, '', 'Unable to process command as boot messages are pending.')
    INCOMPLETE_FOREIGN_CONFIGURATION = (
        59, 'Incomplete foreign configuration', 'Returned in case if foreign configurations are incomplete.')
    SERROR_61 = (
        61, '', 'Returned when a command is tried on unsupported hardware.')
    SERROR_62 = (
        62, '', 'CC scheduling is disabled.')
    SERROR_63 = (
        63, '', 'PD CopyBack operation is in progress.')
    SERROR_64 = (
        64, '', 'Selected more than one PD per array.')
    SERROR_65 = (
        65, '', 'Microcode update operation failed.')
    SERROR_66 = (
        66, '', 'Unable to process the command as the drive security feature is not enabled.')
    SERROR_67 = (
        67, '', 'Controller already has a lock key.')
    SERROR_68 = (
        68, '', 'Lock key cannot be backed-up.')
    SERROR_69 = (
        69, '', 'Lock key backup cannot be verified.')
    SERROR_70 = (
        70, '', 'Lock key from backup failed verification.')
    SERROR_71 = (
        71, '', 'Rekey operation not allowed, unless controller already has a lock key.')
    SERROR_72 = (
        72, '', 'Lock key is not valid, cannot authenticate.')
    SERROR_73 = (
        73, '', 'Lock key from escrow cannot be used.')
    SERROR_74 = (
        74, '', 'Lock key backup (pass-phrase) is required.')
    SERROR_75 = (
        75, '', 'Secure LD exists.')
    SERROR_76 = (
        76, '', 'LD secure operation is not allowed.')
    SERROR_77 = (
        77, '', 'Reprovisioning is not allowed.')
    SERROR_78 = (
        78, '', 'Drive security type (FDE or non-FDE) is not appropriate for the requested operation.')
    SERROR_79 = (
        79, '', 'LD encryption type is not supported.')
    SERROR_80 = (
        80, '', 'Cannot mix FDE and non-FDE drives in same array.')
    SERROR_81 = (
        81, '', 'Cannot mix secure and unsecured LD in same array.')
    SERROR_82 = (
        82, '', 'Secret key not allowed.')
    SERROR_83 = (
        83, '', 'Physical device errors were detected.')
    SERROR_84 = (
        84, '', 'Controller has LD cache pinned.')
    SERROR_85 = (
        85, '', 'Requested operation is already in progress.')
    SERROR_86 = (
        86, '', 'Another power state set operation is in progress.')
    SERROR_87 = (
        87, '', 'Power state of device is not correct.')
    SERROR_88 = (
        88, '', 'No PD is available for patrol read.')
    SERROR_89 = (
        89, '', 'Controller reset is required.')
    SERROR_90 = (
        90, '', 'No EKM boot agent detected.')
    SERROR_91 = (
        91, '', 'No space on the snapshot repository VD.')
    SERROR_92 = (
        92, '', 'For consistency SET PiTs, some PiT creations might fail and some succeed.')
    SERROR_93 = (
        93, '', 'Secondary iButton cannot be used and is incompatible with controller.')
    SERROR_94 = (
        94, '', 'PFK does not match or cannot be applied to the controller.')
    SERROR_95 = (
        95, '', 'Maximum allowed unconfigured (configurable) PDs exist.')
    SERROR_96 = (
        96, '', 'IO metrics are not being collected.')
    SERROR_97 = (
        97, '', 'AEC capture must be stopped before proceeding.')
    SERROR_98 = (
        98, '', 'Unsupported level of protection information.')
    SERROR_99 = (
        99, '', 'PDs in LD have incompatible EEDP types.')
    SERROR_100 = (
        100, '', 'Request cannot be completed because protection information is not enabled.')
    SERROR_101 = (
        101, '', 'PDs in LD have different block sizes.')
    SERROR_102 = (
        102, '', 'LD Cached data is present on a (this) SSCD.')
    SERROR_103 = (
        103, '', 'Config sequence number mismatch.')
    SERROR_104 = (
        104, '', 'Flash image is not supported.')
    SERROR_105 = (
        105, '', 'Controller cannot be online-reset.')
    SERROR_106 = (
        106, '', 'Controller booted to safe mode, command is not supported in this mode.')
    SERROR_107 = (
        107, '', 'SSC memory is unavailable to complete the operation.')
    SERROR_108 = (
        108, '', 'Peer node is incompatible.')
    SERROR_109 = (
        109, '', 'Dedicated hot spare assignment is limited to array(s) with same LDs.')
    SERROR_110 = (
        110, '', 'Signed component is not part of the image.')
    SERROR_111 = (
        111, '', 'Authentication failure of the signed firmware image.')
    SERROR_112 = (
        112, '', 'Flashing was ok but FW restart is not required, ex: No change in FW from current.')
    SERROR_113 = (
        113, '', 'Firmware is in some form of restricted mode, example: passive in A/P HA mode.')
    SERROR_114 = (
        114, '', 'The maximum number of entries are exceeded.')
    SERROR_115 = (
        115, '', 'Cannot start the subsequent flush because the previous flush is still active.')
    SERROR_116 = (
        116, '', 'Status is ok but a reboot is need for the change to take effect.')
    SERROR_117 = (
        117, '', 'Cannot perform the operation because the background operation is still in progress.')
    SERROR_118 = (
        118, '', 'Operation is not possible.')
    SERROR_119 = (
        119, '', 'Firmware update on the peer node is in progress.')
    SERROR_120 = (
        120, '', 'Hidden policy is not set for all of the virtual drives in the drive group that contains this virtual drive.')
    SERROR_121 = (
        121, '', 'Indicates that there are one or more secure system drives in the system.')
    SERROR_122 = (
        122, '', 'Boot LD cannot be hidden.')
    SERROR_123 = (
        123, '', 'The LD count is greater than the maximum transportable LD count.')
    SERROR_124 = (
        124, '', 'DHSP is associated with more than one disk group. Force is needed if dcmd.mbox.b[5] is 0.')
    SERROR_125 = (
        125, '', 'The operation not possible because the configuration has some LDs in a transport ready state.')
    SERROR_126 = (
        126, '', 'The IO request encountered a SCSI DATA UNDERRUN, MFI_HDR.length. The length is set to bytes transferred.')
    SERROR_127 = (
        127, '', 'Firmware flash is not allowed in the current mode.')
    SERROR_128 = (
        128, '', 'The operation is not possible because the device is in a transport ready state.')
    SERROR_129 = (
        129, '', 'The operation is not possible because the LD is in a transport ready state.')
    SERROR_130 = (
        130, '', 'The operation is not possible because the LD is not in a transport ready state.')
    SERROR_131 = (
        131, '', 'The operation is not possible because the PD in a removal ready state.')
    SERROR_132 = (
        132, '', 'The status is ok, but a host reboot is required for the changes to take effect.')
    SERROR_133 = (
        133, '', 'A microcode update is pending on the device.')
    SERROR_134 = (
        134, '', 'A microcode update is in progress on the device.')
    SERROR_135 = (
        135, '', 'There is a mismatch between the drive type and the erase option.')
    SERROR_136 = (
        136, '', 'The operation is not possible because an automatically created configuration exists.')
    SERROR_137 = (
        137, '', 'A secure EPD or EPD-PASSTHRU device exists.')
    SERROR_138 = (
        138, '', 'The operation is not possible because the host FRU data is invalid.')
    SERROR_139 = (
        139, '', 'The operation is not possible because the controller FRU data is invalid.')
    SERROR_140 = (
        140, '', 'The requested image not found.')
    SERROR_141 = (
        141, '', 'NVCache related error.')
    SERROR_142 = (
        142, '', 'The requested LD size is less than MINIMUM SIZE LIMIT.')
    SERROR_143 = (
        143, '', 'The requested drive count is invalid for this raid level.')
    SERROR_144 = (
        144, '', 'An OEM-specific backplane authentication failure.')
    SERROR_145 = (
        145, '', 'The OEM-specific backplane not found.')
    SERROR_146 = (
        146, '', 'Flashing the image is not possible because the downloaded and running firmware on the controller are same.')
    SERROR_147 = (
        147, '', 'Unmap is not supported on the device or the controller.')
    SERROR_148 = (
        148, '', 'The device does not support the sanitize type that is specified.')
    SERROR_149 = (
        149, '', 'A valid Snapdump is unavailable.')
    SERROR_150 = (
        150, '', 'The Snapdump feature is not enabled.')
    SERROR_151 = (
        151, '', 'The LD or device does not support the requested policy.')
    SERROR_152 = (
        152, '', 'The requested operation cannot be performed because of an existing configuration.')
    SERROR_153 = (
        153, '', 'The status is ok, but a shutdown is required to take effect.')
    SERROR_154 = (
        154, '', 'The PD cannot participate in a RAID configuration.')
    SERROR_155 = (
        155, '', 'Secure boot needs another key slot and the eFUSE is full.')
    SERROR_156 = (
        156, '', 'Clear Snapdump before proceeding.')
    SERROR_157 = (
        157, '', 'The operation is not possible because one or more non unmap drives are used.')
    SERROR_158 = (
        158, '', 'The firmware image will disable the firmware device re-ordering.')
    SERROR_159 = (
        159, '', 'New firmware download is not allowed due to a Secure Boot pending key change.')
    SERROR_160 = (
        160, '', 'DPM only supports in EXT format.')
    SERROR_161 = (
        161, '', 'The NVMe repair command failed.')
    SERROR_162 = (
        162, '', 'The NVMe repair command is already in progress for this device.')
    SERROR_163 = (
        163, '', 'The NVMe repair status displays there is no repair in progress for this device.')
    SERROR_164 = (
        164, '', 'The imported certificate chain failed the firmware validation.')
    SERROR_165 = (
        165, '', 'The contents of the specified slot cannot be altered.')
    SERROR_166 = (
        166, '', 'The import initiated without an export or another import in process.')
    SERROR_167 = (
        167, '', 'Another export operation is in process.')
    SERROR_168 = (
        168, '', 'The configuration page read command failed.')
    SERROR_169 = (
        169, '', 'Failed to authenticate due to an invalid key pair or certificate.')
    SERROR_170 = (
        170, '', 'The certificate page read succeeded, but this page is not yet present in MPB.')
    SERROR_171 = (
        171, '', 'Lock key passphrase is incorrect, the user may retry.')
    SERROR_172 = (
        172, '', 'Lock key passphrase try count is exceeded, a reboot is required.')
    SERROR_173 = (
        173, '', 'The requested operation is not possible because of an active reconstruction.')
    SERROR_174 = (
        174, '', 'The requested operation is not possible as the firmware activation is pending.')
    SERROR_175 = (
        175, '', 'The requested operation is not possible as the PD Sanitize operation is in progress.')
    INVALID_STATUS = (
        255, '', 'Invalid status - used for polling command completion.')

    @property
    def value(self) -> int:
        return self._value_[0]

    @property
    def description(self) -> str:
        if len(self._value_[1]) == 0:
            return self.detailed_description
        else:
            return self._value_[1]

    @property
    def detailed_description(self) -> str:
        return self._value_[2]

    def __str__(self):
        return self.description

    @staticmethod
    def get(value: Union[int, str]):
        """Pass an integer value to get the corresponding error code."""

        for e in StorcliError:
            if e.value == value or e.description == value or e.detailed_description == value:
                return e

        return StorcliError.INVALID_STATUS
