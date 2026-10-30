"""Independently reconstruct current842 from qualified816; bind every physical count to actual closures."""
import copy
from collections import Counter
from contextlib import ExitStack
import json
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14732_current842_incremental_registry import SOURCE,NORMAL,PREVIOUS,PREVIOUS_POST,NEW,require,read

MODULES={m:m for m in ['api','batch','bootstrap','protocol','storage','web']}

def module_for_source(name):
    import re
    require(isinstance(name,str) and re.fullmatch(r'dev/codex/schubert/nk/(api|batch|bootstrap|protocol|storage|web)/(?:[A-Za-z_][A-Za-z0-9_]*/)*[A-Za-z_][A-Za-z0-9_]*',name),'exact package/module/class identity')
    return MODULES[name.split('/')[4]]

def module_prevention():
    for module in MODULES:require(module_for_source('dev/codex/schubert/nk/'+module+'/some/Class')==module,'all six module identities')
    values=['dev/codex/schubert/nk/unknown/Class','other/codex/schubert/nk/batch/Class','dev/codex/schubert/nk/batch','dev/codex/schubert/nk/batch//Class']
    for value in values:
        try:module_for_source(value)
        except ValueError:pass
        else:raise ValueError('module alias admitted')
    return dict(positive=6,negative=len(values))

PIN='aa96fcee286c5ca767581006cf4ed5803d3a9f72e0b9b2d961e79fabd235f096'
OUT=data.BASE/'PG14734-current842-incremental-registry-post-v1'

