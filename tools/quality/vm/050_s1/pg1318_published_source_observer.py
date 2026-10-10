"""New current769 observer only; exact source/BOM/generation, no starts or stops."""
from pg1237_fresh_day_observer import source as previous
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST


def source():
    code=previous().replace('pg1237','pg1318').replace('PG1237','PG1318')
    code=code.replace('pg1236-completed-runtime-retired-post-v1.safe.json','pg1315-ordinary-publication-independent-v1.safe.json')
    code=code.replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE).replace('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST).replace('PG1068','PG1292')
    compile(code,'<new published source observer>','exec');return code


if __name__=='__main__':exec(compile(source(),'<actual new-source observer>','exec'),{'__file__':__file__,'__name__':'__main__'})
