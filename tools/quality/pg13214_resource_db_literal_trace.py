"""Four existing Test SHA changes only, guarded by independent current-source complete static proof."""
import sys
import pg13203_resource_db_literal_config as cfg
import f03_literal_batch_trace as core
import g07_host_class_provenance_inputs as data

SOURCE = '6d7f55c22a3ffec8a9013e706282ac845c595492'
NORMAL = '01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4'
PROOF = 'f0a0817f4a3cbac3d4ebacc267e892b09510c9994cf31daf6c3e1e20821f3a65'

def state_after():
    return core.state_after(cfg)

def static_guard():
    value = data.read_checked(data.BASE/'PG13220-spotbugs-fresh-aux-post-v1/manifest.json','2ac356e6962abdf7208277da575a6213b924809b1d0f09cc80e8f16243454e3b')
    assert value['source'] == SOURCE and value['actualExit'] == value['currentMissingClasses'] == value['currentAnalysisErrors'] == value['currentBugs'] == 0
    assert value['fullPhysicalMain'] == 1843 and value['resolvedOldMissingOccurrences'] == 18

if __name__ == '__main__':
    static_guard()
    if sys.argv[1:] == ['--emit-patch']:print(core.emit(cfg,SOURCE,NORMAL,PROOF),end='')
    else:assert not sys.argv[1:];core.main(cfg,SOURCE,NORMAL,PROOF)
