Version 0.6.1
=============

- **New features**:
  -----------------
  - [**Controller**]        Added method drives_ids to get all pair of enclosure:drive_id

- **Fixes**:
  ----------
  - [**Controller**]        Fixed device count on controller.create_vd. Requested in [#2](https://github.com/Naudit/pystorcli2/issues/2)
  - [**Controller**]        Fixed default pd on controller.create_vd in some scenarios. Requested in [#2](https://github.com/Naudit/pystorcli2/issues/2)

Version 0.6.0
=============

- **New features**:
  -----------------
    - Added enclosures, drives and virtualdrives to main __init__.py
    - Increased test coverage
    - [**Storcli**]         Added version properties to storcli class
    - [**Storcli**]         Added property to get the list of controllers
    - [**Controller**]      Method `create_vd` now accepts `PDperArray`. If it is required for some raid types, it is set to #disks//2. Requested in [#2](https://github.com/Naudit/pystorcli2/issues/2)
    - [**DriveMetrics**]    Added vd and vd_id properties to DriveMetrics class
    - [**Drive**]           Added method `set_state` that can be forced. Requested in [#5](https://github.com/Naudit/pystorcli2/issues/5)
    - [**Drive**]           Added class `DriveState` to better manage drive states. Closes [#7](https://github.com/Naudit/pystorcli2/issues/7)
    - [**Drives**]          Added class `Drives` to manage a list of drives. This have been just added to keep the enclosures/virtualdrives working model.

- **Fixes**:
  ----------
    - Package `pystorcli2` installs packages `pystorcli` and `pystorcli2` for backward compatibility. This is a temporary fix until all the projects using `pystorcli` are updated to use `pystorcli2`. The package `pystorcli` will be removed in the future. Contents of `pystorcli` and `pystorcli2` are the same.
    Requested in [#1](https://github.com/Naudit/pystorcli2/issues/1)
    - Fixed variable `__all__` in project `__init__.py`
    - [**Storcli**]         Fixed issue with `get_controllers` method. Requested in [#6](https://github.com/Naudit/pystorcli2/issues/6)
    - [**Storcli**]         Fixed (some) calls when storcli rejects returning jsons. Requested in [#8](https://github.com/Naudit/pystorcli2/issues/8)
    - [**Controller**]      Fixed issue with `create_vd` method. Now it is possible to create a virtual drive with a specific number of physical drives per array. Requested in [#2](https://github.com/Naudit/pystorcli2/issues/2)
    - [**Drive**]           Fixed issue with `set_state` method & property. Requested in [#5](https://github.com/Naudit/pystorcli2/issues/5)
    - [**Binaries**][**metric**]: fixed library calls
    - Other minor fixes


- **Breaking changes**
  --------------------
    - Supported python versions are now 3.8 and onwards
    - Slowly we are migrating to python3-typed classes. This have changed types in many clases and more is coming in future versions.
      If you found any issue (typing error), please report it and we'll fix it as soon as possible.
    - Migrated from setup.py to pyproject.toml
    - [**Enclosure**]        Drive list is now a *`Drives` object* instead of a *list of `Drive`* objects

Thanks to @ulmitov for the contributions to this release


Version 0.5.0
=============
- **New features**:
  -----------------
    - Added some code tests
    - Added coverals to ci

- **Fixes**:
  ----------
    - Fixed some issues with python<3.9
    - fixing listing controllers when there is no controllers

Version 0.3.7
=============
- Minnor code fixes
- Changed maintainer to *Rafael Leira* & *Naudit HPCN S.L*.
- pystorcli is renamed to pystorcli2
- Change license to BSD

Version 0.3.6
=============
- [virtualdrive] fix pdcache getter and setter docstring

Version 0.3.5
=============
- [bin] [metrics] add smart and predictive failure to the drive metrics

Version 0.3.4
=============
- [bin] [metrics] fix missing cachevault
- [enclosure] change way of getting disk slot ids
- [storcli] fix singleton binary override
- [all] suppressing exception context for StorCliMissingError

Version 0.3.2
=============
- install pystorcli-metrics script
- [bin] add pystorcli-metrics script for printing base storcli json metrics
- [controller] fix physical_drives_non_optimal metric

Version 0.3.1
=============
- [all] consolidate all metrics as string

Version 0.3.0
=============
- Add option for StorCLI thread safe singleton class instance and resposne caching

Version 0.2.3
=============
- [enclosure] fix 2 has_drives method

Version 0.2.2
=============
- [enclosure] fix has_drives method

Version 0.2.1
=============
- [all] rework exceptions & and add object self existance check

Version 0.1.0
=============
- [cachevault] add another abstract object CacheVault
- [virtualdrive] consolidate state output
- [vd / enclosure] add has_* method to verify presence of the next level objects in storctl hierarchy
- [controller / vd / drive / enclosure] fix args modification - create deep copy of args first
- [controller / vd / drive] add basic metrics
- [all] fix docstrings

Version 0.0.5
=============
- [drive] fix comment typo
- [drive] fix create hotspare dgs and enclaffinity options

Version 0.0.2
=============
- [drive] create hotspare add enclousure affinity option
