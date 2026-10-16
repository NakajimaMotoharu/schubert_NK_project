"""Publish only safe original build/independent/static count/hash reports, never raw logs."""
import datetime
import hashlib
import json
import os
from pg4694_ssc299_full import SOURCE, ROOT, W
from pg4702_ssc299_signed_candidate import validate_gate


def main():
    paths = {'whole.json': W/'pg4694-ssc299-six-v1/manifest.safe.json',
             'qualification.json': W/'pg4696-ssc299-whole-qualified-v1/manifest.safe.json',
             'static.json': W/'pg4700-ssc299-static-v1/manifest.safe.json'}
    inputs = {n: json.loads(p.read_bytes()) for n,p in paths.items()}
    if any(type(v['actualExit']) is not int or v['actualExit'] != 0 for v in inputs.values()):
        raise ValueError('every original result must have genuine zero')
    gate = validate_gate(inputs['qualification.json'], SOURCE)
    whole, diagnostic = inputs['whole.json'], inputs['static.json']
    if (whole['source'] != SOURCE or whole['result']['sourceInputsUnchanged'] is not True
            or whole['result']['tests'] != 3739 or diagnostic['productionSource'] != SOURCE
            or diagnostic['result']['sameCurrentSixJarAbi'] is not True):
        raise ValueError('same immutable source, exact original whole, current ABI diagnostic')
    os.umask(0o077)
    out = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4697-ssc299-whole-v1'
    out.mkdir()
    hashes = {}
    for name,value in inputs.items():
        # These reports consist of code/test/XML/ABI/rule hashes and counters only.
        # Private Maven/SQL/native/session/credential payloads are never copied.
        encoded = json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2).encode()+b'\n'
        with (out/name).open('xb') as handle:
            handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
        hashes[name] = hashlib.sha256(encoded).hexdigest()
    result = {'source':SOURCE,'run':'PG4694-six-v1','originalExec':11464,'independentExec':82351,
              'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'originalActualExit':0,'independentActualExit':0,'wholeReplayed':False,
              'tests':3739,'suites':549,'mainClasses':1646,'unchangedPhysicalClasses':1638,
              'modifiedClasses':6,'addedInternalInterfaces':2,'FESFlakyNotRun':0,'spotbugsSixModules':0,
              'coverage':gate['coverage'],'allFour100':False,'nativePending':True,
              'pmdRaw':diagnostic['result']['pmd']['rawFindings'],
              'pmdProcessingErrors':diagnostic['result']['pmd']['processingErrors'],
              'checkstyleFindings':diagnostic['result']['checkstyle']['findings'],
              'allSixFormatBeforeAnyPt':False,'formatOrderIssue':'BUG1381/YKT1147',
              'F03Accepted':False,'formalAccepted':False,'formalTests':1964,'formalScopes':53,
              'effortCompletion':None,'QA051final':'HELD','files':hashes,
              'originalInputSha256':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}}
    with (out/'manifest.json').open('x') as handle:
        json.dump(result,handle,ensure_ascii=False,sort_keys=True,indent=2);handle.write('\n');handle.flush();os.fsync(handle.fileno())
    print(json.dumps({'actualExit':0,'publicManifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'tests':3739,'formalAccepted':False}))
    return 0


if __name__=='__main__':raise SystemExit(main())
