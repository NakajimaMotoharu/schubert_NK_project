"""Bind the actual range exec to an independent CRC and qualify historical proof applicability."""

from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path('evidence/01_PT/018_NK-OPS-001')
H = runpy.run_path(str(Path(__file__).with_name('5609_scr012_count_underclaim.py')))
pin, read, sha = (H[key] for key in ('pin','read','sha'))
crc64 = runpy.run_path(str(Path(__file__).with_name('5593_p01808_original_name_binding.py')))['class_id']


def main():
    actual, = (ROOT/'evidence').glob('PG41190-*/manifest.json')
    old156, = (ROOT/'evidence').glob('PG37652-*/manifest.json')
    original = read(actual)
    quoted156 = read(old156)
    assert quoted156['actualExit']==0 and quoted156['tests']==156
    assert all(row['classname'].startswith('dev.codex.schubert.nk.protocol.') for row in quoted156['cases'])
    group = original['stages']['compile']['command']
    prior = read(Path(original['sharedEarlierInputs']['path']))
    earlier = prior['allPhysicalHashes']
    physical = original['physical']
    measured = original['actualProbeRecords']
    regenerated = []
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-range-crc-post-') as directory:
        base = Path(directory)
        for flags in ((),('-g',),('-g','-parameters')):
            out = base/('default' if not flags else str(len(flags)))
            out.mkdir()
            cmd = [*group]
            cmd[cmd.index('-d')+1] = str(out)
            cmd[1:1] = flags
            proc = subprocess.run(cmd,capture_output=True,timeout=30)
            assert proc.returncode==0,proc.stderr
            data = {name:(out/name).read_bytes() for name in physical}
            hashes = {name:sha(blob) for name,blob in data.items()}
            main = next(blob for name,blob in data.items() if name.endswith('/HttpByteRangeParser.class'))
            new_crc = f'{crc64(main):016x}'
            if not flags:
                assert hashes==physical
                assert int(new_crc,16)==int(measured['crc64'],16)
            regenerated.append(dict(flags=flags,compileExit=proc.returncode,
                exactMatchesToPrevious=sum(earlier[k]==h for k,h in hashes.items()),projectionCrc=new_crc))
    output = ROOT/'evidence/PG41192-range-long-cap-independent-v1'
    output.mkdir()
    manifest = output/'manifest.json'
    value = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                 testId=original['testId'],sameRunProof=pin(actual),physical=5,
                 independentRuntimeCrcMatches=True,compilationConfigurations=regenerated,
                 original156=pin(old156),original156Category='Protocol layout/codec namespace only',
                 scr012CheckedCasesInOriginal156=0,localProductTestsReplayed=0,knownNativeActions=0,
                 whole451=False,formalDelta=0)
    with manifest.open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(manifest),regenerated)


if __name__=='__main__':
    main()