def wire(value):return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent registry post');module_checks=module_prevention()
    old,prior=read(PREVIOUS),read(PREVIOUS_POST);m=read(('PG14732-current842-incremental-registry-v1',PIN))
    require(prior['actualExit']==old['actualExit']==m['actualExit']==0 and prior['registryManifestSha256']==PREVIOUS[1] and prior['independentReturnedXmlAndJarClosure'] is True and all(wire(prior['summary'][k])==wire(old[k]) for k in prior['summary']),'qualified original816')
    verify(old['invocation']);verify(prior['invocation']);verify(m['invocation'])
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',NORMAL));hashes=normal['begin']['inputHashes']
    require(normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all fixed normal inputs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    expected=copy.deepcopy(old);units=expected['fullSourceUnits'];owners=expected['owners'];meta=expected['metadataClasses'];cases={(v['classname'],v['name']) for v in old['cases']};added=[]
    with ExitStack() as stack:
        jars={module:stack.enter_context(zipfile.ZipFile(j['path'])) for module,j in normal['jars'].items()}
        require(all(data.sha(__import__('pathlib').Path(j['path']).read_bytes())==j['sha256'] for j in normal['jars'].values()),'all six Main jars unchanged')
        for name,(pin,count,suite_count) in NEW.items():
            p=read((name,pin));verify(p['invocation'])
            require(p['actualExit']==0 and p['source']==SOURCE and p['normalManifestSha256']==NORMAL and p['singleSession'] is True and p['crcMismatch']==0 and p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False,'same source/single exec new post')
            local=[]
            for filename,h in p['xmlHashes'].items():
                raw=(data.BASE/name/filename).read_bytes();require(data.sha(raw)==h,'actual returned XML hash')
                root=ET.fromstring(raw);require(int(root.get('tests'))==len(root.findall('testcase')) and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'XML all cases and FES0')
                for case in root.findall('testcase'):
                    require(not list(case),'no non-PASS XML');local.append((case.get('classname'),case.get('name')))
            require(len(local)==len(set(local))==count and len({c for c,n in local})==suite_count and not cases&set(local),'exact unique new methods/suites')
            require(set(local)=={(v['classname'],v['name']) for v in p['cases']} and p.get('originalTestsCountedElsewhere',False) is False,'post matches original, not existing-exec reanalysis')
            cases.update(local);added.extend(local)
            for path,owned in p['owners'].items():
                require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'each canonical/UNKNOWN role independently derived')
                require(path not in owners or owners[path]==owned,'shared owners identical');owners[path]=owned
            physical=set()
            for source,u in p['fullSourceUnits'].items():
                require(source not in units,'no Source exec union');module=module_for_source(source);jar=jars[module]
                closure={n[:-6] for n in jar.namelist() if n==source+'.class' or n.startswith(source+'$') and n.endswith('.class')}
                require(closure==set(u['physical'])==set(p['completeSourceUnitClosure'][source]) and not physical&closure,'exact full Jar closure')
                physical.update(closure)
                totals={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
                for n in closure:
                    raw=jar.read(n+'.class');info=code.decode(raw,n+'.class');record=p['sourcePhysicalInventory'][n]
                    require(data.sha(raw)==p['physicalClasses'][n]==record['sha256'] and all(info[k]==record[k] for k in ['flags','sourceFile','methods']),'actual original class bytecode metadata')
                    if n in p.get('metadataClasses',[]):
                        require(n not in meta and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no metadata duplicate or manual filter')
                        has_code=any(v['hasCode'] for v in info['methods'])
                        if has_code:
                            require(n=='dev/codex/schubert/nk/storage/ServiceCredentialId$1' and info['flags']==4128 and info['sourceFile']=='ServiceCredentialId.java' and info['methods']==[dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True,codeLength=40)],'only actual compiler switch filter, never noCode')
                        else:require(info['flags']==1537 and n.startswith('dev/codex/schubert/nk/storage/ResourceScope$'),'actual abstract ports')
                        meta[n]=dict(kind='COMPILER_SYNTHETIC_STANDARD_FILTER' if has_code else 'NO_CODE',sha256=data.sha(raw),postSha256=pin)
                    else:
                        require(n in p['executable'] and any(v['hasCode'] for v in info['methods']),'actual executable retained')
                        for k,v in p['executable'][n]['counters'].items():
                            for role in ['missed','covered']:totals[k][role]+=v[role]
                require(totals==u['totals'],'unit totals equal every executable physical counter')
                four=all(v['covered']>0 and v['missed']==0 for v in totals.values());no_code=closure<=set(p.get('metadataClasses',[]));natural=not no_code and totals['BRANCH']==dict(covered=0,missed=0)
                require(u['four100'] is four and (not natural or all(totals[k]['covered']>0 and totals[k]['missed']==0 for k in ['LINE','METHOD','CLASS'])),'four100 versus natural0')
                units[source]=dict(post=name,postSha256=pin,physical=u['physical'],counters=totals,four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=no_code,branchNaturallyZero=natural)
            require(physical==set(p['physicalClasses']),'nothing omitted from new Source targets')
            expected['originalPostReferences'].append(dict(name=name,sha256=pin,tests=count,suites=suite_count,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_SCOPED_PT_NOT_WHOLE_451'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREVIOUS),previousRegistryPostReference=list(PREVIOUS_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+len(NEW),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),metadataPhysical=len(meta),generatedMetadataPhysical=sum(v['kind']=='COMPILER_SYNTHETIC_STANDARD_FILTER' for v in meta.values()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),metadataSourcePrograms=sum(u['metadataOnly'] for u in units.values()),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()),totalProductExecs=old['totalProductExecs']+len(NEW),totalMethodExecutions=old['totalMethodExecutions']+len(added),uniqueProductMethodDelta=len(added),sourceProgramDelta=len(units)-len(old['fullSourceUnits']))
    def contract(v):require(wire(v)==wire(expected),'exact independently derived whole registry, types and prior history')
    contract(m)
    require((m['tests'],m['suites'],m['measuredSourcePrograms'],m['measuredPhysical'],m['totalProductExecs'],m['totalMethodExecutions'])==(842,119,206,277,52,898),'observed distinct methods and necessary repeated qualification')
    vectors=[('source','source','OLD'),('methods','tests',872),('suites','suites',108),('exec','originalExecs',44),('four','four100SourcePrograms',189),('natural','naturalZeroBranchSourcePrograms',0),('incomplete','incompleteSourcePrograms',0),('metadata','metadataPhysical',0),('generated','generatedMetadataPhysical',0),('code','executablePhysical',254),('unknown','unknownOwnerPaths',0),('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',50),('history','qualificationReplacedUnitHistory',{}),('qualification','additionalQualificationReferences',[]),('scope','additionalScopeReferences',[]),('context','additionalSourceContractReference',{}),('union','coverageExecUnion',True),('bool','originalTestsReexecutedByRegistry',False)]
    vectors.extend([('four-physical-minus-one','four100Physical',191),('four-code-minus-one','four100ExecutablePhysical',181)])
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false registry accepted '+label)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,moduleMappingChecks=module_checks,registryManifestSha256=PIN,previousRegistryPostSha256=PREVIOUS_POST[1],independentReturnedXmlAndJarClosure=True,originalXmlMethods=len(cases),originalXmlSuites=len({c for c,n in cases}),metadataNegativeVectors=len(labels),negativeLabels=labels,summary={k:m[k] for k in ['tests','suites','originalExecs','measuredSourcePrograms','measuredPhysical','executablePhysical','metadataPhysical','generatedMetadataPhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','metadataSourcePrograms','incompleteSourcePrograms','unknownOwnerPaths','ownerStatusCounts','additionalQualificationExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','sourceProgramDelta']},originalMethodsReexecuted=0,oldSourceTransferred=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
