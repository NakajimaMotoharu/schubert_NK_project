"""Whole protected seventeen-source current runtime-retirement ABI and Werror."""
import pg3036_current_runtime_retirement_compile as template
from pg3902_current_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS


def main():
    engine=template.previous.previous.previous.prior.prior.prior.old.prior.prior
    raw=engine.compiler_source()
    for old,new in [('Pg1609','Pg3902'),('pg1610','pg3904'),('pg1544-release-v1','pg3748-release-v1'),
                    ('pg1217-frozen-v1.safe.json','pg3878-frozen-v1.safe.json'),('Pg1216','Pg3876'),
                    ('pg1216-native-tools-v1','pg3876-current-resume-owned-tools-v1')]:raw=raw.replace(old,new)
    values={**engine.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':SHA,'TARGET':engine.prior.prior.W/TOOLS}
    exec(compile(raw,'<current protected whole17 retirement ABI>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
