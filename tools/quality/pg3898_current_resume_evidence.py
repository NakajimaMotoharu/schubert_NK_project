"""Publish exact current completed-resume/Browser/stop/two-cohort safe receipts only."""
import inspect
import pg3838_hygiene_current_evidence as previous
from pg3798_hygiene_current_observer import SOURCE,BOM

OUT=previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3898-current-resume-lifecycle-v1'
RECEIPTS=[('PT-CURRENT-RESUME-3858','pg3858-current-resume-terminal-v1/manifest.safe.json'),
 ('PT-CURRENT-RESUME-ROWS-3860','pg3860-current-resume-rows-v1/manifest.safe.json'),
 ('PT-CURRENT-RESUME-SEAL-3862','pg3862-current-resume-full-seal-v1/manifest.safe.json'),
 ('PT-CURRENT-RESUME-BROWSER-3866','pg3866-current-resume-browser-actual-v1/manifest.safe.json'),
 ('PT-CURRENT-RESUME-COMPOSITE-3870','pg3870-current-resume-composite-full-seal-v1/manifest.safe.json'),
 ('PT-CURRENT-RESUME-PARENT18-3872','pg3872-current-resume-parent-projection-v1.safe.json'),
 ('PT-CURRENT-RESUME-STOP-3880','pg3880-stop-v1.safe.json'),
 ('PT-CURRENT-RESUME-POST-3882','pg3882-current-resume-owned-post-v1/manifest.safe.json')]


def main():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg3832-hygiene-native-qualified-v1','pg3892-current-two-cohort-native-v1'),
                    ("native['currentNativeStreams']!=9","native['currentNativeStreams']!=18"),
                    ("native['validatedNativePoints']!=10","native['validatedNativePoints']!=20"),
                    ('PG3838-hygiene-current-lifecycle-v1','PG3898-current-resume-lifecycle-v1'),
                    ("'RootElapsedSeconds':1758.747101","'RootElapsedSeconds':inputs[0][1]['elapsedSeconds']"),
                    ("'newsourceNativePoints':10","'newsourceNativePoints':20"),
                    ("'newsourceNativeStreams':9","'newsourceNativeStreams':18"),
                    ('remaining same-source resume/legacy branches','remaining same-source legacy/negative branches')]:
        if old not in raw:raise ValueError('one exact current collector role required '+old)
        raw=raw.replace(old,new)
    values={**previous.__dict__,'SOURCE':SOURCE,'BOM':BOM,'OUT':OUT,'RECEIPTS':RECEIPTS}
    exec(compile(raw,'<actual same-source completed resume safe collector>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
