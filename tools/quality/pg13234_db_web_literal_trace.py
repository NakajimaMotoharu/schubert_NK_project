"""Six existing Test SHA overlay changes only; preserve canonical ownership, cost and old runtime."""
import sys
import pg13223_db_web_literal_config as cfg
import f03_literal_batch_trace as core
import g07_host_class_provenance_inputs as data

SOURCE = '1762d68747c3460afd90a03377858572dfc25931'
NORMAL = '3919599fe1f9798297a75b209802f656f3af603af3ed0df21f114e1dc0c39e74'
PROOF = '831b167d07a65a79ca3df889b26ca36423c50c055a88a559cdd8d53ce4f6860e'

def state_after():
    return core.state_after(cfg)

def static_guard():
    value = data.read_checked(data.BASE/'PG13233-db-web-literal-v1/manifest.json','a32d5d6fc28df9fb963b6ea3216074836caee553911ddd5c70e310895ee14d6f')
    assert value['source'] == SOURCE and value['actualExit'] == value['currentMissingClasses'] == value['currentAnalysisErrors'] == value['currentBugs'] == 0
    assert value['fullPhysicalMain'] == 1843 and value['metadataNegativeVectors'] == 8

if __name__ == '__main__':
    static_guard()
    if sys.argv[1:] == ['--emit-patch']:print(core.emit(cfg,SOURCE,NORMAL,PROOF),end='')
    else:assert not sys.argv[1:];core.main(cfg,SOURCE,NORMAL,PROOF)
