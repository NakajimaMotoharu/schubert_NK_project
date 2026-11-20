"""Check the NK-side template wiring for the approved DIF-007 screen set."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re
import subprocess


TEMPLATES = "src/schubert-nk-web/src/main/resources/templates/"
SCREEN_TEMPLATES = {
    "SCR-002": "menu.html",
    "SCR-003": "search.html",
    "SCR-004": "scenarios.html",
    "SCR-005": "scenario-routes.html",
    "SCR-006": "scenario-files.html",
    "SCR-007": "scenario.html",
    "SCR-008": "animation.html",
    "SCR-009": "animation-list.html",
    "SCR-010": "animation-watch.html",
    "SCR-011": "music.html",
    "SCR-012": "music-sections.html",
    "SCR-013": "music-list.html",
    "SCR-014": "logs.html",
    "SCR-015": "admin/user-list.html",
    "SCR-016": "admin/user-new.html",
    "SCR-017": "admin/user-detail.html",
    "SCR-018": "questions/new.html",
    "SCR-019": "questions/accepted.html",
    "SCR-020": "notifications/list.html",
    "SCR-021": "notifications/detail.html",
    "SCR-022": "questions/list.html",
    "SCR-023": "questions/detail.html",
}
FRAGMENT_CALL = re.compile(
    r"~\{fragments/layout :: (topbar|userActions)\(\$\{(page\.(?:values\.)?topBar)\}\)\}"
)
VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())


@dataclass
class Element:
    tag: str
    attrs: dict[str, str | None] = field(default_factory=dict)
    parent: "Element | None" = None
    descendants: list["Element"] = field(default_factory=list)

    def has_class(self, name):
        return name in (self.attrs.get("class") or "").split()

    def walk(self):
        for child in self.descendants:
            yield child
            yield from child.walk()


class TemplateMarkup(HTMLParser):
    def __init__(self, data):
        super().__init__()
        self.root = Element("document")
        self.stack = [self.root]
        self.feed(data.decode("utf-8"))
        self.close()

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if len(data) != len(attrs):
            raise ValueError(f"duplicate attribute on {tag}")
        parent = self.stack[-1]
        node = Element(tag, data, parent)
        parent.descendants.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return


def single(nodes, message):
    if len(nodes) != 1:
        raise ValueError(message)
    return nodes[0]


def layout(root):
    topbar = single([x for x in root.walk() if x.attrs.get("th:fragment") == "topbar(topbar)"],
                    "one shared top-bar fragment required")
    actions = single(
        [x for x in topbar.walk() if x.attrs.get("th:fragment") == "userActions(topbar)"],
        "shared top bar must include the user actions",
    )
    for attr, expression in (("login-user", "${topbar.username}"), ("login-role", "${topbar.role}")):
        span = single([x for x in actions.walk() if x.has_class(attr)], f"one {attr} required")
        if span.tag != "span" or span.attrs.get("th:text") != expression:
            raise ValueError(f"fixed text binding required for {attr}")
        if "th:utext" in span.attrs:
            raise ValueError(f"unescaped binding is invalid for {attr}")
    logout = single([x for x in actions.walk() if x.has_class("logout-form")], "one logout form required")
    if (logout.tag, logout.attrs.get("method"), logout.attrs.get("th:action")) != ("form", "post", "@{/logout}"):
        raise ValueError("logout form must use POST /logout")
    single([x for x in logout.walk() if x.tag == "button" and x.attrs.get("type") == "submit"],
           "one logout submit control required")
    single([x for x in actions.walk() if x.tag == "a" and x.attrs.get("th:href") == "@{/}"],
           "one menu link required")


def template_view(root):
    entries = []
    for node in root.walk():
        match = FRAGMENT_CALL.fullmatch(node.attrs.get("th:replace") or "")
        if match:
            entries.append((node, *match.groups()))
    node, fragment, expression = single(entries, "one shared authenticated top-bar call required")
    if fragment == "topbar" and node.tag == "header":
        return fragment, expression
    while node.parent:
        node = node.parent
        if node.tag == "header" and node.has_class("topbar"):
            return fragment, expression
    raise ValueError("authenticated actions must be inside the rendered top bar")


def public_and_conditional(root_login, root_error):
    if any(":: userActions" in (x.attrs.get("th:replace") or "")
           or ":: topbar" in (x.attrs.get("th:replace") or "") for x in root_login.walk()):
        raise ValueError("public login uses the authenticated fragment")
    condition = "${page.topBar.isPresent()}"
    branch = single([x for x in root_error.walk() if x.attrs.get("th:if") == condition],
                    "one authenticated error branch required")
    single([x for x in branch.walk() if x.tag == "header" and x.attrs.get("th:replace")
            == "~{fragments/layout :: topbar(${page.topBar.orElseThrow()})}"],
           "authenticated error branch lacks the shared fragment")
    anonymous = single([x for x in root_error.walk() if x.attrs.get("th:unless") == condition],
                       "one anonymous error branch required")
    single([x for x in anonymous.walk() if x.tag == "a" and x.attrs.get("th:href") == "@{/login}"],
           "anonymous error branch must link to login")
    if any(x.has_class("logout-form") or "/logout" in (x.attrs.get("th:action") or "")
           or ":: topbar" in (x.attrs.get("th:replace") or "")
           or ":: userActions" in (x.attrs.get("th:replace") or "") for x in anonymous.walk()):
        raise ValueError("anonymous error branch contains an authenticated action")


def main():
    folder = Path("documents/400_PGPT/470_PMO")
    start = next(folder.glob("601_*/950_*"))
    values = json.loads(start.read_bytes())["values"]
    source = values["productionCoreMain"]
    candidate = values["source"]
    out = Path("evidence/01_PT/015_NK-WEB-001/evidence") / values["run"]

    def git(*args):
        return subprocess.check_output(["git", *args])

    def read(name):
        data = git("show", f"{source}:{TEMPLATES}{name}")
        return TemplateMarkup(data).root, hashlib.sha256(data).hexdigest()

    current_path = "program/characterization/baseline/current"
    baseline = git("rev-parse", f"843de94:{current_path}").decode().strip()
    current = git("rev-parse", f"{candidate}:{current_path}").decode().strip()
    if current != baseline:
        raise ValueError("Current characterization tree changed")

    app = {name for name in SCREEN_TEMPLATES.values()}
    expected = app | {"login.html", "error/error.html", "fragments/layout.html",
                      "fragments/pagination.html", "fragments/log-pagination.html"}
    names = git("ls-tree", "-r", "--name-only", source, "--", TEMPLATES).decode().splitlines()
    if {path.removeprefix(TEMPLATES) for path in names} != expected:
        raise ValueError("screen or fragment inventory differs from the approved matrix")

    parsed, sha = read("fragments/layout.html")
    layout(parsed)
    shared = {"path": TEMPLATES + "fragments/layout.html", "sha256": sha}
    screens = {}
    for screen, name in SCREEN_TEMPLATES.items():
        tree, sha = read(name)
        fragment, expression = template_view(tree)
        screens[screen] = {"fragment": fragment, "model": expression,
                           "path": TEMPLATES + name, "sha256": sha}
    login, login_sha = read("login.html")
    error, error_sha = read("error/error.html")
    public_and_conditional(login, error)
    result = {
        "actualExit": 0,
        "environment": {"os": platform.system(), "python": platform.python_version()},
        "command": "python3 -B evidence/01_PT/015_NK-WEB-001/input/4692_dif007_topbar_template_matrix.py",
        "tool": "Python html.parser, source inspection only",
        "source": candidate,
        "productionCore": source,
        "canonicalDesign": values["canonicalDesignSource"],
        "currentBaselineTreeUnchanged": current,
        "testId": "PT-CHR-U02-DIF007-TPL-001",
        "shared": shared,
        "protectedScreens": screens,
        "loginSha256": login_sha,
        "errorSha256": error_sha,
        "authenticatedErrorBranchVerified": True,
        "anonymousErrorBranchVerified": True,
        "liveBrowserOrHttpActions": 0,
        "wholeDif007Accepted": False,
        "actualCaptureStillRequired": True,
        "formalDelta": 0,
        "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
    }
    out.mkdir()
    manifest = out / "manifest.json"
    with manifest.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(manifest, result["testId"], len(screens), len(expected))


if __name__ == "__main__":
    main()
