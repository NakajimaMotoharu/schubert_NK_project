"""Exact six-owner expression PG and eight raw diagnostics removed, unchanged static policy."""
import hashlib
import inspect
import subprocess
import pg5776_jms_primary_static as engine
from pg5804_rollback_static import class_key,signature

PREFIX='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/'
REWRITES={
 'codec/FieldCodec.java':[
  ('public final class FieldCodec {','public final class FieldCodec {\n  private static final int BOOLEAN_FIELD_LENGTH = 1;\n  private static final int MINIMUM_FIELD_LENGTH = 1;\n'),
  ('if (field.length != 1)', 'if (field.length != BOOLEAN_FIELD_LENGTH)'),
  ('if (length < 1)', 'if (length < MINIMUM_FIELD_LENGTH)')],
 'header/MessageKind.java':[
  ('  private final char encodedValue;','  private static final int WIRE_CODE_LENGTH = 1;\n\n  private final char encodedValue;'),
  ('if (value.length() != 1)','if (value.length() != WIRE_CODE_LENGTH)')],
 'header/InteractionKind.java':[
  ('  private final char encodedValue;','  private static final int WIRE_CODE_LENGTH = 1;\n\n  private final char encodedValue;'),
  ('if (value.length() != 1)','if (value.length() != WIRE_CODE_LENGTH)')],
 'layout/LayoutDefinition.java':[
  ('  public static final int HEADER_LENGTH = 256;','  private static final int SUPPORTED_VERSION = 1;\n\n  public static final int HEADER_LENGTH = 256;'),
  ('if (version != 1)','if (version != SUPPORTED_VERSION)')],
 'layout/LayoutFieldCatalog.java':[
  ('public final class LayoutFieldCatalog {','public final class LayoutFieldCatalog {\n  private static final int CATALOG_COLUMN_COUNT = 8;\n  private static final int MINIMUM_POSITIVE_VALUE = 1;\n'),
  ('if (cells.length != 8)','if (cells.length != CATALOG_COLUMN_COUNT)'),
  ('if (parsed < 1)','if (parsed < MINIMUM_POSITIVE_VALUE)')],
 'file/LargeResultRecordCodec.java':[
  ('        result[offset++] = (byte) single;','        result[offset] = (byte) single;\n        offset++;')]}
MODIFIED={PREFIX+p for p in REWRITES}


def expected_source(path,before):
    for old,new in REWRITES[path.removeprefix(PREFIX)]:
        if before.count(old)!=1:raise ValueError('one declared expression before PG')
        before=before.replace(old,new,1)
    return before


def class_contract(old,current):
    outer={class_key(p)for p in MODIFIED};changed={k for k in old if k in current and old[k]!=current[k]}
    if len(old)!=1666 or len(current)!=1666 or set(old)!=set(current)or not outer<=changed or any(not any(k==o or k.startswith(o[:-6]+'$')for o in outer)for k in changed):raise ValueError('all1666 physical classes; only declared six owners and their nested/debug changes')
    return sorted(changed)


def pg_contract(snapshot,value,old):
    sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};before=old['allSourceHashes']
    if len(sources)!=851 or set(sources)!=set(before)or {p for p in sources if sources[p]!=before[p]}!=MODIFIED:raise ValueError('exact six Main source changes')
    for path,digest in sources.items():
        if hashlib.sha256(subprocess.check_output(['git','show',value['source']+':'+path],cwd=engine.ROOT)).hexdigest()!=digest:raise ValueError('canonical compile source')
    prior=engine.W/'pg5828-isolation-selected66-v1/source'
    for path in MODIFIED:
        if expected_source(path,(prior/path).read_text())!=(snapshot/path).read_text():raise ValueError('only named unchanged values and separated local increment')
        if signature(prior,path)!=signature(snapshot,path):raise ValueError('existing public ABI unchanged')
    return sources,class_contract(old['auxClassHashes'],value['allPhysicalMainSha256'])


def runner_source():
    raw=inspect.getsource(engine.main)
    changes={
      'pg5774-jms-primary-green-v1/manifest.safe.json':'pg5844-protocol-expression-selected105-v1/manifest.safe.json',
      "(v['tests'],v['suites'])==(14,7)":"(v['tests'],v['suites'])==(105,26)",
      'pg5750-exception-static-v1/manifest.safe.json':'pg5830-isolation-static-v1/manifest.safe.json',
      'provisional/PG5750-exception-static-v1/manifest.json':'provisional/PG5830-isolation-static-v1/manifest.json',
      '70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9':'a8db12fed46184684ec8d911266dedac6206f42ca65be2fcd8f8c424ab6bbf8f',
      '    guards=guard_coverage(snapshot)':'    guards=v["targetCounters"]',
      "expected_counts['CompareObjectsWithEquals']+=3":"expected_counts['AvoidLiteralsInIfCondition']-=7;expected_counts['AssignmentInOperand']-=1",
      "'changedSourcePaths':sorted(PATHS)":"'changedSourcePaths':sorted(MODIFIED)",
      "'physicalMain':1664":"'physicalMain':1666", "'unchangedPhysicalClasses':1662":"'unchangedPhysicalClasses':1666-len(classes)",
      "'allFieldAndMethodDescriptorsUnchanged':True":"'existingPublicAbiUnchanged':True,'removedPublicDescriptors':0,'addedPublicDescriptors':0,'privateNamedConstantsOnly':True,'rawDiagnosticsRemovedByPg':8",
      "'inputSourceFiles':849":"'inputSourceFiles':851", "'actualAuxClasses':1664":"'actualAuxClasses':1666",
      "'newGuardsActualCoverage':guards":"'selectedTargetActualCounters':guards", ",'newGuardsActualCoverage','F03Accepted'":",'selectedTargetActualCounters','F03Accepted'",
      "provisional/PG5776-jms-primary-static-v1';target.mkdir()":"provisional/PG5848-protocol-expression-static-v1';target.mkdir()"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact851/1666 expression static binding: '+old)
        raw=raw.replace(old,new,1)
    a=raw.index('    sources=');b=raw.index("    for name in('pmd.xml','checkstyle.xml'):",a)
    raw=raw[:a]+"    sources,classes=pg_contract(snapshot,v,old)\n    current=v['allPhysicalMainSha256'];before_snapshot=W/'pg5828-isolation-selected66-v1/source'\n"+raw[b:]
    compile(raw,'<all851 expression PG static>','exec');return raw


def main():
    scope={**vars(engine),'SLOT':'pg5848-protocol-expression-static-v1','MODIFIED':MODIFIED,'pg_contract':pg_contract}
    exec(compile(runner_source(),'<all851 expression PG static>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
