"""Record the one older public projection that can be safely compacted."""
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib
import runpy
import subprocess

HERE=Path(__file__).resolve()
BASE=HERE.with_name('5126_g07_preserve_duplicate_text_projections.py')
B=runpy.run_path(str(BASE))
E=B['EVIDENCE']
DOC=Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
OWN='PG38950-g07-new-published-blobs'


def git(*args):
    return subprocess.check_output(['git',*args],timeout=20)


def main():
    start=B['load'](next(DOC.glob('566_*')))
    v=start['values']
    assert git('rev-parse','HEAD').decode().strip()==v['source']
    for row in v['oracleReferences'][:2]:
        assert B['hash_file'](Path(row['path']))==row['sha256']
    old=v['oracleReferences'][2]
    assert hashlib.sha256(git('show',v['source']+':'+old['path'])).hexdigest()==old['sha256']
    output=E/v['run']
    assert not output.exists()
    work=B['RUNS']/OWN.lower()
    assert not (work/'text-projection-retained.tar.gz').exists()
    oids={row['blobOid'] for row in B['load'](work/'projection.json') if row['text']}
    verified=subprocess.run(['git','cat-file','--batch-check=%(objecttype)'],
                             input=''.join(f'{oid}\n' for oid in sorted(oids)).encode(),
                             capture_output=True,check=True,timeout=30)
    assert verified.stdout.splitlines()==[b'blob']*len(oids)
    begin=datetime.now(timezone.utc).isoformat()
    result=B['preserve'](OWN,'manifest.json',1195,legacy=True)
    result.update(run=v['run'],head=v['source'],startEvent=start['eventId'],gitBlobIdentitiesRetained=len(oids),
                  startedAtUTC=begin,terminalAtUTC=datetime.now(timezone.utc).isoformat(),newProductTests=0,
                  scannerReplayed=False,newAcceptance=0,wholeG07Accepted=False,whole451Accepted=False,
                  initialPreparationExit=1,initialPreparationCause='Legacy binary rows are an array, before archive opened',
                  preservationToolSha256=B['hash_file'](BASE))
    assert result['availableAfter']>result['availableBefore']
    output.mkdir()
    B['write'](output/'manifest.json',result)
    print(result['availableBefore'],result['availableAfter'],result['duplicateTextCopiesReleased'],
          B['hash_file'](output/'manifest.json'))


if __name__=='__main__':
    main()
