"""Tool-only profile canaries then existing current exec post reanalysis; no Product replay."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_whole_pure_source_post_v1 as core
import pg14658_question_plain_whole_eight_pt as original

PROFILE={"rawFolder":"PG14658-question-plain-whole-eight-pt-v1","rawSha256":"4700c58777e904acebb2ec08e218ecb64b33e5a49c00385a0a747f4d69ef63e8","postFolder":"PG14670-shared-pure-existing-question-eight-post-v1","sources":{"dev/codex/schubert/nk/api/application/question/QuestionQueryRequest":{"path":"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionQueryRequest.java","sha256":"7e8ed5ca4175bb673a3396612d7cb3e0f7c9aca239bd1ae8f6337155e5201181","module":"api","closure":["dev/codex/schubert/nk/api/application/question/QuestionQueryRequest"],"owner":"WBS-P013-01"}},"kind":"REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES","originalTestsAlreadyCounted":True}
OUT=data.BASE/'PG14670-shared-pure-post-profile-selftest-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    core.validate_profile(PROFILE);name=next(iter(PROFILE['sources']))
    vectors=[
      ('unknown-field',lambda p:p.update(extra=True)),
      ('unsupported-kind',lambda p:p.update(kind='NATIVE')),
      ('raw-path-escape',lambda p:p.update(rawFolder='../PG14658')),
      ('overwrite-raw',lambda p:p.update(postFolder=p['rawFolder'])),
      ('raw-pin',lambda p:p.update(rawSha256='wrong')),
      ('empty-sources',lambda p:p.update(sources={})),
      ('class-alias',lambda p:p['sources'].update({name+'//Alias':p['sources'].pop(name)})),
      ('unknown-module',lambda p:p['sources'][name].update(module='unknown')),
      ('module-path',lambda p:p['sources'][name].update(module='storage')),
      ('source-pin',lambda p:p['sources'][name].update(sha256='x'*64)),
      ('owner-invented',lambda p:p['sources'][name].update(owner='UNKNOWN')),
      ('missing-outer',lambda p:p['sources'][name].update(closure=[name+'$Nested'])),
      ('duplicate-class',lambda p:p['sources'][name].update(closure=[name,name])),
      ('foreign-class',lambda p:p['sources'][name].update(closure=[name,'dev/codex/schubert/nk/api/Other'])),
      ('non-string-class',lambda p:p['sources'][name].update(closure=[name,0])),
      ('bool-role-integer',lambda p:p.update(originalTestsAlreadyCounted=0)),
      ('post-path-escape',lambda p:p.update(postFolder='PG14670/escape')),
      ('unknown-source-field',lambda p:p['sources'][name].update(extra=True))]
    labels=[]
    for label,change in vectors:
        wrong=copy.deepcopy(PROFILE);change(wrong)
        try:core.validate_profile(wrong)
        except ValueError:labels.append(label)
        else:raise ValueError('unsupported profile admitted '+label)
    assert len(labels)==18
    core.verify_profile(original,PROFILE)
    post_path=data.BASE/PROFILE['postFolder']/'manifest.json';post=data.read_checked(post_path,data.sha(post_path.read_bytes()))
    assert post['actualExit']==0 and post['tests']==8 and post['suites']==1 and post['strictFour100GateExit']==1
    assert post['originalTestsCountedElsewhere'] is post['currentSourceExistingExecReanalyzed'] is True and post['newProductExecutions']==post['productTestsReexecutedByPost']==0
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,profile=PROFILE,profileNegativeVectors=len(labels),negativeLabels=labels,reanalysisPostManifest=str(post_path.relative_to(data.ROOT)),reanalysisPostSha256=data.sha(post_path.read_bytes()),originalMethodsAlreadyCounted=8,newProductMethods=0,newProductExecutions=0,productionSourceChanged=False,toolOnly=True,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
