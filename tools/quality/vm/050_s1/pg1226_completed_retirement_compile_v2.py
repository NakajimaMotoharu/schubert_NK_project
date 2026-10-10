"""New immutable compiler slots after BUG1062 actual inventory scope correction."""
from pg1225_completed_retirement_compile import source as previous

def source():
    s=previous().replace('pg1224-native-tools-v1','pg1224-native-tools-v2').replace('pg1225','pg1226')
    s=s.replace("generated=generate(None)","generated={n:v.replace('pg1224-native-tools-v1','pg1224-native-tools-v2')for n,v in generate(None).items()}")
    compile(s,'<v2 current runtime compiler>','exec');return s

if __name__=='__main__':exec(compile(source(),'<v2 new-only actual compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
