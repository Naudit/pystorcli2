# -*- coding: utf-8 -*-

# Copyright (c) 2023, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI virtual drive state
'''

from enum import Enum


class VDState(Enum):
    """Virtual Drive State
    """
    # From storcli 7.1704
    # VD=Virtual Drive| DG=Drive Group|Rec=Recovery
    # Cac=CacheCade|OfLn=OffLine|Pdgd=Partially Degraded|Dgrd=Degraded
    # Optl=Optimal|dflt=Default|RO=Read Only|RW=Read Write|HD=Hidden|TRANS=TransportReady
    # B=Blocked|Consist=Consistent|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack
    # AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
    # EID=Enclosure Device ID|Slt=Slot No|DID=Device ID|DG=DriveGroup

    # From old pystorcli: optimal | recovery | offline | degraded | degraded_partially

    Optl = 'Optimal'
    Rec = 'Recovery'
    OfLn = 'OffLine'
    Pdgd = 'Partially Degraded'
    Dgrd = 'Degraded'

    def __str__(self) -> str:
        return self.value

    def is_good(self) -> bool:
        """Get if virtual drive is good"""
        good_states = [
            VDState.Optl,
        ]

        return self in good_states

    @staticmethod
    def from_string(status: str) -> 'VDState':
        """Get DriveState from string"""
        for vd_status in VDState:
            if vd_status.name.lower() == status.lower() or vd_status.value.lower() == status.lower():
                return vd_status
        raise ValueError(
            'Invalid Virtual Drive status code: {0}'.format(status))
