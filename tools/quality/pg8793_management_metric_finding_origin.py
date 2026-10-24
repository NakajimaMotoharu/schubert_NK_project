"""Map current raw PMD findings to unchanged legacy spans; applicability remains pending."""
import datetime
import difflib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg8791_management_metric_static as current
from host_tool_invocation import capture,verify

host=current.host
OUT=host.BASE/'PG8793-management-metric-finding-origin-v1'
PROOF=host.BASE/'PG8791-management-metric-static-v1/manifest.json'
SHA='a90c75594c92df4ff73aa017a1a6c72eb152b97d32cdbc5df603b02e53990a47'
BEFORE='db9c16e0360d7eeb76850feea93899d7a7f8753f'

def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists() and host.sha(PROOF)==SHA
    proof=json.loads(PROOF.read_text())
    assert proof['source']==current.selected.SOURCE and proof['actualExit']==1
    assert proof['static']['pmd']['findings']==proof['unclassified']==40
    report=current.SLOT/'pmd.xml'
    assert host.sha(report)==proof['static']['pmd']['reportSha256']
    sources={};mapping={}
    for role,path in current.MAIN.items():
        now=(host.ROOT/path).read_text()
        old=subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT,text=True)
        assert host.sha(host.ROOT/path)==proof['sourceHashes'][path]
        first,last=old.splitlines(),now.splitlines()
        equal={}
        for block in difflib.SequenceMatcher(a=first,b=last,autojunk=False).get_matching_blocks():
            for offset in range(block.size):
                equal[block.b+offset+1]=block.a+offset+1
        sources[path]=dict(role=role,sourceSha256=proof['sourceHashes'][path],before=BEFORE,beforeLines=len(first),currentLines=len(last),matchingLines=len(equal))
        mapping[path]=(first,last,equal)
    parsed=[];joined=[]
    for file in ET.parse(report).getroot().findall('{*}file'):
        path=Path(file.attrib['name']).relative_to(host.ROOT).as_posix()
        assert path in sources
        first,last,equal=mapping[path]
        role=sources[path]['role']
        for node in file.findall('{*}violation'):
            row=dict(node.attrib,message=' '.join(''.join(node.itertext()).split()))
            parsed.append(row)
            assert row['package']=='dev.codex.schubert.nk.'+role+'.bootstrap'
            assert row['class']==role.title()+'ManagementServer'
            begin,end=int(row['beginline']),int(row['endline'])
            assert 1<=begin<=end<=len(last)
            old_lines=[equal[line] for line in range(begin,end+1)]
            assert old_lines==list(range(old_lines[0],old_lines[0]+len(old_lines)))
            assert last[begin-1:end]==first[old_lines[0]-1:old_lines[-1]]
            joined.append(dict(index=len(joined)+1,path=path,raw=row,sourceSha256=sources[path]['sourceSha256'],currentSpan=[begin,end],previousSpan=[old_lines[0],old_lines[-1]],sameSourceText=True,applicability='PENDING_INDIVIDUAL_F03_REVIEW_NOT_ZERO_FINDINGS',currentPtPass=False))
    assert parsed==proof['static']['pmd']['rawFindings'] and len(joined)==40
    assert all(host.sha(host.ROOT/path)==row['sourceSha256'] for path,row in sources.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=proof['source'],timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,staticManifestSha256=SHA,pmdReportSha256=proof['static']['pmd']['reportSha256'],sourceRows=sources,findings=joined,rawFindings=40,allOriginsLegacySourceText=True,applicableFindings=None,applicabilityPending=40,pmdQualified=False,productTestsExecuted=0,coverage=None,formalUpdated=False,newAccepted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=40,legacyTextOrigins=40,applicabilityPending=40,pmdQualified=False,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
