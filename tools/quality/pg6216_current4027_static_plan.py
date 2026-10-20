"""One complete current1340 inventory; strict reauthentication is not a new disposition."""
import inspect
import pg6200_current4024_static_plan as prior
from pg6208_keeper_faults_qualification import original_source


def definitions():
    scope={**vars(prior),'original_source':original_source}
    for name in ('calculate','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
            ('PG6193-management-primary-qualification-v2','PG6208-keeper-faults-qualification-v1'),
            ('pg6193-management-primary-qualification-v2','pg6208-keeper-faults-qualification-v1'),
            ('e64ddbb2f3f2d736379f374633d00efa215872b3aaee344f1b43605002ad0e1f','b000fbecefc854567332c21530dd63d1de411c06042f00d9e182e2def106ac34'),
            ('1334','1340'),('!=190','!=196'),('changedSourceFindings=190','changedSourceFindings=196'),
            ('originalSelectedTests=60','originalSelectedTests=63'),('PG6196-six-v1','PG6212-six-v1'),
            ('PG6200-current4024-static-plan-v1','PG6216-current4027-static-plan-v1')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<current1340 '+name+'>','exec'),scope)
    return scope


def calculate():return definitions()['calculate']()
def main():return definitions()['main']()


if __name__=='__main__':main()
