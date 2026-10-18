import pg5356_ffm_outputs_selected as entry
import pg5281_factory_finish as finish
from pg5366_ffm_outputs_bytecode import SOURCE,RUN


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5354-scope-classification-manager-session-v1/manifest.json',
        previous_sha='5b04eb686a0c40577446e4058a8b9afde8e1045bd6182d106a0820d16f1e0732',
        previous_source='6c212913dd407d4f35a9aac8553e724eea3bc887',
        qualified_ref='018_NK-OPS-001/evidence/provisional/'+RUN+'-metadata-v2/manifest.json',
        tests=1099,suites=132,counts={'FIXED_LIMITED':208,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':28},
        out_name='PG5370-scope-classification-ffm-outputs-v1',
        extra={'additionalFactoryFixedLimited':4,'additionalFactoryFormalFixed':0,
            'extraFfmBoundariesFixedLimited':2,'extraReadonlyCandidatesStillPending':4})
