# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI drive states
'''

from enum import Enum


class DriveState(Enum):
    """Drive status
    """
    # From storcli 7.1704
    # EID=Enclosure Device ID|Slt=Slot No|DID=Device ID|DG=DriveGroup
    # DHS=Dedicated Hot Spare|UGood=Unconfigured Good|GHS=Global Hotspare
    # UBad=Unconfigured Bad|Sntze=Sanitize|Onln=Online|Offln=Offline|Intf=Interface
    # Med=Media Type|SED=Self Encryptive Drive|PI=Protection Info
    # SeSz=Sector Size|Sp=Spun|U=Up|D=Down|T=Transition|F=Foreign
    # UGUnsp=UGood Unsupported|UGShld=UGood shielded|HSPShld=Hotspare shielded
    # CFShld=Configured shielded|Cpybck=CopyBack|CBShld=Copyback Shielded
    # UBUnsp=UBad Unsupported|Rbld=Rebuild

    DHS = 'Dedicated Hot Spare'
    UGood = 'Unconfigured Good'
    GHS = 'Global Hotspare'
    UBad = 'Unconfigured Bad'
    Sntze = 'Sanitize'
    Onln = 'Online'
    Offln = 'Offline'
    Failed = 'Failed'
    SED = 'Self Encryptive Drive'
    UGUnsp = 'UGood Unsupported'
    UGShld = 'UGood shielded'
    HSPShld = 'Hotspare shielded'
    CFShld = 'Configured shielded'
    Cpybck = 'CopyBack'
    CBShld = 'Copyback Shielded'
    UBUnsp = 'UBad Unsupported'
    Rbld = 'Rebuild'
    Missing = 'Missing'
    JBOD = 'JBOD'

    def __str__(self) -> str:
        return self.value

    def is_good(self) -> bool:
        """Check if drive is good according to status"""
        good_states = [
            DriveState.DHS,
            DriveState.UGood,
            DriveState.GHS,
            # DriveState.Sntze, ??
            DriveState.Onln,
            DriveState.SED,
            # DriveState.UGUnsp, ??
            DriveState.UGShld,
            DriveState.HSPShld,
            DriveState.CFShld,
            DriveState.Cpybck,
            DriveState.CBShld,
            DriveState.Rbld,
            DriveState.JBOD
        ]

        return self in good_states

    def is_configured(self) -> bool:
        """Check if drive is configured according to status"""
        configured_states = [
            DriveState.DHS,
            DriveState.GHS,
            # DriveState.Sntze, ??
            DriveState.Onln,
            DriveState.SED,
            # DriveState.UGShld, ??
            DriveState.HSPShld,
            DriveState.CFShld,
            DriveState.Cpybck,
            DriveState.CBShld,
            DriveState.Rbld,
            DriveState.JBOD
        ]

        return self in configured_states

    def is_settable(self) -> bool:
        """Check if this status can be directly set. Not all statuses can be set directly."""
        # online | offline | missing | good

        settable_states = [
            DriveState.Onln,
            DriveState.Offln,
            DriveState.Missing,
            DriveState.UGood,
            DriveState.JBOD
        ]

        return self in settable_states

    def settable_str(self) -> str:
        """Get string representation of settable status. Storcli uses different strings for set command than for show command."""
        if self == DriveState.Onln:
            return 'online'
        elif self == DriveState.Offln:
            return 'offline'
        elif self == DriveState.Missing:
            return 'missing'
        elif self == DriveState.UGood:
            return 'good'
        elif self == DriveState.JBOD:
            return 'jbod'
        else:
            raise ValueError('This status is not settable')

    @staticmethod
    def from_string(status: str) -> 'DriveState':
        """Get DriveState from string"""

        alias = {
            'good': DriveState.UGood,
            'bad': DriveState.UBad,
            'dedicated': DriveState.DHS,
            'hotspare': DriveState.GHS,
            'unconfigured': DriveState.UGood,
            'unconfigured(good)': DriveState.UGood,
            'unconfigured(bad)': DriveState.UBad,
        }

        # check for direct match
        for drive_status in DriveState:
            if drive_status.name.lower() == status.lower() or drive_status.value.lower() == status.lower():
                return drive_status

        # check for alias
        if status.lower() in alias:
            return alias[status.lower()]

        raise ValueError('Invalid drive status: {0}'.format(status))
