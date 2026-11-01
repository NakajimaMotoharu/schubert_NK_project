"""Metadata-only environment callback ownership qualification. No compiler/JVM/network/process calls."""
import inspect
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_host as old
import scoped_prometheus_owned_loopback_host_v1 as owned
import pg14296_web_target_mutation_whole_twenty_four_pt as previous
import owned_loopback_environment_step_v1 as selected
OUT=data.BASE/'PG17393-owned-loopback-environment-binding-v2'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only metadata')
    require(data.sha((data.ROOT/'tools/quality/scoped_prometheus_owned_loopback_host_v1.py').read_bytes())=='faf3eae6357d50d2b3b89311fb4fb48613309c236e1d32686f9227a9cfd4c6ea','qualified unchanged disclosure runner')
    expected=inspect.getsource(previous.environmental_step).replace('_original_step','_owned_original_step')
    actual=inspect.getsource(selected.environmental_step)
    def source_contract(value):require(value==expected,'same original JVM prefix/hash/bounds, only own runner binding differs')
    source_contract(actual);source_labels=[]
    for a,b in [('run.SLOT','old.SLOT'),('_owned_original_step','_original_step'),('range(32)','range(64)'),('readline(513)','readline()'),("run.host.sha(log)==result['logSha256']",'True')]:
        require(a in actual,'actual callback guard anchor')
        try:source_contract(actual.replace(a,b))
        except ValueError:source_labels.append(a)
        else:raise ValueError('changed callback accepted')
    def binding(callback,step,runner):
        require(callback is selected.environmental_step and callback.__globals__['run'] is runner is owned and step.__module__==owned.__name__,'same actual module owns step and runtime slot')
    binding(selected.environmental_step,selected._owned_original_step,owned);binding_labels=[]
    for c,s,r,label in [(previous.environmental_step,selected._owned_original_step,owned,'old-callback'),(selected.environmental_step,old.step,owned,'old-step'),(selected.environmental_step,selected._owned_original_step,old,'old-runner')]:
        try:binding(c,s,r)
        except ValueError:binding_labels.append(label)
        else:raise ValueError('foreign runner callback accepted')
    original=selected._owned_original_step;old_slot=old.SLOT;calls=[];marker={'actualExit':0}
    def stub(name,command):
        calls.append((name,command));return marker
    try:
        selected._owned_original_step=stub
        require(selected.environmental_step('metadata-only',['NOT_EXECUTED']) is marker and calls==[('metadata-only',['NOT_EXECUTED'])],'exact single stub delegation, not a process')
    finally:selected._owned_original_step=original
    require(old.SLOT==old_slot and selected.run is owned and selected._owned_original_step is original,'no old slot/global modification')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,callbackSourceSha256=data.sha(actual.encode()),originalCallbackModule=previous.environmental_step.__module__,ownedCallbackModule=selected.environmental_step.__module__,ownedStepModule=original.__module__,sourceNegativeVectors=len(source_labels),sourceNegativeLabels=source_labels,bindingNegativeVectors=len(binding_labels),bindingNegativeLabels=binding_labels,stubDelegations=len(calls),oldSlotUnchanged=True,callerImportedByQualification=False,qualificationDependencyDirection='FIXED_HELPER_THEN_METADATA_PROOF_THEN_CALLER',productTestsExecuted=0,compilerCommandsIssued=0,jvmCommandsIssued=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
