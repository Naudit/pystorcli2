#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

"""Return json metrics from storcli
"""


import json
import sys

import pystorcli
import pystorcli.controller
import pystorcli.enclosure
import pystorcli.cachevault
import pystorcli.exc


def cachevault_metrics(ctl):
    """Return cache vault metrics

    Returns:
        (dict): cache vault metrics

        "0": {
          "metric": {
            "replacement_required": "no",
            "state": "optimal",
            "temperature": "29",
            "offload_status": "ok"
          }
        }
      },

    """
    try:
        cache_vault = pystorcli.cachevault.CacheVault(ctl.id)
        return {
            '0': {
                'metric': cache_vault.metrics.all
            }
        }
    except pystorcli.exc.StorCliMissingError:
        return {
            '0': {
                'metric': {}
            }
        }


def drive_metrics(drive):
    """Return drive metrics

    Returns:
        (dict): drive metrics

            "metric": {
              "state": "online",
              ...
            }
    """
    return {
        'metric': {
            'state': drive.metrics.state,
            'smart_alert': drive.metrics.smart_alert,
            'predictive_failure': drive.metrics.predictive_failure
        }
    }


def drives_metrics(drives):
    """Return drives metrics

    Returns:
        (dict): drives metrics

            "0": {
              "metric": {
                "state": "online"
              }
            },
            "1": {
              "metric": {
                "state": "online"
              }
            },
    """
    output = {}

    for drive in drives:
        output[drive.id] = drive_metrics(drive)
    return output


def enclosure_metrics(encl):
    """Return enclosure metrics with drives metrics

    Returns:
        (dict): enclosure metrics

        "enclosure": {
          "64": {
            "drive": {
              "0": {
                "metric": {
                  "state": "online"
                }
              },
            ...
            "metrics": {}

    """
    return {
        'metric': {},
        'drive': drives_metrics(encl.drives)
    }


def enclosures_metrics(encls):
    """Return enclosures metrics with drives metrics

    Returns:
        (dict): enclosures metrics

            "enclosure": {
              "64": {
                "drive": {
                  "0": {
                    "metric": {
                      "state": "online",
                      ...
                    },
                    ...
                  },
                  ...
    """
    output = {}

    for encl in encls:
        output[encl.id] = enclosure_metrics(encl)
    return output


def virtual_drives_metrics(vds):
    """Return virtual drives metrics and metrics from other subobjects

    Returns:
        (dict): controllers metrics

            "virtualdrive": {
              "0": {
                "metric": {
                  "state": "optimal",
                  ...
                },
                "enclosure": {
                  "64": {
                    "drive": {
                      "0": {
                        "metric": {
                          "state": "online",
                          ...
                        },
                        ...
                      },
                      ...
                "metric": {
                    "state": "optimal",
                }

    """
    def virtual_drive_metrics(vd):
        enclosures = {}
        for drive in vd.drives:
            if drive.encl_id in enclosures:
                enclosures[drive.encl_id]['drive'].update(
                    {drive.id: drive_metrics(drive)})
            else:
                enclosures[drive.encl_id] = {
                    'drive': {
                        drive.id: drive_metrics(drive)
                    }
                }

        return {
            'metric': vd.metrics.all,
            'enclosure': enclosures
        }

    output = {}

    for vd in vds:
        output[vd.id] = virtual_drive_metrics(vd)
    return output


def controller_metrics(ctl):
    """ Return all controller metrics and metrics from other subobjects

    Returns:
        (dict): controller metrics
    """
    output = {
        ctl.id: {
            'metric': ctl.metrics.all,
            'virtualdrive': virtual_drives_metrics(ctl.vds),
            'enclosure': enclosures_metrics(ctl.encls),
            'cachevault': cachevault_metrics(ctl),
        }
    }

    return output


def controllers_metrics():
    """ Return controllers metrics

    Returns:
        (dict): controllers metrics
    """
    output = {
        'controller': {}
    }

    for ctl in pystorcli.controller.Controllers():
        output['controller'].update(controller_metrics(ctl))
    return output


def main():
    """Return json metrics
    """
    # enable StoreCLI singleton object with resposne cache
    pystorcli.StorCLI.enable_singleton()
    storcli = pystorcli.StorCLI()
    storcli.cache_enable = True

    return json.dumps(controllers_metrics())


if __name__ == '__main__':
    print(main())
    sys.exit(0)
