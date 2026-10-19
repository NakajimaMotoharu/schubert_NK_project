"""PG-D439 exact16 manual edits; this helper never edits source or invokes the generic renamer."""
import json
import re
import subprocess
from pg5540_snapshot_scratch_selected import ROOT,TC,sha

JMS='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/JmsRequestReplyException.java'
REVERSE={'failureReason':'reason','denialCode':'resultCode','lockDelaySeconds':'retryAfterSeconds'}


def fields():
    p=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5584-field-accessor-inspection-v1/manifest.json'
    if sha(p)!='31a2a4f92e8a5a2ad0c320a1e6d78008bd560f61e4e3284388ed0a560217bc04':raise ValueError('original typed field inventory')
    rows={r['sourcePath']:r for r in json.loads(p.read_bytes())['fields']if r['ownerKind']!='ENUM'}
    if len(rows)!=16 or any(not r['defaultSerializedField']for r in rows.values()):raise ValueError('all16 inherited default serialized fields, never enum proof reuse')
    return rows


def expected_source(path,old):
    row=fields()[path];before=row['field'];after={v:k for k,v in REVERSE.items()}[before]
    text,count=re.subn(r'(private final [\w.]+ )'+before+r';',r'\g<1>'+after+';',old)
    if count!=1:raise ValueError('exact one private final field')
    text,count=re.subn(r'\bthis\.'+before+r' =',r'this.'+after+' =',text)
    if count!=(2 if path.endswith(('/ResponseSnapshotException.java','/JmsRequestReplyException.java'))else 1):raise ValueError('all declared constructor assignments')
    text,count=re.subn(r'\breturn '+before+r';',r'return '+after+';',text)
    if count!=1:raise ValueError('same public accessor, only return field changed')
    if path.endswith('/MediaDeliveryException.java'):text=text.replace('return reason == Reason.BUSY','return failureReason == Reason.BUSY')
    if path==JMS:
        old_assignment='this.failureReason = reason;'
        if text.count(old_assignment)!=2:raise ValueError('both exact existing JMS constructor assignments')
        text=text.replace(old_assignment,'this.failureReason = java.util.Objects.requireNonNull(reason, "reason");')
    return text


def normalize(text):
    text=re.sub(r'\b(?:'+'|'.join(REVERSE)+r')\b',lambda m:REVERSE[m[0]],text)
    text=re.sub(r'#\d+[ \t]+(?=//)','<cp> ',text)
    return re.sub(r'#\d+','<cp>',text)


def abi_contracts(snapshot):
    jdk=TC/'jdk-25.0.4/bin/javap';old=ROOT.parent/'pgpt-runs/PG379/pg5742-revocation-selected-v1/source';rows=[]
    for path in fields():
        module=path.split('/')[1];member=path.split('/src/main/java/')[1][:-5].replace('/','.')
        def javap(root,code):return subprocess.check_output([str(jdk),'-p',code,'-classpath',str(root/('src/'+module+'/target/classes')),member],text=True)
        if normalize(javap(old,'-s'))!=normalize(javap(snapshot,'-s')):raise ValueError('all public descriptors and private field types preserved')
        left,right=normalize(javap(old,'-c')),normalize(javap(snapshot,'-c'))
        guards=0
        if path==JMS:
            strip=lambda s:re.sub(r'^(\w+)[ \t]+',r'\1 ',re.sub(r'^\s*\d+:\s*','',s,flags=re.M),flags=re.M)
            left,right=strip(left),strip(right)
            pattern=r'ldc <cp> // String reason\ninvokestatic <cp> // Method java/util/Objects.requireNonNull:\(Ljava/lang/Object;Ljava/lang/String;\)Ljava/lang/Object;\ncheckcast <cp> // class dev/codex/schubert/nk/web/messaging/JmsRequestReplyException\$Reason\n'
            right,guards=re.subn(pattern,'',right)
            if guards!=2:raise ValueError('exact two new null invariant sequences')
        if left!=right:raise ValueError('all other actual disassembled instructions unchanged')
        rows.append({'sourcePath':path,'publicDescriptorsUnchanged':True,'privateFieldTypeUnchanged':True,'opcodeSameAfterPrivateNamesAndDeclaredNullGuards':True,'newReasonNullGuards':guards,'inheritedJavaSerializedSchemaCompatibilityClaimed':False})
    return rows
