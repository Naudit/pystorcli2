# -*- coding: utf-8 -*-

# Copyright (c) 2023, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI virtual drive access types
'''

from enum import Enum


class VDAccess(Enum):
    """Virtual Drive Access type
    """
    # From storcli 7.1704
    # VD=Virtual Drive| DG=Drive Group|Rec=Recovery
    # Cac=CacheCade|OfLn=OffLine|Pdgd=Partially Degraded|Dgrd=Degraded
    # Optl=Optimal|dflt=Default|RO=Read Only|RW=Read Write|HD=Hidden|TRANS=TransportReady
    # B=Blocked|Consist=Consistent|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack
    # AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
    # EID=Enclosure Device ID|Slt=Slot No|DID=Device ID|DG=DriveGroup

    RO = 'Read Only'
    RW = 'Read Write'
    B = 'Blocked'
    RmvBlkd = 'Remove Blocked'

    def __str__(self) -> str:
        return self.value

    def can_write(self) -> bool:
        """Get if virtual drive is writable"""
        good_states = [
            VDAccess.RW,
        ]

        return self in good_states

    def can_read(self) -> bool:
        """Get if virtual drive is readable"""
        good_states = [
            VDAccess.RW,
            VDAccess.RO,
        ]

        return self in good_states

    def settable_str(self) -> str:
        """Get string representation of settable state. Storcli uses different strings for set command than for show command."""
        if self == VDAccess.RO:
            return 'RO'
        elif self == VDAccess.RW:
            return 'RW'
        elif self == VDAccess.B:
            return 'Blocked'
        elif self == VDAccess.RmvBlkd:
            return 'RmvBlkd'
        else:
            raise ValueError('This status is not settable')

    @staticmethod
    def from_string(status: str) -> 'VDAccess':
        """Get DriveState from string"""
        for vda in VDAccess:
            if vda.name.lower() == status.lower() or vda.value.lower() == status.lower():
                return vda
        raise ValueError(
            'Invalid Virtual Drive Acess code: {0}'.format(status))
