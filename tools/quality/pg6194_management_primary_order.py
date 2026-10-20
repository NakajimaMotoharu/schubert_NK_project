"""Current original60 JVM/source reauthentication plus exact redacted primary policy."""
import inspect
import pg6186_native_ownership_order as prior
from pg6192_management_primary_qualification import original_source
from jvm_monitor_release import local_slot


def normal_primary_policy(blocks):
    choices=[v for k,v in blocks.items() if ' open(' in k and '$Factory)' in k]
    if len(choices)!=1:raise ValueError('one complete management component open')
    code=choices[0];ops=prior.instructions(code)
    constructed=[i for i,(_,op,arg) in enumerate(ops) if op=='invokespecial' and 'IllegalStateException."<init>":' in arg]
    if len(constructed)!=1:raise ValueError('one fixed pre-acquire diagnostic')
    store=constructed[0]+1
    slot=local_slot(ops[store][1],ops[store][2],'astore')
    bind=prior.one_call({'open':code},'Method bind:')[0][2]
    suppressed=prior.one_call({'open':code},'Throwable.addSuppressed:')[0][2]
    if not store<bind<suppressed or local_slot(ops[suppressed-1][1],ops[suppressed-1][2],'aload')!=slot:
        raise ValueError('exact prebuilt diagnostic, never raw cleanup Throwable')
    if sum(op=='instanceof' and '// class java/lang/Error' in arg for _,op,arg in ops)!=2 or sum(op=='if_acmpeq' for _,op,_ in ops)!=1:
        raise ValueError('both fatal classifications and identity-based self-suppression guard')
    if sum(op=='athrow' for _,op,_ in ops)!=2:
        raise ValueError('separate primary and fatal-secondary exits')
    return dict(diagnosticLocal=slot,constructedBeforeBind=True,addSuppressedUsesOnlyFixedDiagnostic=True,
        fatalClassifications=2,selfSuppressionGuard=True,evidenceTest='bind316006/eight independent compound inputs')


def main():
    raw=inspect.getsource(prior.main)
    for before,after,count in (
        ('PG6184-unstarted-management-qualification-v1','PG6192-management-primary-qualification-v1',1),
        ('pg6184-unstarted-management-qualification-v1','pg6192-management-primary-qualification-v1',1),
        ('(59,20,1667)','(60,20,1667)',1),
        ('pg6182-unstarted-management-selected-v1/source','pg6190-management-primary-selected-v1/source',1),
        ('PG6186-native-ownership-order-v1','PG6194-management-primary-order-v1',1),
        ('    value=dict(actualExit=0','    primary=normal_primary_policy(management)\n    value=dict(actualExit=0',1),
        ('ownershipReviewed=True,\n','ownershipReviewed=True,normalPrimaryPolicy=primary,\n',1)):
        if raw.count(before)!=count:raise ValueError('one declared current JVM binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'original_source':original_source,'normal_primary_policy':normal_primary_policy}
    exec(compile(raw,'<current60 JVM/source review>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
