#!/usr/bin/env python3
"""PG194: certify Scenario hierarchy HTTP slice, never the complete Web/PGPT phase."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.web.session.ScenarioControllerTest"
LOG_TEMPLATE_CLASS = "dev.codex.schubert.nk.web.view.LogSearchTemplateTest"
LOG_TEMPLATE_METHODS = ("log084LayoutAndFilters", "log085RowsAndOptional", "log086Pagination", "log087Escaping", "log088InvalidDisplay", "log089CsrfAndClosedSurface", "log090StylesAndResources", "log091ConcurrentRendering")
LOG_SCRIPT_CLASS = "dev.codex.schubert.nk.web.view.LogSearchScriptTest"
LOG_HTTP_CLASS = "dev.codex.schubert.nk.web.session.LogControllerTest"
LOG_HTTP_METHODS = ("log093SuccessAndIndependentWire", "log094InvalidInputNeverSends", "log095AllResultErrors", "log096SessionInvalidIsTerminal", "log097MalformedTransportAndProjection", "log098NullRoleAndUnknownFailure", "log099MvcRoutesAndBinding", "log100RealHttpAuthorizationAndSession", "log101ConcurrentAdminContexts", "log102EscapingEmptyAndPagination", "log103PublicScriptIsReadOnly")
LOGIN_CLASS = "dev.codex.schubert.nk.web.controller.LoginControllerTest"
LOGIN_METHODS = ("scr105ApprovedBrandAndPostCsrf", "scr106InputsAndNoLeakedCredentials",
                 "scr107OnlyMatchingCurrentMessagesAppear", "scr108ClosedViewAndControllerBoundary")
WEB_HTTP_CLASS = "dev.codex.schubert.nk.web.bootstrap.WebHttpServerTest"
WEB_HTTP_METHODS = ("scr109ActualLoopbackLoginAndClosedRoutes", "scr110InvalidStartupFailsBeforeBinding",
                    "scr111CloseIsIdempotentAndPortBecomesUnavailable",
                    "scr112StartupWithoutStartedContextAndCleanupFailureAreVisible",
                    "scr120CallerOwnedPortReachesRealFeatureController",
                    "scr121InvalidPortRegistrationFailsBeforeTomcatCreation",
                    "scr123LegacyFactoryOverloadReturnsStartedServer")
WEB_HTTP_IDS = (109, 110, 111, 112, 120, 121, 123)
WEB_DEPENDENCY_CLASS = "dev.codex.schubert.nk.web.bootstrap.WebDependencyReadinessTest"
WEB_DEPENDENCY_METHODS = ("scr113RealPostgresAndApprovedBrokerQueue", "scr114NullAndInvalidDatabaseStopBeforeJms",
                          "scr115ProviderFailuresAreRedactedAndBorrowedResourcesClose",
                          "scr116UnavailableBrokerCannotBecomeReady",
                          "scr136FatalDatabaseCloseCannotBeDowngraded",
                          "scr137FatalBrokerCloseCannotBeDowngraded")
WEB_DEPENDENCY_IDS = (113, 114, 115, 116, 136, 137)
WEB_APPLICATION_CLASS = "dev.codex.schubert.nk.web.bootstrap.WebApplicationTest"
WEB_APPLICATION_METHODS = ("scr117ActualIntegratedLoginAndDirectDenial",
                           "scr118DependencyFailurePreventsHttpBind",
                           "scr119NullAndInvalidInputStopsBeforeDependencyProbe",
                           "scr122InvalidMvcDependencyStopsBeforeDatabaseBorrow",
                           "scr124SessionFactoryWiresLogMvcUsingSecurityRepository",
                           "scr125NullSessionFactoryStopsBeforeBorrowingResources",
                           "scr126InvalidSessionDependenciesStopBeforeHttpBind")
WEB_APPLICATION_IDS = (117, 118, 119, 122, 124, 125, 126)
WEB_LOG_RUNTIME_CLASS = "dev.codex.schubert.nk.web.bootstrap.WebLogApplicationRuntimeTest"
WEB_LOG_RUNTIME_METHODS = (
    "scr127RealReplyWorkerAndSecuredLogMvcStartAndClose",
    "scr128InvalidReplyDlqMakesWholeRuntimeNotReady",
    "scr129PartialStartupClosesReplyConsumer",
    "scr130LifecycleAggregatesCloseFailuresAndReadinessBoundaries",
    "scr131StartupNullContractsAndSuppressedCleanup",
    "scr133SameThrowableAcrossOwnedClosuresKeepsPrimary",
    "scr134RealHttpLoginUsesProductionApiBrokerAndSession",
    "scr135RealHttpAdminLogSearchUsesProductionApiBroker")
WEB_LOG_RUNTIME_IDS = (127, 128, 129, 130, 131, 133, 134, 135)
WEB_RUNTIME_DEPENDENCY_CLASS = "dev.codex.schubert.nk.web.bootstrap.WebRuntimeDependencyTest"
WEB_RUNTIME_DEPENDENCY_METHODS = ("scr132RuntimePostgresDriverAndScopeCanaries",)
LOG_SCRIPT_PATH = "src/schubert-nk-web/src/main/resources/static/js/log-search-validation.js"
MUSIC_HTTP_CLASS = "dev.codex.schubert.nk.web.session.MusicControllerTest"
MUSIC_HTTP_METHODS = ("music072SuccessAndWire", "music073ErrorMapping", "music074SessionInvalid",
                      "music075MalformedAndTransport", "music076ResponseBinding", "music077NullAndUnknown",
                      "music078MvcRoutesAndInput", "music079RealHttpSecurity", "music080EscapingAndIsolation",
                      "music081EmptyAndMaximum", "music082ConcurrentRequests", "music083CompatibilityTrace")
MUSIC_CLASS = "dev.codex.schubert.nk.web.view.MusicHierarchyTemplateTest"
MUSIC_METHODS = ("music066CategoryMenu", "music067SectionMenu", "music068EmptyAndMaximum",
                 "music069EscapingAndCsrf", "music070CssAndViewBoundary", "music071ConcurrentRendering")
DETAIL_CLASS = "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest"
SCRIPT_CLASS = "dev.codex.schubert.nk.web.view.ScenarioSearchScriptTest"
SCRIPT_PATH = "src/schubert-nk-web/src/main/resources/static/js/search-speaker-submit.js"
SEARCH_CLASS = "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest"
SEARCH_HTTP_CLASS = "dev.codex.schubert.nk.web.session.ScenarioSearchControllerTest"
ANIMATION_HTTP_CLASS = "dev.codex.schubert.nk.web.session.AnimationControllerTest"
ANIMATION_HTTP_METHODS = ("animation054SuccessAndWire", "animation055ErrorMapping", "animation056SessionInvalid",
                          "animation057MalformedAndTransport", "animation058ResponseBinding", "animation059NullAndUnknown",
                          "animation060MvcRoutes", "animation061RealHttpSecurity", "animation062EscapingAndIsolation",
                          "animation063EmptyAndGrouping", "animation064ConcurrentRequests", "animation065CompatibilityTrace")
ANIMATION_CLASS = "dev.codex.schubert.nk.web.view.AnimationTemplateTest"
ANIMATION_METHODS = ("animation046Menu", "animation047MainRows", "animation048OvaRows", "animation049EmptyAndMaximum",
                     "animation050MegabyteRounding", "animation051EscapingAndCsrf", "animation052CssAndViewBoundary",
                     "animation053ConcurrentRendering")
SEARCH_HTTP_METHODS = ("search034SuccessAndWire", "search035InvalidNoMq", "search036ResultErrorsAtEveryStage",
                       "search037SessionInvalidAtEveryStage", "search038MalformedAndTransport", "search039ResponseBinding",
                       "search040NullAndFailurePropagation", "search041MvcGetHeadAndMethod", "search042RealHttpSecurity",
                       "search043EscapingAndIsolation", "search044ConcurrentRequests", "search045CompatibilityTrace")
SEARCH_METHODS = ("search026CommonLayoutAndInputs", "search027ResultsAndAudio", "search028PaginationAndEmpty",
                  "search029ValidationErrors", "search030EscapingAndCsp", "search031MaximumRowsAndCandidates",
                  "search032CssResourcesAndViewBoundary", "search033ConcurrentRendering")
DETAIL_METHODS = ("detail017HeaderAndCommonLayout", "detail018PreviousNext", "detail019EntriesAndVoices",
                  "detail020EmptyScenario", "detail021HtmlAndUrlSafety", "detail022MaximumRecordsAndVoices",
                  "detail023CssAndViewBoundary", "detail024ConcurrentRendering")
METHODS = ("screens001GamesSuccess", "screens002RoutesSuccess", "screens003FilesSuccess",
           "screens004EmptyHierarchy", "screens005AllResultCodes", "screens006InvalidSessionTerminal",
           "screens007WireAndBindingFailure", "screens008NullAndForeignPrincipal",
           "screens009ClosedRoutesAndRequests", "screens010RealTemplatesAndNavigation",
           "screens011HtmlEscaping", "screens012CompatibilityObservations", "screens013ConcurrentQueries",
           "screens014FailurePropagation", "screens015MvcConfiguration", "screens016RealHttpSecurityAndTerminal")
SUBJECTS = ("dev/codex/schubert/nk/web/controller/ScenarioController",
            "dev/codex/schubert/nk/web/config/ScenarioMvcConfiguration",
            "dev/codex/schubert/nk/web/config/WebMvcConfiguration",
            "dev/codex/schubert/nk/web/controller/AnimationController",
            "dev/codex/schubert/nk/web/config/AnimationMvcConfiguration",
            "dev/codex/schubert/nk/web/controller/MusicController",
            "dev/codex/schubert/nk/web/config/MusicMvcConfiguration",
            "dev/codex/schubert/nk/web/controller/LogController",
            "dev/codex/schubert/nk/web/config/LogMvcConfiguration",
            "dev/codex/schubert/nk/web/controller/LoginController",
            "dev/codex/schubert/nk/web/bootstrap/WebHttpServer",
            "dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness",
            "dev/codex/schubert/nk/web/bootstrap/WebStartupException",
            "dev/codex/schubert/nk/web/bootstrap/WebApplication",
            "dev/codex/schubert/nk/web/bootstrap/WebLogApplicationRuntime")
TRACES = {"PT-SCR-012.txt": b"cases=CHR-S05|CHR-S06\nfixture=public-synthetic\ngames=2\nroutes=2\nfiles=2\norderAndText=PASS\nactualNkGate=false\n",
          "PT-SCR-024.txt": b"template=scenario\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumEntries=10000\nmaximumVoices=999\nactualNkGate=false\n",
          "PT-SCR-033.txt": b"template=search\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRows=100\nmaximumSpeakers=500\nactualNkGate=false\n",
          "PT-SCR-045.txt": b"screen=SCR003\nfixture=public-synthetic\nrequestOrder=SRC|GAM|SPK\nresults=2\nrepresentativeAudio=1\nempty=PASS\nactualNkGate=false\n",
          "PT-SCR-053.txt": b"templates=animation|animation-list\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRecords=50\nactualNkGate=false\n",
          "PT-SCR-065.txt": b"screens=SCR008|SCR009\nfixture=public-synthetic\nroutes=3\nmenuCards=3\nlistRecords=2\nactualNkGate=false\n",
          "PT-SCR-071.txt": b"templates=music|music-sections\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumCategories=20\nmaximumSections=100\nactualNkGate=false\n",
          "PT-SCR-083.txt": b"screens=SCR011|SCR012\nfixture=public-synthetic\nroutes=2\ncategories=2\nsections=2\nactualNkGate=false\n"}
SOURCE_PATHS = (
    LOG_SCRIPT_PATH,
    "src/schubert-nk-web/src/test/javascript/log-search-validation.test.cjs",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/LogSearchScriptTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/LogController.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/LogMvcConfiguration.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/LogControllerTest.java",
    "src/schubert-nk-web/src/main/resources/templates/logs.html",
    "src/schubert-nk-web/src/main/resources/templates/fragments/log-pagination.html",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/LogSearchViewModel.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/LogSearchTemplateTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/MusicController.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/MusicMvcConfiguration.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/MusicControllerTest.java",
    "src/schubert-nk-web/src/main/resources/templates/music.html",
    "src/schubert-nk-web/src/main/resources/templates/music-sections.html",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/MusicCategoryViewModel.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/MusicSectionViewModel.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/MusicHierarchyTemplateTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/AnimationController.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/AnimationMvcConfiguration.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/AnimationControllerTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/ScenarioController.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/ScenarioMvcConfiguration.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/WebMvcConfiguration.java",
    "src/schubert-nk-web/src/main/resources/templates/scenarios.html",
    "src/schubert-nk-web/src/main/resources/templates/scenario-routes.html",
    "src/schubert-nk-web/src/main/resources/templates/scenario-files.html",
    "src/schubert-nk-web/src/main/resources/templates/fragments/layout.html",
    "src/schubert-nk-web/src/main/resources/static/css/schubert.css",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ScenarioControllerTest.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ApiSessionInvalidTest.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/EmbeddedWebSecurityTest.java",
    "src/schubert-nk-web/src/main/resources/templates/scenario.html",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/ScenarioDetailViewModel.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioDetailTemplateTest.java",
    SCRIPT_PATH,
    "src/schubert-nk-web/src/test/javascript/search-speaker-submit.test.cjs",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioSearchScriptTest.java",
    "src/schubert-nk-web/src/main/resources/templates/search.html",
    "src/schubert-nk-web/src/main/resources/templates/fragments/pagination.html",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioSearchTemplateTest.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ScenarioSearchControllerTest.java",
    "src/schubert-nk-web/src/main/resources/templates/animation.html",
    "src/schubert-nk-web/src/main/resources/templates/animation-list.html",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/AnimationMenuViewModel.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/AnimationListViewModel.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/AnimationTemplateTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/LoginController.java",
    "src/schubert-nk-web/src/main/resources/templates/login.html",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/controller/LoginControllerTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServerTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebStartupException.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadinessTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebApplication.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebApplicationTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebLogApplicationRuntime.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebLogApplicationRuntimeTest.java")
SOURCE_PATHS += (
    "src/schubert-nk-web/pom.xml",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeDependencyTest.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginApplicationAssembly.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/log/LogQueryApplicationAssembly.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiLogPathApplicationRuntime.java")


def validate_suite(suite, detail=False):
    classname, methods, first = (DETAIL_CLASS, DETAIL_METHODS, 17) if detail else (CLASS, METHODS, 1)
    return validate_named_suite(suite, classname, methods, first)


def validate_script_suite(suite):
    return validate_named_suite(suite, SCRIPT_CLASS, ("search025BrowserInputScript",), 25)


def validate_search_suite(suite):
    return validate_named_suite(suite, SEARCH_CLASS, SEARCH_METHODS, 26)


def validate_search_http_suite(suite):
    return validate_named_suite(suite, SEARCH_HTTP_CLASS, SEARCH_HTTP_METHODS, 34)


def validate_animation_http_suite(suite):
    return validate_named_suite(suite, ANIMATION_HTTP_CLASS, ANIMATION_HTTP_METHODS, 54)


def validate_animation_suite(suite):
    return validate_named_suite(suite, ANIMATION_CLASS, ANIMATION_METHODS, 46)


def validate_music_suite(suite):
    return validate_named_suite(suite, MUSIC_CLASS, MUSIC_METHODS, 66)


def validate_log_template_suite(suite):
    return validate_named_suite(suite, LOG_TEMPLATE_CLASS, LOG_TEMPLATE_METHODS, 84)


def validate_log_script_suite(suite):
    return validate_named_suite(suite, LOG_SCRIPT_CLASS, ("log092BrowserInputScript",), 92)


def validate_log_http_suite(suite):
    return validate_named_suite(suite, LOG_HTTP_CLASS, LOG_HTTP_METHODS, 93)


def validate_music_http_suite(suite):
    return validate_named_suite(suite, MUSIC_HTTP_CLASS, MUSIC_HTTP_METHODS, 72)


def validate_login_suite(suite):
    return validate_named_suite(suite, LOGIN_CLASS, LOGIN_METHODS, 105)


def validate_web_http_suite(suite):
    return validate_named_suite(suite, WEB_HTTP_CLASS, WEB_HTTP_METHODS, 109, WEB_HTTP_IDS)


def validate_web_dependency_suite(suite):
    return validate_named_suite(suite, WEB_DEPENDENCY_CLASS, WEB_DEPENDENCY_METHODS, 113, WEB_DEPENDENCY_IDS)


def validate_web_application_suite(suite):
    return validate_named_suite(suite, WEB_APPLICATION_CLASS, WEB_APPLICATION_METHODS, 117, WEB_APPLICATION_IDS)


def validate_web_log_runtime_suite(suite):
    return validate_named_suite(suite, WEB_LOG_RUNTIME_CLASS, WEB_LOG_RUNTIME_METHODS, 127,
                                WEB_LOG_RUNTIME_IDS)


def validate_web_runtime_dependency_suite(suite):
    return validate_named_suite(suite, WEB_RUNTIME_DEPENDENCY_CLASS, WEB_RUNTIME_DEPENDENCY_METHODS, 132)


def validate_named_suite(suite, classname, methods, first, test_ids=None):
    identifiers = tuple(range(first, first + len(methods))) if test_ids is None else tuple(test_ids)
    if len(identifiers) != len(methods) or len(set(identifiers)) != len(methods):
        raise ValueError("duplicate or missing screen Test IDs")
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != classname or suite.get("tests") != str(len(methods))
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != len(methods) or len(set(names)) != len(methods) or set(names) != set(methods)
            or any(case.get("classname") != classname or
                   any(child.tag not in ("system-out", "system-err") for child in case) for case in cases)):
        raise ValueError("missing or nonpassing hierarchy screen tests")
    return {f"PT-SCR-{i:03}": classname + "#" + name for i, name in zip(identifiers, methods)}


def validate_script_trace(trace, script_hash, test_id="PT-SCR-025"):
    expected = {"testId": test_id, "nodeVersion": "v24.19.0", "subcases": 8,
                "failed": 0, "skipped": 0, "todo": 0, "syntaxExit": 0, "testExit": 0,
                "lineCoverage": 100, "functionCoverage": 100, "branchCoverage": 100,
                "productionFiles": 1, "scriptSha256": script_hash,
                "browserDom": "deterministic-event-double", "actualNkGate": False}
    if trace != expected or any(type(trace[key]) is not type(value) for key, value in expected.items()):
        raise ValueError("invalid or incomplete browser script evidence")


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("invalid hierarchy screen trace")


def validate_coverage(report):
    result = {}
    for cls in report.iter("class"):
        if cls.get("name") in SUBJECTS:
            counters = {counter.get("type"): {
                "missed": int(counter.get("missed")), "covered": int(counter.get("covered"))
            } for counter in cls.findall("counter")}
            # Configuration and the one-constructor exception class are branchless; no exclusion.
            if cls.get("name") in (SUBJECTS[1], SUBJECTS[2], SUBJECTS[4], SUBJECTS[6], SUBJECTS[8], SUBJECTS[9], SUBJECTS[12], SUBJECTS[13]):
                counters.setdefault("BRANCH", {"missed": 0, "covered": 0})
            result[cls.get("name")] = counters
    if set(result) != set(SUBJECTS) or any(
            not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
            or any(value["missed"] for value in counters.values())
            or any(counters[kind]["covered"] <= 0 for kind in ("LINE", "METHOD", "CLASS"))
            for counters in result.values()) or any(result[name]["BRANCH"]["covered"] <= 0 for name in (SUBJECTS[0], SUBJECTS[3], SUBJECTS[5], SUBJECTS[7], SUBJECTS[10], SUBJECTS[11], SUBJECTS[14])):
        raise ValueError("missing or incomplete hierarchy screen coverage")
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-web/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    methods.update(validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + DETAIL_CLASS + ".xml")).getroot(), True))
    methods.update(validate_script_suite(ET.parse(target / "surefire-reports" / ("TEST-" + SCRIPT_CLASS + ".xml")).getroot()))
    methods.update(validate_search_suite(ET.parse(target / "surefire-reports" / ("TEST-" + SEARCH_CLASS + ".xml")).getroot()))
    methods.update(validate_search_http_suite(ET.parse(target / "surefire-reports" / ("TEST-" + SEARCH_HTTP_CLASS + ".xml")).getroot()))
    methods.update(validate_animation_suite(ET.parse(target / "surefire-reports" / ("TEST-" + ANIMATION_CLASS + ".xml")).getroot()))
    methods.update(validate_animation_http_suite(ET.parse(target / "surefire-reports" / ("TEST-" + ANIMATION_HTTP_CLASS + ".xml")).getroot()))
    methods.update(validate_music_suite(ET.parse(target / "surefire-reports" / ("TEST-" + MUSIC_CLASS + ".xml")).getroot()))
    methods.update(validate_music_http_suite(ET.parse(target / "surefire-reports" / ("TEST-" + MUSIC_HTTP_CLASS + ".xml")).getroot()))
    methods.update(validate_log_template_suite(ET.parse(target / "surefire-reports" / ("TEST-" + LOG_TEMPLATE_CLASS + ".xml")).getroot()))
    methods.update(validate_log_script_suite(ET.parse(target / "surefire-reports" / ("TEST-" + LOG_SCRIPT_CLASS + ".xml")).getroot()))
    methods.update(validate_log_http_suite(ET.parse(target / "surefire-reports" / ("TEST-" + LOG_HTTP_CLASS + ".xml")).getroot()))
    methods.update(validate_login_suite(ET.parse(target / "surefire-reports" / ("TEST-" + LOGIN_CLASS + ".xml")).getroot()))
    methods.update(validate_web_http_suite(ET.parse(target / "surefire-reports" / ("TEST-" + WEB_HTTP_CLASS + ".xml")).getroot()))
    methods.update(validate_web_dependency_suite(ET.parse(target / "surefire-reports" / ("TEST-" + WEB_DEPENDENCY_CLASS + ".xml")).getroot()))
    methods.update(validate_web_application_suite(ET.parse(target / "surefire-reports" / ("TEST-" + WEB_APPLICATION_CLASS + ".xml")).getroot()))
    methods.update(validate_web_log_runtime_suite(ET.parse(target / "surefire-reports" / ("TEST-" + WEB_LOG_RUNTIME_CLASS + ".xml")).getroot()))
    methods.update(validate_web_runtime_dependency_suite(ET.parse(target / "surefire-reports" / ("TEST-" + WEB_RUNTIME_DEPENDENCY_CLASS + ".xml")).getroot()))
    script_trace = json.loads((target / "pt-search-script/PT-SCR025-node.json").read_text())
    validate_script_trace(script_trace, digest(repo / SCRIPT_PATH))
    log_script_trace = json.loads((target / "pt-log-script/PT-SCR092-node.json").read_text())
    validate_script_trace(log_script_trace, digest(repo / LOG_SCRIPT_PATH), "PT-SCR-092")
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    trace_root = target / "scenario-screen-traces"
    traces = {str(path.relative_to(trace_root)): path.read_bytes() for path in trace_root.rglob("*") if path.is_file()}
    validate_traces(traces)
    program = repo / "evidence/01_PT/016_NK-WEB-002"
    evidence = program / "evidence"
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    (evidence / "logs").mkdir(exist_ok=True)
    (evidence / "output/PT-SCR025-node.json").write_text(json.dumps(script_trace, indent=2) + "\n")
    (evidence / "output/PT-SCR092-node.json").write_text(json.dumps(log_script_trace, indent=2) + "\n")
    for name in ("001_NK-WEB-002_Scenario階層画面単体テスト仕様書.md", "002_NK-WEB-002_Scenario階層画面実行結果.md",
                 "003_NK-WEB-002_Scenario本文template単体テスト仕様書.md", "004_NK-WEB-002_Scenario本文template実行結果.md",
                 "005_NK-WEB-002_検索ブラウザ入力単体テスト仕様書.md", "006_NK-WEB-002_検索ブラウザ入力実行結果.md",
                 "007_NK-WEB-002_検索template単体テスト仕様書.md", "008_NK-WEB-002_検索template実行結果.md",
                 "009_NK-WEB-002_検索HTTP単体テスト仕様書.md", "010_NK-WEB-002_検索HTTP実行結果.md",
                 "011_NK-WEB-002_Animation一覧template単体テスト仕様書.md", "012_NK-WEB-002_Animation一覧template実行結果.md",
                 "013_NK-WEB-002_Animation一覧HTTP単体テスト仕様書.md", "014_NK-WEB-002_Animation一覧HTTP実行結果.md",
                 "015_NK-WEB-002_Music階層template単体テスト仕様書.md", "016_NK-WEB-002_Music階層template実行結果.md",
                 "017_NK-WEB-002_Music階層HTTP単体テスト仕様書.md", "018_NK-WEB-002_Music階層HTTP実行結果.md",
                 "019_NK-WEB-002_Log画面template単体テスト仕様書.md", "020_NK-WEB-002_Log画面template実行結果.md",
                 "021_NK-WEB-002_Logブラウザ入力単体テスト仕様書.md", "022_NK-WEB-002_Logブラウザ入力実行結果.md",
                 "023_NK-WEB-002_Log検索HTTP単体テスト仕様書.md", "024_NK-WEB-002_Log検索HTTP実行結果.md",
                 "025_NK-WEB-002_Login画面単体テスト仕様書.md", "026_NK-WEB-002_Login画面実行結果.md",
                 "027_NK-WEB-002_WebHTTP起動単体テスト仕様書.md", "028_NK-WEB-002_WebHTTP起動実行結果.md",
                 "029_NK-WEB-002_Web依存接続単体テスト仕様書.md", "030_NK-WEB-002_Web依存接続実行結果.md",
                 "031_NK-WEB-002_Web起動統合単体テスト仕様書.md", "032_NK-WEB-002_Web起動統合実行結果.md",
                 "033_NK-WEB-002_MVC依存登録単体テスト仕様書.md", "034_NK-WEB-002_MVC依存登録実行結果.md",
                 "035_NK-WEB-002_共有session依存単体テスト仕様書.md", "036_NK-WEB-002_共有session依存実行結果.md",
                 "037_NK-WEB-002_Log経路親起動単体テスト仕様書.md", "038_NK-WEB-002_Log経路親起動実行結果.md",
                 "039_NK-WEB-002_Web実行時JDBC依存単体テスト仕様書.md",
                 "041_NK-WEB-002_Web・API実Login縦結線単体テスト仕様書.md",
                 "042_NK-WEB-002_Web・API実Login縦結線実行結果.md",
                 "043_NK-WEB-002_Web・API実Log検索縦結線単体テスト仕様書.md",
                 "044_NK-WEB-002_Web・API実Log検索縦結線実行結果.md",
                 "045_NK-WEB-002_Web起動前資源複合単体テスト仕様書.md",
                 "046_NK-WEB-002_Web起動前資源複合実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    suite = ET.Element("testsuite", name="NK-WEB-002-screen-slices", tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage").mkdir(exist_ok=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "webReadinessResourceOracle": "045/SCR136..137: synthetic public JDBC/JMS normal inspection with distinct fatal owned close must preserve original Error and close once, DB failure prevents broker acquisition; BUG250 RED is not a PT pass. Full process readiness and NK capture remain unverified.",
        "logTemplateOracle": "019/SCR084..091: actual Log resolver/Current DOM literals,ADMIN,7filters/6types/3levels/date step,all row optionals/details,0/100/101/201/clamped pagination,escaping/invalid field display/CSRF,scoped Current CSS/resource,64 renders.Not browser byte validator/HTTP/NK gate.",
        "logBrowserOracle": "021/SCR092-A..H: eight independent byte/NFC/control/DOM event cases, Node line/function/branch100, exact hash and no skipped/todo. Not live browser or actual NK CHR.",
        "logHttpOracle": "023/SCR093..103: independent UI232/235 bytes and DOM/status, ADMIN/anonymous/USER/0102, all result errors, invalid400/noMQ, malformed/unknown/IO/null, real loopback GET/HEAD/POST and role/session, 64 concurrent contexts. Not live broker or actual NK CHR-L01.",
        "logJavascript": log_script_trace,
        "programId": "NK-WEB-002", "scopeResult": "PASS_HIERARCHY_SEARCH_ANIMATION_MUSIC_LOG_HTTP_AND_BROWSER_UNIT_ONLY", "programComplete": False,
        "musicHttpOracle": "017/SCR072..083: independent MCT/MCS wire,2routes,USER/ADMIN,all error and0102 terminal,malformed/binding/null/unknown,category NFC/64bytes/control/trailing-space/noMQ400,root-empty200/section-empty404,actual template/HTTP/HEAD/security/escaping,20/100 bounds,64 contexts.Not tracks/pair/stream/live broker/NK gate.",
        "musicTemplateOracle": "015/SCR066..071: actual category/section templates, independent Current title/count/order/URLs,USER/ADMIN,0/20 categories,0/100 sections,HTML/CSRF escaping,closed resolver,CSS,64 renders.Not Music HTTP/tracks/stream/actual NK gate.",
        "animationHttpOracle": "013/SCR054..065: independent ANM/ANL wire and three fixed routes,USER/ADMIN,error/0102 session invalidation,malformed and semantic binding,null/unknown propagation,actual MVC/Tomcat/security/HEAD,closed escaped models,0/50 and main/subtrack grouping,64 isolated requests,public trace.Not watch/stream/live broker/NK gate.",
        "animationTemplateOracle": "011/SCR046..053: actual Animation menu/list resolver,independent Current three-card labels/order/count/URLs,main/subtrack grouping and placeholder,OVA metadata,0/50 records,MB rounding literals,escaping/CSRF,7 desktop and1 mobile CSS rules,64 renders.Not Animation HTTP/stream/live Browser/NK gate.",
        "searchHttpOracle": "009/SCR034..045: independent UI234 bytes,SRC/GAM/SPK order,invalid400/no-MQ,all stages error/0102/malformed,request-page binding,null/unknown propagation,MVC and real HEAD distinction,real HTTP USER/ADMIN/session invalidation,64 isolated queries/192 correlations,escaped DOM and public trace.Not live broker/actual NK gate.",
        "searchTemplateOracle": "007/SCR026..033: actual search/pagination template, independent Current title/labels/order/metadata/audio/URLs/counts and all field errors.0/100 results,10 games,500 speakers,64 renders,CSRF only on Logout,all conditionals and HTML escaping.25 desktop/7 mobile CSS rules from Current,exact JS resource GET/HEAD and unknown404 at resource-unit boundary. Not search controller/live browser/actual NK gate.",
        "javascript": script_trace,
        "javascriptCommand": {
            "cwd": "src/schubert-nk-web",
            "syntax": ["/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node", "--check", str(repo / SCRIPT_PATH)],
            "test": ["/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node", "--test", "--experimental-test-coverage",
                     "--test-reporter=tap", "--test-coverage-lines=100", "--test-coverage-functions=100", "--test-coverage-branches=100",
                     "--test-coverage-include=" + str(repo / SCRIPT_PATH),
                     str(repo / "src/schubert-nk-web/src/test/javascript/search-speaker-submit.test.cjs")]},
        "javascriptOracle": "005/PT-SCR025-A..H:8 Node cases inside1 JUnit, independent DOM event double and literals for missing structure,UTF8/NFC/ASCII trim/Unicode controls/surrogates/BOM/byte boundaries,all errors,input recovery and native requestSubmit. Exact Production1file coverage inclusion,syntax/version/exit/skipped/todo checks. Not live Browser/HTTP certificate.",
        "logJavascriptCommand": {"cwd": "src/schubert-nk-web", "node": "/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node", "test": "--test --experimental-test-coverage --test-coverage-lines=100 --test-coverage-functions=100 --test-coverage-branches=100", "production": LOG_SCRIPT_PATH, "fixture": "src/schubert-nk-web/src/test/javascript/log-search-validation.test.cjs"},
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0, "classCoverage": coverage,
        "loginOracle": "025/SCR105..108: actual Spring MVC GET and Thymeleaf, independent approved title/brand, POST form/CSRF and credential-free inputs, Current error/locked/logout text, closed resolver and no controller POST. QA045/UIC005/SSC074; not actual NK CHR-A01/L01.",
        "webHttpOracle": "027/SCR109..112 and 033/SCR120/121/123: actual loopback Tomcat11/MVC/Thymeleaf GET/HEAD/404, mandatory caller security Filter, caller-owned port reaches feature Controller, invalid dependency/path/port/config before Tomcat, legacy factory success, failed bind/start/cleanup, idempotent close. No full production bootstrap or actual NK CHR.",
        "webDependencyOracle": "029/SCR113..116: isolated PostgreSQL18/Flyway Web role and embedded Artemis broker, no message consumption, JDBC false/SQL/close and JMS open/attach/close/unavailable provider boundaries. Consumer construction does not certify Queue existence; SS321 management readiness remains mandatory. No actual NK CHR.",
        "webApplicationOracle": "031/SCR117..119 and 033/SCR122: actual isolated PostgreSQL18/Flyway, embedded Artemis and secured loopback Tomcat, approved login title/CSRF/session cookie and DB row, untrusted direct 403, invalid MVC port rejected before DB/JMS borrow, null/invalid/dependency fault before HTTP. Not credential management, API listener, Queue management readiness or actual NK CHR.",
        "webRuntimeDependencyOracle": "039/SCR132: SS342/343 Web production runtime JDBC scope/version/uniqueness; test/compile/system/absent scope, wrong version and duplicate mutation rejected; Maven runtime-only classpath independently checked in 040. BUG233/YKT186. Not a live DB login or actual NK CHR.",
        "coverageNotes": "Only configuration classes have zero conditional branches; controller branches all covered. No exclusion. Template condition/iteration/text branches verified by SCR001..024/026..033/046..053/066..071/084..091. SCR025 and SCR092 each execute8 Node subcases; both Production JS files have line/function/branch100, no JS class declaration and no exclusion; subcases are not additional JUnit tests.",
        "staticAnalysis": verified["modules"]["web"]["spotbugs"],
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["PG-D-194", "PG-D-195", "PG-D-196", "PG-D-201", "PG-D-202", "PG-D-203", "PG-D-204", "PG-D-205", "PG-D-206", "PG-D-207", "PG-D-208", "PG-D-209", "PG-D-210", "PG-D-211", "PG-D-238", "SSC-071", "SSC-072", "BUG-213", "BUG-214", "BUG-215", "BUG-219", "BUG-220", "BUG-233", "YKT-169", "YKT-170", "YKT-171", "YKT-175", "YKT-176", "YKT-186"],
        "fixture": "Public synthetic independent UI232/234 byte vectors, isolated PostgreSQL encrypted sessions, loopback Tomcat and actual security/MVC. No raw session/cookie/token or master data saved.",
        "oracle": "001/SCR001..016: explicit status/DOM/order/URLs,0/max/null/foreign identity,all result codes,SCF binding,0102 terminal,100 concurrent correlations,unknown failure identity.012 is a synthetic display projection comparison, not the actual NK CHR gate.",
        "detailTemplateOracle": "003/SCR017..024: Production scenario template via resolver, independent heading/navigation/entry/audio/URLs,0/10000 entries/999 voices,all conditionals,escaping,64 renders and full new CSS declaration table/900px/target highlighting. Not a browser screenshot or a registered detail HTTP endpoint.",
        "limitations": "Web HTTP composition, Login GET, isolated DB/broker connectivity only; no credential/final API-Web bootstrap, SS321 Queue management readiness, detail/file port/live broker/all screens/production request logging/actual NK CHR-A01/L01/IT/ST certificate.",
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCE_PATHS]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": len(methods), "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
