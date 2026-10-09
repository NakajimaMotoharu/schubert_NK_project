"""New-only stopped current full24, actual closed ExecStart + finitecold explicit."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg784_stopped_baseline.py').read_text().replace('pg784-stopped-current-v1','pg785-stopped-current-v1')
    pure=(R/'pg785_exec_history.py').read_text()
    raw=replace(raw,(('def configuration(unit):',pure+'\ndef configuration(unit):'),
        (" assert actual['ExecStart']==expected['ExecStart']or right[3:]==('n/a','n/a','0','(null)','0/0')",r''' current=h.show(unit)
 capture=base/'pg779-failed758-recovery-v1'/(unit+'.stopped.private')
 closed=json.loads(capture.read_bytes())if capture.exists()else json.loads((base/'pg781-retained779-current-v1/current.private.json').read_bytes())['units'][unit]
 assert accepted(left,right,current,closed)''')))
    return raw


if __name__=='__main__':
    exec(compile(source(),'<new785 actualstopped full capture>','exec'),{'__file__':str(R/'pg785_stopped_baseline.py'),'__name__':'__main__'})
