"""All16 exact exception PG models/ABI, constructor invariants and current-source static gates."""
import inspect
import xml.etree.ElementTree as ET
import pg5744_revocation_static as previous
from exception_private_contract import fields,expected_source,abi_contracts

SLOT='pg5750-exception-static-v1'
SELECTED='pg5748-exception-green-v1'


def target_counter_contract(snapshot):
    target={}
    for path in fields():
        module=path.split('/')[1];member=path.split('/src/main/java/')[1][:-5]
        report=snapshot/('src/'+module+'/target/site/jacoco/jacoco.xml')
        found=[c for c in ET.parse(report).getroot().findall('package/class')if c.get('name')==member]
        if len(found)!=1:raise ValueError('each actual target exception class')
        counters={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in found[0].findall('counter')}
        counters={k:counters.get(k,{'covered':0,'missed':0})for k in('LINE','METHOD','CLASS','BRANCH')}
        if not all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in('LINE','METHOD','CLASS'))or counters['BRANCH']['missed']!=0:raise ValueError('all16 actual four counters100,branchless0/0')
        target[module+':'+member]=counters
    return target


def main():
    raw=inspect.getsource(previous.main)
    replacements={
      "(v['tests'],v['suites'])==(15,7)":"(v['tests'],v['suites'])==(17,13)",
      "p=w/'pg5734-enum48-static-v1/manifest.safe.json'":"p=w/'pg5744-revocation-static-v1/manifest.safe.json'",
      "public=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5734-enum48-static-v1/manifest.json'":"public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5744-revocation-static-v1/manifest.json'",
      '81aa7ea5f48a0c93762d629f43bbdeeb8672a2379a69e175641499b680838e3a':'c85484fba88b1ae8ae84428de88c25eb283597872ead51a5bfc2b09005ab3ffb',
      "oldcp=w/'pg5734-enum48-static-v1/aux-classpath.txt'":"oldcp=w/'pg5744-revocation-static-v1/aux-classpath.txt'",
      "remaining=[r for r in rows if r['sourcePath']==REL and r['rule']=='UnusedNullCheckInEquals']":"remaining=[r for r in rows if r['rule']=='AvoidFieldNameMatchingMethodName']",
      "'changedSourcePaths':[REL]":"'changedSourcePaths':sorted(FIELDS)",
      "'changedPhysicalClasses':[expected_class]":"'changedPhysicalClasses':sorted(expected_classes)",
      "'unchangedPhysicalClasses':1663":"'unchangedPhysicalClasses':1648",
      "'allFieldAndMethodDescriptorsUnchanged':True":"'allPublicMethodDescriptorsUnchanged':True,'privateFieldTypesUnchanged':True,'abi':abi,'inheritedJavaSerializedCompatibilityClaimed':False,'genericRenamerGuardChanged':False",
      "target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5744-revocation-static-v1'":"target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5750-exception-static-v1'"}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('exact current static runner predicate')
        raw=raw.replace(old,new,1)
    a=raw.index('    sources=');b=raw.index("    for name in('pmd.xml','checkstyle.xml'):",a)
    block="""    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(sources)!=849 or set(sources)!=set(old['allSourceHashes'])or set(k for k in sources if sources[k]!=old['allSourceHashes'][k])!=set(FIELDS):raise ValueError('exact16 Main source changes')
    for name in FIELDS:
        before=subprocess.check_output(['git','show',old['source']+':'+name],cwd=ROOT,text=True)
        if expected_source(name,before)!=(snapshot/name).read_text():raise ValueError('only declared private fields plus two constructor null guards')
    current=v['allPhysicalMainSha256'];prior=old['auxClassHashes']
    expected_classes={name.split('/')[1].removeprefix('schubert-nk-')+':'+name.split('/src/main/java/')[1][:-5]+'.class'for name in FIELDS}
    if len(current)!=1664 or set(current)!=set(prior)or set(k for k in current if current[k]!=prior[k])!=expected_classes:raise ValueError('all16 actual class changes,1648 identical')
    abi=abi_contracts(snapshot)
"""
    raw=raw[:a]+block+raw[b:]
    a=raw.index('    coverage=snapshot');b=raw.index('    os.umask',a)
    raw=raw[:a]+"    coverage=snapshot/'src/schubert-nk-web/target/site/jacoco/jacoco.xml'\n    counters=target_counter_contract(snapshot)\n"+raw[b:]
    marker="    done=exits[0]in(0,4)"
    if raw.count(marker)!=1:raise ValueError('exact current static qualifier')
    raw=raw.replace(marker,"    expected_rules=Counter(old['ruleCounts']);del expected_rules['AvoidFieldNameMatchingMethodName']\n    done=Counter(r['rule']for r in rows)==expected_rules and exits[0]in(0,4)",1)
    namespace={**vars(previous),'SELECTED':SELECTED,'SLOT':SLOT,'FIELDS':fields(),'expected_source':expected_source,'abi_contracts':abi_contracts,'target_counter_contract':target_counter_contract}
    exec(compile(raw,'<current16 explicit exception PG and static contracts>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
