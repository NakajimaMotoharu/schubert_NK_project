"""Eight existing Test SHA changes, with explicit independent baseline new2 accounting supplement."""
import sys
import f03_literal_batch_trace as core
from pg13243_business_delivery_baseline_refinement import trace_cfg
import g07_host_class_provenance_inputs as data

SOURCE = 'db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
NORMAL = '73d770b42807892d7b39bdc6d7da6d45e73857c152cb6aace83c0387e3239496'
PROOF = 'afa841e05d261034c489b8086937515390f48348022d2f8c9c133549cecd5b04'

def configuration():
    data.read_checked(data.BASE/'PG13243-business-delivery-baseline-refinement-v1/manifest.json','d31e0979ee6ca7808e165673b763ee16d2e401faef05bd31b5ac22fc2463960f')
    return trace_cfg()

def state_after():
    return core.state_after(configuration())

def static_guard():
    value = data.read_checked(data.BASE/'PG13247-business-delivery-literal-v1/manifest.json','e902b285cdb46dba155084e9c94311575b2f6734f1e8dbf855704ee41bb5ff6b')
    assert value['source'] == SOURCE and value['actualExit'] == value['currentMissingClasses'] == value['currentAnalysisErrors'] == value['currentBugs'] == 0
    assert value['fullPhysicalMain'] == 1843 and value['metadataNegativeVectors'] == 8

if __name__ == '__main__':
    cfg = configuration();static_guard()
    if sys.argv[1:] == ['--emit-patch']:print(core.emit(cfg,SOURCE,NORMAL,PROOF),end='')
    else:assert not sys.argv[1:];core.main(cfg,SOURCE,NORMAL,PROOF)
