"""Fresh whole-six source/XML/byte/static/session qualification; no old native import."""
import inspect
import pg858_completed_reference_collect as previous

def code():
    raw=inspect.getsource(previous.main)
    replacements=(
      ('pg857-completed-reference-six-host-v1','pg1018-stream-six-host-v2'),
      ('pg854-completed-reference-selected-v4','pg1020-stream-selected-v9'),
      ('pg830-manager-six-host-v1','pg926-body-six-host-v1'),
      ('85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede','4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'),
      ("module=='batch' and any(name.startswith('dev/codex/schubert/nk/batch/file/'+n)for n in ('MaintenanceRunFiles','MorningNewRunAdmission','MorningResumeAdmission'))","module=='batch' and name=='dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader.class'"),
      ('tests==3541 and suites==522','tests==3563 and suites==523'),
      ('2a0d5aa392c85a1dc12a1cdb423978e8500895b8','40ef6e894573d2ffab1d1732124960f9c98d5f97'),
    )
    for a,b in replacements:assert raw.count(a)==1,a;raw=raw.replace(a,b)
    marker="assert sha(base/'jacoco.xml')==sha(current/'site/jacoco/jacoco.xml')"
    extra="""
        for p in reports:
            original=current/'surefire-reports'/p.name
            assert sha(p)==sha(original) and start<=original.stat().st_mtime<=end+1
            r=ET.parse(p).getroot();cases=r.findall('testcase')
            assert len(cases)==int(r.get('tests'))>0
            assert len({(c.get('classname'),c.get('name'))for c in cases})==len(cases)
        if module=='batch':
            item=next(c for c in ET.parse(base/'jacoco.xml').findall('.//class')if c.get('name')=='dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader')
            expected={'LINE':129,'METHOD':20,'CLASS':1,'BRANCH':24}
            for c in item.findall('counter'):
                if c.get('type')in expected:assert int(c.get('missed'))==0 and int(c.get('covered'))==expected[c.get('type')]
"""
    assert raw.count(marker)==1;raw=raw.replace(marker,marker+extra)
    marker="result={'actualExit':0";assert raw.count(marker)==1
    raw=raw.replace(marker,"assert changed==['dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader.class']\n    "+marker)
    return raw

if __name__=='__main__':
    env=dict(previous.__dict__);exec(compile(code(),'<PG1022 actual new source whole-six qualification>','exec'),env);env['main']()
