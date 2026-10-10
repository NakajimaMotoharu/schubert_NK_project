"""New-only full current/candidate post and exact host bindRO after owned verification."""
import ast
import inspect
import pg1297_unused_candidate_independent_post as previous


def payload():
    code=previous.payload()
    code=code.replace("stage_root=base/'pg1293-unused-stage-v1'","stage_root=base/'pg1300-unused-stage-v1'")
    code=code.replace('unusedCandidatePlaced=true\\n','candidateReadOnlyVerified=true\\n')
    code=code.replace('PG1297-unused-candidate-independent-v1','PG1303-candidate-ro-independent-v1')
    marker='print(json.dumps(result))'
    if code.count(marker)!=1:raise ValueError('fixed candidate post boundary required')
    oracle=r'''
mounts=pathlib.Path('/proc/self/mountinfo').read_text().splitlines()
records=[line.split(' ')for line in mounts]
require(all(len(f)>=10 and'-'in f for f in records))
root_records=[f for f in records if f[4]=='/'];target_records=[f for f in records if f[4]==str(root)]
require(len(root_records)==len(target_records)==1 and not any(f[4].startswith(str(root)+'/')for f in records))
r,t=root_records[0],target_records[0];ri,ti=r.index('-'),t.index('-')
require(t[1]==r[0]and t[2]==r[2]and t[3]==str(root)and t[5]=='ro,relatime'and t[ti+1:ti+3]==r[ri+1:ri+3]==['ext4','/dev/vda1']and t[ti+3]==r[ri+3])
require(os.statvfs(root).f_flag&os.ST_RDONLY)
result.update(candidateHostReadonly=True,candidateBindMountMatchesRootAndNoNested=True,currentApprovalEpochUnchanged=True,normalNewCandidateRoManagementScope=True)
'''
    code=code.replace(marker,oracle+'\n'+marker)
    ast.parse(code);return code


def main():
    env=dict(previous.previous.__dict__);env['payload']=payload
    code=inspect.getsource(previous.previous.main).replace('pg1281-current-readonly-v1','pg1303-candidate-ro-independent-v1')
    exec(compile(code,'<new-only candidate readonly full post>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
