"""Read new-case original240/33, bind all764 unchanged Main; never combine counters with old536."""
import json
import xml.etree.ElementTree as ET
import pg5122_root_elf_public as public
import pg5164_metadata_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5164-readonly-agent-green-v1'
    actual=json.loads((run/'manifest.safe.json').read_bytes())
    before=json.loads((public.W/'pg5156-native-coverage-green-v2/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['mainDelta']['physicalSha256']!=before['mainDelta']['physicalSha256']:
        raise ValueError('new actual240 with exact all764 unchanged Production class bytes required')
    selected.EXTRA_CHANGED={'bootstrap:dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'}
    child=('childfd009OwnerSetAdoptsBothAndConsumesProofBeforeAdmissionOnce',
           'childfd010OwnerSetCompoundFailuresKeepIndependentPriorityAndBothConsumption')
    overrides={('dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest',name):
       {'testId':'PT-OPS-CHILDFD-'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':False}
       for i,name in enumerate(child,9)}
    overrides[('dev.codex.schubert.nk.bootstrap.NativeCoverageExportTest',
       'nchannel193001ReadOnlyAgentMetadataRequiresExactlyOneLink')]={
       'testId':'PT-NEXPORT193-META001','newIndependentCase':True,'newInThisChange':True}
    path=run/'source/src/schubert-nk-bootstrap/target/site/jacoco/jacoco.xml'
    cls=next(c for c in ET.parse(path).getroot().findall('package/class')
             if c.get('name')=='dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile')
    method=next(m for m in cls.findall('method') if m.get('name')=='checked')
    counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}
              for c in method.findall('counter')}
    return public.main(factory_run_name=run.name,measurement_module=selected,
       required_counts=(240,33,42),case_overrides=overrides,extra_suites=entry.EXTRA,extra_fields={
       'newIndependentCases':1,'priorIndependentCasesRevalidated':41,'newJavaCasesInThisChange':1,
       'spec':'1053_nativeCoverage保持directory_factory所有_PT仕様.md',
       'productionMainChanges':0,'all764MainIdenticalToSource178':True,'previousFullSelectedSource':before['sourceSnapshot'],
       'checkedCountersInThisSubsetOnly':counters,'otherSubsetCountersImported':False,
       'ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
