"""Normal protocol96 plus nine dependency guards after expression-only PG, no operational entry."""
import inspect
import pg5732_enum48_selected as engine
from pg5800_rollback_green import source_test_names

COUNTS={'AuthenticationErrorProfileTest':3,'FieldCodecTest':5,'MessageCodecTest':7,'PayloadCodecTest':8,'PayloadGoldenVectorTest':3,'ScenarioRecordEncodingTest':3,'LargeResultRecordCodecTest':7,'MediaDescriptorValidatorTest':7,'HeaderModelTest':7,'LayoutFieldCatalogTest':3,'LayoutMetadataTest':4,'PayloadSemanticValidatorTest':8,'PayloadTypeCatalogTest':6,'SemanticFieldValueTest':4,'EnumWireCompatibilityTest':2,'ProtocolSemanticTypeTest':5,'JstWireTimestampTest':4,'BrokerTopologyTest':2,'FailedJmsIsolationExceptionTest':4,'UnconfirmedJmsRollbackExceptionTest':4,'EnumValueCatalogCompatibilityTest':1,'HttpByteRangeParserTest':4}
CASES={**engine.CASES,'protocol':{
 'protocol.codec.'+s for s in('AuthenticationErrorProfileTest','FieldCodecTest','MessageCodecTest','PayloadCodecTest','PayloadGoldenVectorTest','ScenarioRecordEncodingTest')}|{
 'protocol.file.LargeResultRecordCodecTest','protocol.file.MediaDescriptorValidatorTest','protocol.header.HeaderModelTest','protocol.layout.LayoutFieldCatalogTest','protocol.layout.LayoutMetadataTest','protocol.layout.PayloadSemanticValidatorTest','protocol.layout.PayloadTypeCatalogTest','protocol.layout.SemanticFieldValueTest','protocol.layout.semantic.EnumWireCompatibilityTest','protocol.layout.semantic.ProtocolSemanticTypeTest','protocol.time.JstWireTimestampTest','protocol.transport.BrokerTopologyTest','protocol.transport.FailedJmsIsolationExceptionTest','protocol.transport.UnconfirmedJmsRollbackExceptionTest'}}
TARGETS={'protocol':['protocol/'+p for p in('codec/FieldCodec','file/LargeResultRecordCodec','header/MessageKind','header/InteractionKind','layout/LayoutDefinition','layout/LayoutFieldCatalog')]}


def runner_source():
    raw=inspect.getsource(engine.main)
    changes={
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=COUNTS[cls.rsplit('.',1)[1]]",
      'sum(map(len,expected.values()))!=12 or len(expected)!=7':'sum(map(len,expected.values()))!=105 or len(expected)!=26',
      "'expectedTests':12":"'expectedTests':105",
      "method=case.get('name','').removesuffix('()')":"method=case.get('name','').split('(',1)[0]",
      'len(physical)==1664':'len(physical)==1666',
      'len(target_counters)==14':'len(target_counters)==6',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(executionKind='NORMAL_PROTOCOL_EXPRESSION_SELECTED105',noExternalRuntimeOperation=True,protocolTests=96,fullSourceFormalQualificationPending=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact protocol105 predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<protocol105 normal fixtures>','exec');return raw


def main():
    scope={**vars(engine),'SLOT':'pg5844-protocol-expression-selected105-v1','CASES':CASES,'COUNTS':COUNTS,'TARGETS':TARGETS,'test_names':source_test_names}
    exec(compile(runner_source(),'<protocol105 normal fixtures>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
