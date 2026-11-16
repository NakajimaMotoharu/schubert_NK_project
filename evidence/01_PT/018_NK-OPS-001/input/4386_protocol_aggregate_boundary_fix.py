"""Add the missing independent getters/length negatives after BUG3122; preserve old assertions."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';t=r/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/ProtocolAggregateValueContractTest.java';old=t.read_text();e=b/'evidence/PG36460-protocol-aggregate-getter-boundary-source-v4';e.mkdir();(e/'ProtocolAggregateValueContractTest.java.txt').write_text(old)
blocks=[('    assertEquals(1, fields.dataFields().size());\n','    assertEquals(first, fields.layout());\n'),('    assertEquals(1, first.records().size());\n','    assertEquals(new LayoutId(LAYOUT_IDENTIFIER), first.layoutId());\n    assertEquals(values(FIELD_TEXT), first.data());\n'),('    assertEquals(value, typed.data().fields());\n','    assertEquals(new LayoutId(LAYOUT_IDENTIFIER), typed.layoutId());\n'),('    assertKeys(first, same, different, HEADER_TEXT);\n','''    assertEquals("SCHBNK01", first.protocolIdentifier());
    assertEquals(1, first.headerVersion());
    assertEquals(1, first.layoutVersion());
    assertEquals(MessageKind.REQUEST, first.messageKind());
    assertEquals(InteractionKind.SYNCHRONOUS, first.interactionKind());
    assertEquals(UUID.fromString(ID_TEXT), first.messageId());
    assertEquals(Instant.parse("2026-09-01T00:00:00Z"), first.sentAt());
    assertEquals(Optional.empty(), first.authenticationContext());
    assertEquals(256, first.headerLength());
    assertEquals(Optional.empty(), first.resultCode());
'''),('    assertEquals(first, message.header());\n','''    assertThrows(NullPointerException.class, () -> new WireMessage<FixedPayload>(null, immutable));
    assertThrows(NullPointerException.class, () -> new WireMessage<FixedPayload>(first, null));
    assertThrows(LayoutValidationException.class, () -> new WireMessage<>(first, new FixedPayload(new byte[1], 0, List.of())));
    assertThrows(LayoutValidationException.class, () -> new WireMessage<>(first, new FixedPayload(new byte[2], 1, List.of())));
    assertThrows(LayoutValidationException.class, () -> new WireMessage<>(first, new FixedPayload(new byte[2], 0, List.of(new byte[0]))));
''')]
new=old
for anchor,addition in blocks:assert new.count(anchor)==1;new=new.replace(anchor,anchor+addition)
inverse=new
for anchor,addition in blocks:inverse=inverse.replace(anchor+addition,anchor)
assert inverse==old;t.write_text(new)
subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(t)],check=True,timeout=30)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));mp=e/'manifest.json';mp.open('x').write(json.dumps(dict(actualExit=0,bug='BUG3122',ykt='YKT2594',before=ref(e/'ProtocolAggregateValueContractTest.java.txt'),after=ref(t),oldAssertionsAndExpectationsPreservedInverseExact=True,addedGetterContracts=14,wireLengthInequalities=3,wireNullContracts=2,newJUnitDefinitions=0,originalJUnitDefinitions=4,mainChanged=0,applicationTestsExecuted=0),indent=2)+'\n')
c=json.loads((b/'input/4380_protocol_aggregate_profile_v3.json').read_text());c.update(id='PG36480-PROTOCOL-AGGREGATE-SEVEN-VALUES-18-V4',slots={k:str((b/('evidence/PG'+str(n)+'-protocol-aggregate-'+k+'-v4')).relative_to(r)) for k,n in [('prestyle',36462),('prepare',36464),('static',36466),('preflight',36468),('unit',36480),('post',36482)]},privateDirs=dict(prepare='pg36464-protocol-aggregate-values-v4',unit='pg36480-protocol-aggregate-values-v4'));c['closureProofs'].append(ref(mp));(b/'input/4387_protocol_aggregate_profile_v4.json').open('x').write(json.dumps(c,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,newDefinitions=0,totalNewDefinitions=4,wireNegativeContracts=5,mainChanged=0)))
