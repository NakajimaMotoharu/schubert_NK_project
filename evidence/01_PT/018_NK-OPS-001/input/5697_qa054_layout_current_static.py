"""Check the one changed Protocol source against the pinned stylesheet and typed PMD."""

import importlib.util
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

parent=Path(__file__).with_name('5694_qa054_canonical_rules_protocol_verify.py')
spec=importlib.util.spec_from_file_location('fixed_protocol_run',parent)
h=importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def main():
    pinned=h.read(next((h.OPS/h.RUN).glob('manifest.json')))
    home=h.ROOT.parent/'pgpt-runs/PG379'/h.RUN
    begin=h.read(home/'begin.json')
    assert pinned['source']==begin['source']==h.git('rev-parse','HEAD').decode().strip()
    work=Path(begin['work'])
    source=next(p for p in begin['twoInputDeltas'] if p.endswith('.java'))
    path=work/source
    assert h.pin(path)['sha256']==begin['currentInputs'][source]
    artifact=Path(pinned['currentPackage']['path'])
    assert h.pin(artifact)==pinned['currentPackage']
    binary=work/h.MODULE/'target/classes'
    with ZipFile(artifact) as archive:
        data={n:h.sha(archive.read(n)) for n in archive.namelist() if n.endswith('.class')}
    assert len(data)==176 and all(n.startswith('dev/codex/schubert/nk/protocol/') for n in data)
    assert data=={p.relative_to(binary).as_posix():h.pin(p)['sha256'] for p in binary.rglob('*.class')}
    commands=h.read(next(h.OPS.glob('PG41306-*'))/'manifest.json')['steps']
    old_style=commands['style'].get('argv') or commands['style']['command']
    old_typed=commands['pmd'].get('argv') or commands['pmd']['command']
    listing=home/'pmd-current-source.txt'
    listing.write_text(str(path)+'\n')
    current_pmd=home/'pmd-current.xml'
    candidates=[Path(p) for p in old_typed[12].split(os.pathsep)]
    toolchain=h.ROOT.parent/'toolchain'
    aux=[str(p) for p in candidates if p.is_relative_to(toolchain) and p.name in ('jrt-fs.jar','jspecify-1.0.1.jar')]
    assert len(aux)==2
    new_checkstyle=[*old_style[:7],str(path)]
    new_pmd=[*old_typed[:6],str(listing),*old_typed[7:12],
             os.pathsep.join([*aux,str(binary)]),'--no-cache','--format','xml','--report-file',str(current_pmd)]
    outputs={}
    for stage,argv in (('checkstyle',new_checkstyle),('pmd',new_pmd)):
        r=subprocess.run(argv,capture_output=True,timeout=90)
        text=home/(stage+'.stdout')
        text.write_bytes(r.stdout)
        err=home/(stage+'.stderr')
        err.write_bytes(r.stderr)
        outputs[stage]=dict(argv=argv,exit=r.returncode,stdout=h.pin(text),stderr=h.pin(err))
    cs=ET.parse(home/'checkstyle.stdout').getroot()
    pm=ET.parse(current_pmd).getroot()
    err_nodes=[x for x in pm.iter() if x.tag.rsplit('}',1)[-1] in ('error','configerror')]
    violations=[dict(rule=x.get('rule'),line=x.get('beginline')) for x in pm.iter() if x.tag.rsplit('}',1)[-1]=='violation']
    assert len(cs.findall('file'))==1
    r=dict(source=begin['source'],releaseProof=h.pin(h.OPS/h.RUN/'manifest.json'),actualCommands=outputs,
           sourcePath=source,currentTypedArtifact=h.pin(artifact),checkedPhysicalTypes=176,
           checkstyleFindings=len(cs.findall('.//error')),pmdRaw=len(violations),pmdProcessingErrors=len(err_nodes),
           pmdSites=violations,priorPreflight='Previous auxiliary list included JUnit; no analyzer ran before Main-only admission.',pmdXml=h.pin(current_pmd),newProductTests=0,whole451=False,terminalAtUTC=h.now())
    h.write(h.OPS/h.RUN/'layout-current-static.json',r)
    print('Checkstyle',outputs['checkstyle']['exit'],r['checkstyleFindings'],'PMD',outputs['pmd']['exit'],r['pmdRaw'],r['pmdProcessingErrors'])


if __name__=='__main__':
    main()
