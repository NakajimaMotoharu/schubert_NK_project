"""Exact private enum model/ABI and current-source static analysis; no runtime PT or VM calls."""
import inspect
import re
import pg5726_enum_static_abi as previous
import pg5729_protocol27_static as protocol
from pg5732_enum48_selected import SLOT as SELECTED

SLOT='pg5734-enum48-static-v1'
PREFIX='src/schubert-nk-'
SPECS={
 'api:api/messaging/config/ArtemisConnectionFactoryProvider':('  public enum ConsumerProfile {',None,{'windowBytes':'configuredWindowBytes'}),
 'api:api/messaging/outbound/OutboxDestination':(None,None,{'address':'physicalAddress'}),
 'api:api/security/LoginAttemptKind':(None,None,{'threshold':'failureThreshold'}),
 'batch:batch/platform/ApplicationUnit':(None,None,{'serviceName':'unitName'}),
 'batch:batch/platform/MaintenanceUnit':(None,None,{'serviceName':'unitName'}),
 'batch:batch/platform/BackupUnitStartClient':('  public enum Target {','  @FunctionalInterface',{'unit':'systemUnit','observation':'observedTarget','requestDirectory':'requestPath','marker':'intentFileName'}),
 'batch:batch/platform/InspectorUnitSnapshot':('  public enum Target {','  static final String UNIT',{'unit':'systemUnit'}),
 'batch:batch/platform/RootStartupContext':('  public enum Service {','  public record Snapshot(',{'unit':'systemUnit'}),
 'batch:batch/repository/BatchStep':(None,None,{'backup':'backupStep'}),
 'batch:batch/repository/CleanupKind':(None,None,{'function':'sqlFunction','maximumRows':'rowLimit'}),
 'batch:batch/repository/MaintenanceCompletion':('  public enum Outcome {','  public MaintenanceCompletion {',{'exitCode':'processExitCode'}),
 'bootstrap:api/file/AesCredentialFile':(None,None,{'fileName':'credentialFileName','optional':'optionalCredential'}),
 'bootstrap:bootstrap/SystemManagerObservation':('  public enum Service {','  private static final java.lang.String LITERAL_UNIT',{'unit':'systemUnit'}),
 'storage:storage/ServiceCredentialId':(None,None,{'service':'owningService','fileName':'credentialFileName','kind':'credentialKind'})}


def paths():
    return {PREFIX+k.split(':')[0]+'/src/main/java/dev/codex/schubert/nk/'+k.split(':')[1]+'.java':v for k,v in SPECS.items()}


def renamed_source(path,old):
    if path not in paths():return protocol.renamed_source(path,old)
    start,end,names=paths()[path];a=old.index(start)if start else 0;b=old.index(end,a)if end else len(old)
    part=old[a:b]
    for before,after in names.items():
        part,count=re.subn(r'(private final [\w.]+ )'+before+r';',r'\g<1>'+after+';',part)
        if count!=1:raise ValueError('exact private declaration in bounded enum')
        part,count=re.subn(r'\bthis\.'+before+r' =',r'this.'+after+' =',part)
        if count!=1:raise ValueError('exact enum constructor assignment')
        part,count=re.subn(r'\breturn '+before+r';',r'return '+after+';',part)
        if count!=1:raise ValueError('exact enum accessor body')
    if path.endswith('/OutboxDestination.java'):part=part.replace('destination.address.equals(address)','destination.physicalAddress.equals(address)')
    if path.endswith('/MaintenanceUnit.java'):part=part.replace('"/system.slice/" + serviceName','"/system.slice/" + unitName')
    return old[:a]+part+old[b:]


def normalize_contract(text):
    reverse={**protocol.REVERSE,**{v:k for _,_,names in SPECS.values()for k,v in names.items()}}
    text=re.sub(r'\b(?:'+'|'.join(reverse)+r')\b',lambda m:reverse[m[0]],text)
    text=re.sub(r'#\d+[ \t]+(?=//)','<cp> ',text)
    return re.sub(r'#\d+','<cp>',text)


def main():
    renames={**protocol.rename_fields(),**{p:list(v[2])for p,v in paths().items()}}
    if len(renames)!=37 or sum(map(len,renames.values()))!=48:raise ValueError('all37 enum declarations/48 private fields')
    raw=inspect.getsource(previous.main)
    replacements={
      "proof['protocolFour100Qualified']":"proof['selectedQualified']",
      "(proof['tests'],proof['suites'])==(88,18)":"(proof['tests'],proof['suites'])==(5,5)",
      "(snapshot if m=='protocol'else old_snapshot)":"snapshot",
      "expected={k:v for k,v in before['allPhysicalMainSha256'].items()if not k.startswith('protocol:')}\n    expected.update({'protocol:'+k:v for k,v in proof['allPhysicalProtocolMainSha256'].items()})":"expected=proof['allPhysicalMainSha256']",
      "if len(changes)!=18 or any(not p.startswith('src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/')for p in changes):raise ValueError('only eighteen declared enum sources changed')":"if set(changes)!=set(RENAMES):raise ValueError('all37 exact enum-only source models')",
      "required=old.replace('private final String wireValue;','private final String encodedValue;').replace('this.wireValue = wireValue;','this.encodedValue = wireValue;').replace('return wireValue;','return encodedValue;')":"required=renamed_source(path,old)",
      "if old.count('private final String wireValue;')!=1 or new!=required:":"if new!=required:",
      "cls=path.split('/src/main/java/',1)[1][:-5].replace('/','.')":"cls=path.split('/src/main/java/',1)[1][:-5].replace('/','.')\n        module=path.split('/')[1].removeprefix('schubert-nk-')\n        cls+=NESTED.get(path,'')",
      "old_snapshot/'src/schubert-nk-protocol/target/classes'":"old_snapshot/('src/schubert-nk-'+module+'/target/classes')",
      "str(roots['protocol'])":"str(roots[module])",
      "normalize=lambda text:re.sub(r'#\\d+','<cp>',text.replace('encodedValue','wireValue'))":"normalize=normalize_contract",
      "'privateTokenEdits':3":"'renamedPrivateFields':len(RENAMES[path])",
      "'auxFromCurrentProtocolAndUnchangedOtherModules':True":"'allAuxFromCurrentSixModuleCompile':True",
      "'freshWholeCompileClaimed':False":"'freshWholeCompileClaimed':True"}
    nested={'ArtemisConnectionFactoryProvider':'$ConsumerProfile','BackupUnitStartClient':'$Target','InspectorUnitSnapshot':'$Target','RootStartupContext':'$Service','MaintenanceCompletion':'$Outcome','SystemManagerObservation':'$Service'}
    nested={p:nested[p.rsplit('/',1)[1][:-5]]for p in paths()if p.rsplit('/',1)[1][:-5]in nested}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('exact current static-input construction')
        raw=raw.replace(old,new,1)
    raw=raw.replace('target18StaticAndAbiQualified','target48StaticAndAbiQualified').replace('PG5726-enum-static-v1','PG5734-enum48-static-v1')
    namespace={**vars(previous),'PROTOCOL':SELECTED,'SLOT':SLOT,'RENAMES':renames,'NESTED':nested,'renamed_source':renamed_source,'normalize_contract':normalize_contract}
    exec(compile(raw,'<current all48 private enum static ABI check>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
