"""Query-specific interruption/stop precedence, retaining immediate vs deferred null admission."""
import pg5390_archive_pipeline_selected as previous

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
PREFIX=previous.PREFIX
FILES={'SystemctlStateSource','InspectorUnitProbe'}
OUTERS=FILES
REQUIRED={PREFIX+n+'.class' for n in ('ProcessResourceScope','SystemctlStateSource',
    'InspectorUnitProbe$NativeReader','InspectorUnitProbe$SafeStream','InspectorUnitProbe$QueryProcess')}
ADDED={PREFIX+n+'.class' for n in ('ProcessResourceScope$OwnedQuery','SystemctlStateSource$StdIo')}
DEBUG={PREFIX+n+'.class' for n in ('ProcessResourceScope$QueryWork','SystemctlStateSource$NativeProcess',
    'SystemctlStateSource$Start','InspectorUnitProbe','InspectorUnitProbe$Reader','InspectorUnitProbe$NativeReader$Start')}
RELATED={'dev.codex.schubert.nk.batch.platform.'+n:'batch' for n in (
    'SystemctlStateSourceTest','InspectorUnitProbeTest','ProcessResourceScopeTest')}
EXPECTED_MAIN=767


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|=REQUIRED
    selected.EXTRA_DEBUG|=DEBUG
    selected.EXTRA_ADDED|=ADDED


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


if __name__=='__main__':
    configure()
    raise SystemExit(selected.main(stem_override='pg5404-process-query',version_override='v3',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions()))
