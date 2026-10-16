"""Actual bootstrap child manager/NSS read cost, no Child/Root authentication or action."""
import inspect
import pg4394_root_read_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4402-child-unit-read-cost-v1'


def java():
    raw = previous.JAVA.replace('package dev.codex.schubert.nk.batch.platform;', 'package dev.codex.schubert.nk.bootstrap;')
    raw = raw.replace('RootReadCost', 'ChildUnitReadCost')
    raw = once(raw, 'var io=new RootStartupContext.NativeIo();', 'var io=new ChildStartupContext.NativeIo();')
    raw = raw.replace('io.procFilesystem()', 'io.filesystem()')
    raw = once(raw, 'measure("productionNativeIoUnitRead",()->io.unit(RootStartupContext.Service.MORNING))',
               'measure("productionChildUnitRead",()->io.maintenanceUnit(ChildStartupContext.MaintenanceParent.MORNING))')
    return raw


def payload():
    raw = previous.payload()
    raw = once(raw, 'JAVA=' + repr(previous.JAVA), 'JAVA=' + repr(java()))
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    raw = raw.replace('RootReadCost.java', 'ChildUnitReadCost.java')
    return raw.replace('dev.codex.schubert.nk.batch.platform.RootReadCost', 'dev.codex.schubert.nk.bootstrap.ChildUnitReadCost')


def main():
    ns = {**vars(previous.previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.previous.main), '<actual fixed child data read>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
