"""Restore only the original public repository fixture; preserve failed first run and product sources."""
from pathlib import Path
import json
b=Path('evidence/01_PT/018_NK-OPS-001');i=b/'input';ld=lambda p:json.loads(p.read_text());old=ld(i/'4134_ssc440_namespace39_profile.json');env=ld(i/'2298_env10_closed_profile.json');c=dict(old);c['resources']=env['resources'];c['systemProperties']=env['systemProperties'];c['id']='PG35560-SSC440-PUBLIC-NAMESPACE-WHOLE39-V2'
for key,number in dict(prestyle=35540,prepare=35542,static=35544,preflight=35546,unit=35560,post=35562).items():c['slots'][key]=str(b/'evidence'/('PG'+str(number)+'-ssc440-namespace39-'+key+'-v2'))
for key,number in dict(prepare=35542,unit=35560).items():c['privateDirs'][key]='pg'+str(number)+'-ssc440-namespace39-v2'
assert c['mainSources']==old['mainSources'] and c['testSources']==old['testSources'] and c['expectedTests']==39 and c['resources']==env['resources'] and c['systemProperties']==env['systemProperties'];(i/'4146_ssc440_namespace39_profile_v2.json').open('x').write(json.dumps(c,indent=2)+'\n')
for src,dst,replacements in [('4136_ssc440_namespace39_post_join.py','4148_ssc440_namespace39_post_join_v2.py',{'4134_ssc440_namespace39_profile.json':'4146_ssc440_namespace39_profile_v2.json','PG35523-ssc440-namespace39-post-join-v1':'PG35563-ssc440-namespace39-post-join-v2'}),('4137_ssc440_namespace39_unfiltered.py','4149_ssc440_namespace39_unfiltered_v2.py',{'PG35523-ssc440-namespace39-post-join-v1':'PG35563-ssc440-namespace39-post-join-v2','PG35524-ssc440-namespace39-unfiltered-v1':'PG35564-ssc440-namespace39-unfiltered-v2','pg35514-ssc440-namespace39-v1':'pg35542-ssc440-namespace39-v2'}),('4144_ssc440_static_admission_prepare.py','4147_ssc440_static_admission_prepare_v2.py',{'4134_ssc440_namespace39_profile.json':'4146_ssc440_namespace39_profile_v2.json','4135_ssc440_namespace39_static_admission.json':'4150_ssc440_namespace39_static_admission_v2.json'})]:
 text=(i/src).read_text()
 for a,z in replacements.items():assert a in text;text=text.replace(a,z)
 (i/dst).open('x').write(text)
print('v2 profile and exact-scope wrappers created, product Main/Test unchanged')
