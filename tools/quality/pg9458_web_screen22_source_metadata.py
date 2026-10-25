"""1920 exact Web screen/form/view22 source labels; no rendering, HTTP, DB or target test execution."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PREFIX='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/'
TABLE={
 'form/TargetOperationFormTest.java':'WBS-P015-07','form/UserMutationFormTest.java':'WBS-P016-17',
 'session/AnimationControllerTest.java':'WBS-P016-10','session/ContentDetailControllerTest.java':'WBS-P016-07',
 'session/LogControllerTest.java':'WBS-P016-14','session/MediaControllerTest.java':'WBS-P009-05',
 'session/MenuMvcTest.java':'WBS-P016-02','session/MusicControllerTest.java':'WBS-P016-13',
 'session/NotificationControllerTest.java':'WBS-P016-21','session/QuestionControllerTest.java':'WBS-P016-18',
 'session/ScenarioControllerTest.java':'WBS-P016-07','session/ScenarioSearchControllerTest.java':'WBS-P016-07',
 'session/UserAdminControllerTest.java':'WBS-P016-17','session/UserBusinessControllerTest.java':'WBS-P016-17',
 'view/AnimationTemplateTest.java':'WBS-P016-08','view/AnimationViewModelTest.java':'WBS-P016-08',
 'view/LogSearchTemplateTest.java':'WBS-P016-14','view/MusicHierarchyTemplateTest.java':'WBS-P016-11',
 'view/MusicHierarchyViewModelTest.java':'WBS-P016-11','view/ScenarioDetailTemplateTest.java':'WBS-P016-07',
 'view/ScenarioHierarchyViewModelTest.java':'WBS-P016-04','view/ScenarioSearchTemplateTest.java':'WBS-P016-03'}
PRIMARY={PREFIX+path:owner for path,owner in TABLE.items()}

if __name__=='__main__':
    assert len(PRIMARY)==22
    metadata.run(Path(__file__),metadata.BASE/'PG9458-web-screen22-source-metadata-v1',metadata.ROOT.parent/'pgpt-runs/PG379/pg9458-web-screen22-source-metadata-v1',
      PRIMARY,'PG9450-web-boundary24-source-join-v1/manifest.json','170288a0dc7c8b2ebecd8bd42c397bdfdc274f30057c8c2c7dc850063afe5818',False)
