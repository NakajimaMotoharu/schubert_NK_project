"""Replay only the previously failed SpotBugs phase with the declared analysis annotation jar."""
import gzip
from pathlib import Path
import runpy
from zipfile import ZipFile

HERE=Path(__file__)
M=runpy.run_path(str(HERE.with_name('5224_f03_storage_bootstrap_module_static.py')))
H,E=M['H'],M['E']
ref,read,save=M['ref'],M['load'],M['save']
TYPES={'edu.umd.cs.findbugs.annotations.SuppressFBWarnings','edu.umd.cs.findbugs.annotations.SuppressMatchType'}


def main():
    start=read(next(H.glob('504_*')))
    old=(E/start['values']['run']).resolve()
    cfg=read(old/'begin.json')
    failed=read(old/'spotbugs-exit.json')
    prior_success=read(Path(start['values']['oracleReferences'][5]['path']))
    build=M['G']['revalidate_reference'](start['values']['oracleReferences'][0])
    workspace,sources,peers,poms=M['verify_build'](build)
    assert cfg['inputs']==sources and cfg['rootAndPeerPoms']==poms
    assert (failed['actualExit'],cfg['scope'])==(2,['storage','bootstrap'])
    assert M['sha'](gzip.decompress(Path(failed['stderr']['archive']['path']).read_bytes()))==failed['stderr']['exactSha256']
    old_report=M['ET'].parse(old/'spotbugs.xml').getroot()
    assert {x.text for x in old_report.findall('.//MissingClass')}==TYPES
    old_cmd=failed['command']
    assert old_cmd==cfg['exactCommands']['spotbugs']
    plugin=Path(M['TOOL']/'m2/repository/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar')
    previous_aux=Path(start['values']['oracleReferences'][5]['path']).with_name('fresh-aux.txt')
    assert str(plugin) in previous_aux.read_text().splitlines()
    assert str(plugin) in old_cmd[old_cmd.index('-cp')+1].split(':')
    assert ref(plugin) in cfg['toolAndRulePins']
    assert prior_success['stages']['bootstrap-spotbugs']['actualExit']==0
    with ZipFile(plugin) as jar:
        assert {x.replace('.','/')+'.class' for x in TYPES}<=set(jar.namelist())
    out=(E/'PG39812-f03-storage-bootstrap-annotation-peer-v1').resolve()
    aux_text=(old/'spotbugs-aux.txt').read_text()
    assert str(plugin) not in aux_text
    out.mkdir()
    new_aux=out/'spotbugs-aux.txt'
    new_aux.write_text(aux_text+str(plugin)+'\n')
    new_xml=out/'spotbugs.xml'
    cmd=[str(new_aux) if arg==str(old/'spotbugs-aux.txt') else str(new_xml) if arg==str(old/'spotbugs.xml')
         else arg for arg in old_cmd]
    assert len([1 for a,b in zip(old_cmd,cmd,strict=True) if a!=b])==2
    save(out/'begin.json',dict(command=cmd,currentInputs=ref(old/'begin.json'),fromFailure=ref(old/'spotbugs-exit.json'),
                               originalReport=ref(old/'spotbugs.xml'),onlyAdditionalAux=ref(plugin),
                               types=sorted(TYPES),productionCoreMain=build['sourceCore']))
    _,stage=M['run']('spotbugs',cmd,out,workspace)
    physical=set().union(*(build['physicalClassHashes'][m] for m in M['MODULES']))
    result=M['parse_report']('spotbugs',new_xml,workspace,sources,physical)
    M['verify_build'](build)
    success=(stage['actualExit']==0 and result.get('exactPhysical') and
             all(result.get(k)==0 for k in ('findings','errors','missingClasses')))
    save(out/'manifest.json',dict(actualExit=stage['actualExit'],achieved=success,source=build['sourceCore'],
        startedFrom=ref(old/'manifest.json'),previousExit=2,previousMissingClasses=2,
        staticReport=result,independentProcess=ref(out/'spotbugs-exit.json'),onlyAdditionalAux=ref(plugin),
        tests=0,productActions=0,analyzerRetryCount=1,changedProductFiles=0,newSuppressions=0,
        includesActualNativeOrRoot=False,verifier=ref(HERE),terminalAtUTC=M['utc']()))
    print(stage['actualExit'],result)
    return 0 if success else 1


if __name__=='__main__':
    raise SystemExit(main())
