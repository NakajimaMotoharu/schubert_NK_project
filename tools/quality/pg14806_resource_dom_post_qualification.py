"""Tool metadata checks and existing Music receipt reanalysis only; Product executions0."""
import copy
from types import SimpleNamespace
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_resource_dom_post_v1 as core
import pg14790_music_hierarchy_template_six_pt as original

OUT=data.BASE/'PG14806-resource-dom-post-tool-qualification-v1'
PROFILE=dict(rawFolder='PG14790-music-hierarchy-template-six-pt-v1',rawSha256='8ae7f78147a1d9d81a593a4534348caef007b305a0b991d513321833b26874a8',postFolder='PG14808-music-existing-resource-post-v1',resourceOwners={'templates/music.html':'WBS-P016-11','templates/music-sections.html':'WBS-P016-12'})

def main():
    invocation=capture(__file__);core.require(not OUT.exists(),'new-only tool qualification')
    core.validate_profile(original,PROFILE);labels=[]
    for label,change in [('extra',lambda v:v.update(executeAnything=True)),('missing',lambda v:v.pop('rawSha256')),('raw-traversal',lambda v:v.update(rawFolder='../private')),('post-traversal',lambda v:v.update(postFolder='../private')),('alias',lambda v:v.update(postFolder=v['rawFolder'])),('pin',lambda v:v.update(rawSha256='OLD')),('empty-owner',lambda v:v.update(resourceOwners={})),('foreign-resource',lambda v:v.update(resourceOwners={'/private':'WBS-P016-11'})),('cost-parent',lambda v:v.update(resourceOwners={'templates/music.html':'WBS-P016-25.03'}))]:
        bad=copy.deepcopy(PROFILE);change(bad)
        try:core.validate_profile(original,bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false tool profile accepted '+label)
    attributes=['COMPILE_SHA','RESOURCES','TRACE','READ_COPIES','COUNTS','FIXTURES','SOURCE']
    fields={k:copy.deepcopy(getattr(original,k)) for k in attributes}
    for label,key,value in [('normal','COMPILE_SHA','OLD'),('source','SOURCE','OLD'),('resource-path','RESOURCES',{'../private':'0'*64}),('trace-path','TRACE','/private'),('trace-traversal','TRACE','target/scenario-screen-traces/../private.txt'),('read-duplicate','READ_COPIES',['static/css/schubert.css']*2),('read-foreign','READ_COPIES',['../private']),('empty-cases','COUNTS',{}),('bool-count','COUNTS',{'Other':True}),('fixture','FIXTURES',{'other':'0'*64})]:
        bad=copy.deepcopy(fields);bad[key]=value
        try:core.validate_profile(SimpleNamespace(**bad),PROFILE)
        except ValueError:labels.append(label)
        else:raise ValueError('false tool scope accepted '+label)
    duplicates=[]
    for n in [1,2,8]:
        value=dict(cases=[dict(name=str(i)) for i in range(n)]);core.duplicate_case(value)
        core.require(len({v['name'] for v in value['cases']})<len(value['cases']),'duplicate metadata handles singleton and larger scopes');duplicates.append(n)
    core.verify_profile(original,PROFILE)
    post=data.read_checked(data.BASE/PROFILE['postFolder']/'manifest.json',data.sha((data.BASE/PROFILE['postFolder']/'manifest.json').read_bytes()))
    core.require(post['actualExit']==post['javaSourceProgramsQualified']==post['productTestsReexecutedByPost']==0 and post['tests']==6,'existing receipt reanalysis only')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postFolder=PROFILE['postFolder'],postSha256=data.sha((data.BASE/PROFILE['postFolder']/'manifest.json').read_bytes()),profileNegativeVectors=len(labels),negativeLabels=labels,duplicateMetadataCardinalities=duplicates,toolChecks=len(labels)+len(duplicates)+1,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
