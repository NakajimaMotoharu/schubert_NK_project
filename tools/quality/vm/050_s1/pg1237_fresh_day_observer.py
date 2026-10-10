"""Fresh D5 observer after independent completed-runtime retirement, start0."""
from pg1183_canonical_resume_observer import source as previous

def source():
    s=previous().replace('pg1183','pg1237').replace('PG1183','PG1237')
    s=s.replace('pg1182-canonical-runtime-post-v1.safe.json','pg1236-completed-runtime-retired-post-v1.safe.json')
    s=s.replace('ast.parse(raw)',"compile(raw,'<actual fresh observer file>','exec')")
    compile(s,'<fresh current new-day observer>','exec');return s

if __name__=='__main__':exec(compile(source(),'<actual fresh new-day observer>','exec'),{'__file__':__file__,'__name__':'__main__'})
