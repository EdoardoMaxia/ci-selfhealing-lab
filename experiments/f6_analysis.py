"""
F6 (MSR 2027 revision): correct-repair classification and final tables.
Deterministic: no LLM, no network (the repaired test files are read from the fix commits with git).

Criterion (approved 27 Nov 2026). A repair is correct if it does what the case's expected_fix says,
or an equivalent alternative, without removing a package the case declares and without touching
anything else (patch equivalent to restoring the "-" line of the git_diff; same principle as A2,
where weakening the oracle was not a correct repair).

dependency (requirements.txt; line order, spaces, blank lines and comments do not count)
  A  identical to the clean file the harness writes (ORIGINAL_REQUIREMENTS + context). Correct only
     if every package the case declares is declared there too (e.g. dep_025); otherwise it is a
     removal and follows rule D.
  B  the declared package(s) back to the version of the "-" line, the rest intact: correct.
  C  another version or variant coherent with expected_fix (DEP_SPEC), the rest intact: correct.
     C-loose = the same with an unpinned / loosened requirement (counted apart).
  D  a package the case declares was removed: correct only where expected_fix admits the removal.
  E  anything else: manual review (experiments/repair_review.json).
config (ci.yml, compared as parsed YAML)
  A  identical to ci.yml at HEAD; C only the injected python-version changed, to a version
     expected_fix admits; E anything else (another job, another line): manual review.
test (criterion of A2 §5.5)
  identical  repaired test AST-identical to the original: correct; otherwise manual review:
  valid (correct alternative) / adapted (test adapted to the bug) / weakened / incomplete.
  Baseline = A2 (19 Nov), classified in A2 §5.5 (A2_REVIEW below); memory arm = F2.

Usage:
  python experiments/f6_analysis.py --classify   # writes experiments/repair_classification.json
  python experiments/f6_analysis.py --report     # markdown report (tables + LaTeX) on stdout
Inputs (defaults): --f2-dir experiments/results/f2_rerun, --a2-dir experiments/results/a2_test_rerun,
  --a3-dir experiments/results/a3_rerun, --sept-dir experiments/results/sept_paper (the 12 CSVs of
  the September run used in the paper), --git-dir . (a clone holding the F2 fix commits).
"""
import argparse
import ast
import csv
import difflib
import glob
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments import f2_rerun_summary as f2s                 # noqa: E402
from experiments.benchmark import (EXCLUDED_CASES, ORIGINAL_REQUIREMENTS,  # noqa: E402
                                   reference_state)
from experiments.dataset import DATASET                          # noqa: E402

BY_ID = {e["id"]: e for e in DATASET}
CLASSIFICATION_FILE = ROOT / "experiments" / "repair_classification.json"
REVIEW_FILE = ROOT / "experiments" / "repair_review.json"
MODEL_ORDER = f2s.MODEL_ORDER
MODEL_LABEL = {"anthropic_haiku": "Claude Haiku", "openai_gpt4o": "GPT-4o", "ollama_qwen38_27b": "Qwen3.8 27B",
               "ollama_qwen3coder_30b": "Qwen3-Coder 30B", "ollama_llama8b": "Llama 3.1 8B",
               "ollama_mistral7b": "Mistral 7B"}
CORRECT_CLASSES_TEST = {"identical", "valid"}
F1_CHANGED = {"conf_001", "conf_002", "conf_003"}      # git_diff changed in F1 (alignment)

# ── dependency: what expected_fix admits, per included case (annotator: Claude, 27 Nov 2026) ──
# need: packages the case declares, which must stay declared, with the constraint expected_fix puts
#       on their version ("" = any published version; CI green already proves it exists)
# alts: alternative constraint sets (expected_fix offers more than one fix); one must hold
# removable: packages whose removal expected_fix admits
# marker: a package that may stay only with an environment marker containing the given text
# options: pip options expected_fix admits in requirements.txt
# stable: no pre-release version
DEP_SPEC = {
    "dep_001": {"need": {"numpy": ""}},
    "dep_002": {"need": {"pandas": ""}},
    "dep_003": {"need": {"scikit-learn": ">=1.3.0"}},
    "dep_004": {"need": {"requests": ""}},
    "dep_005": {"need": {"flask": ""}},
    "dep_006": {"need": {"tensorflow": ">=2.13.0"}},
    "dep_007": {"need": {"scipy": ""}},
    "dep_008": {"need": {"matplotlib": ""}},
    "dep_009": {"need": {"pandas": "", "scipy": ""}, "alts": [{"scipy": ">=1.10.0"}, {"pandas": "==1.5.3"}]},
    "dep_011": {"need": {}, "removable": {"my-internal-lib"}, "options": {"--extra-index-url"}},
    "dep_012": {"need": {"sqlalchemy": ">=2.0.0", "pydantic": ">=2.0.0", "typing-extensions": ">=4.6.0"}},
    "dep_014": {"need": {"newpackage": "<1.0.0"}},
    "dep_015": {"need": {}, "removable": {"broken-lib"}},
    "dep_018": {"need": {"grpcio": "", "grpcio-tools": "", "protobuf": ">=4.21.6"}},
    "dep_020": {"need": {"celery": "", "kombu": ""}, "alts": [{"kombu": ">=5.3.0"}, {"celery": "<5.3.0"}]},
    "dep_022": {"need": {"flask": ""}},
    "dep_023": {"need": {"pyyaml": ""}},
    "dep_025": {"need": {"click": "==8.1.7"}},
    "dep_027": {"need": {"requests": ""}},
    "dep_029": {"need": {}, "removable": {"pywin32"}, "marker": {"pywin32": "win32"}},
    "dep_030": {"need": {"pillow": ">8.3.2"}},   # log: 8.3.2 flagged for CVE-2021-34552; "e.g. 10.3.0" is an example
    "dep_031": {"need": {"requests": ""}},
    "dep_032": {"need": {"sphinx": "", "docutils": ">=0.18.1,<0.21"}},
    "dep_033": {"need": {"torch": ""}, "options": {"--index-url", "--extra-index-url"}},
    "dep_036": {"need": {"acme-internal-utils": ""}, "options": {"--index-url", "--extra-index-url"}},
    "dep_037": {"need": {"setuptools": ">=68"}},
    "dep_038": {"need": {"internal-tool": ""}},
    "dep_040": {"need": {"click": ""}},
    "dep_042": {"need": {"package-a": "", "package-b": ">=2.0.0"}},
    "dep_044": {"need": {}},        # injected line is YAML (runs-on), it declares no package
    "dep_045": {"need": {}},        # injected line is a pip option (-c constraints.txt); expected_fix removes it
    "dep_047": {"need": {"streamlit": "", "protobuf": ">=3.20,<5"}},
    "dep_048": {"need": {"boto3": "==1.34.10"}, "removable": {"botocore"}},
    "dep_049": {"need": {}},        # injected line is YAML (cache key), it declares no package
    "dep_050": {"need": {"mypackage": ""}, "stable": True},
}
CONFIG_ALLOWED = {"conf_001": {"3.11"}, "conf_002": {"3.11"},
                  "conf_003": {"3.11", "3.12", "3.13", "3.14", "3.15"},   # "3.11 or higher", stable on runners
                  "conf_013": set()}

# ── A2 §5.5: the 28 test fixes different from the original (all other A2 fixes: identical) ──
A2_REVIEW = {
    ("test_007", "anthropic_haiku"): "valid", ("test_007", "ollama_qwen38_27b"): "valid",
    ("test_007", "ollama_qwen3coder_30b"): "valid", ("test_046", "ollama_llama8b"): "valid",
    ("test_046", "ollama_mistral7b"): "valid", ("test_033", "openai_gpt4o"): "valid",
    ("test_017", "anthropic_haiku"): "valid", ("test_045", "anthropic_haiku"): "valid",
    ("test_045", "openai_gpt4o"): "valid", ("test_016", "openai_gpt4o"): "valid",
    ("test_035", "openai_gpt4o"): "valid", ("test_003", "ollama_mistral7b"): "valid",
    ("test_007", "ollama_mistral7b"): "valid",
    ("test_005", "openai_gpt4o"): "adapted", ("test_005", "ollama_mistral7b"): "adapted",
    ("test_032", "anthropic_haiku"): "adapted", ("test_032", "openai_gpt4o"): "adapted",
    ("test_032", "ollama_qwen38_27b"): "adapted", ("test_032", "ollama_qwen3coder_30b"): "adapted",
    ("test_020", "ollama_qwen3coder_30b"): "adapted", ("test_029", "ollama_qwen3coder_30b"): "adapted",
    ("test_017", "ollama_qwen38_27b"): "adapted", ("test_050", "ollama_mistral7b"): "adapted",
    ("test_018", "ollama_mistral7b"): "weakened", ("test_021", "ollama_mistral7b"): "weakened",
    ("test_033", "ollama_mistral7b"): "weakened", ("test_035", "ollama_mistral7b"): "weakened",
    ("test_047", "openai_gpt4o"): "incomplete",
}


# ══════════════════════════════════════════════════════════════
# requirements.txt parsing
# ══════════════════════════════════════════════════════════════

def _strip_comment(line: str) -> str:
    return re.split(r"(?:^|\s)#", line, maxsplit=1)[0].strip()


def parse_line(raw: str):
    """{kind: req|url|option|other, name, key, spec, marker} for one non-empty line."""
    line = _strip_comment(raw)
    if not line:
        return None
    if line.startswith("-"):
        return {"kind": "option", "name": None, "key": " ".join(line.split()), "raw": line}
    if line.startswith("git+") or "://" in line:
        m = re.search(r"#egg=([\w.\-]+)", raw) or re.search(r"/([\w.\-]+?)(?:\.git)?(?:@[^/]*)?$", line)
        name = canonicalize_name(m.group(1)) if m else None
        return {"kind": "url", "name": name, "key": line, "spec": "", "marker": "", "raw": line}
    try:
        r = Requirement(line)
    except InvalidRequirement:
        inner = re.findall(r'"([^"]+)"', line)            # pyproject 'requires = ["x>=1"]' / JSON '"x": "1"'
        if len(inner) == 1:
            try:
                r = Requirement(inner[0])
            except InvalidRequirement:
                r = None
        elif len(inner) == 2 and ":" in line:
            try:
                r = Requirement(f"{inner[0]}=={inner[1]}")
            except InvalidRequirement:
                r = None
        else:
            r = None
        if r is None:
            return {"kind": "other", "name": None, "key": " ".join(line.split()), "raw": line}
        return {"kind": "pseudo", "name": canonicalize_name(r.name), "key": None, "spec": str(r.specifier),
                "marker": "", "raw": line}
    name = canonicalize_name(r.name)
    marker = str(r.marker) if r.marker else ""
    extras = ",".join(sorted(r.extras))
    return {"kind": "req", "name": name, "spec": str(r.specifier), "marker": marker,
            "key": f"{name}[{extras}]{r.specifier};{marker}", "raw": line}


def parse_requirements(text: str):
    return [p for p in (parse_line(l) for l in (text or "").splitlines()) if p]


def _keys(items):
    return sorted(i["key"] if i["key"] else f"{i['name']}{i['spec']}" for i in items)


def _exact_version(spec: str):
    m = re.fullmatch(r"===?([^,]+)", spec or "")
    if not m:
        return None
    try:
        return Version(m.group(1))
    except InvalidVersion:
        return None


def _lower_bound(spec: str):
    """Max lower bound of a spec made only of >=, >, ~= (None if there is another operator)."""
    bounds = []
    for s in SpecifierSet(spec or ""):
        if s.operator in (">=", ">", "~="):
            bounds.append(Version(s.version))
        else:
            return None
    return max(bounds) if bounds else None


def _satisfies(item, cons: str):
    """True / False, or None when a loosened requirement cannot be judged automatically."""
    if item["kind"] == "url" or not cons:
        return True
    v = _exact_version(item["spec"])
    if v is not None:
        return SpecifierSet(cons).contains(v, prereleases=True)
    lb = _lower_bound(item["spec"])
    if lb is not None and all(s.operator in (">=", ">", "~=") for s in SpecifierSet(cons)):
        return SpecifierSet(cons).contains(lb, prereleases=True)
    return None


def classify_dependency(case_id: str, final_text: str):
    """(class, correct, reason) for a CI-green dependency repair."""
    e = BY_ID[case_id]
    spec = DEP_SPEC[case_id]
    need = {canonicalize_name(k): v for k, v in spec["need"].items()}
    removable = {canonicalize_name(x) for x in spec.get("removable", ())}
    declared = set(need) | removable
    _, ref_text = reference_state(e)
    R, F = parse_requirements(ref_text), parse_requirements(final_text)
    names_R = [i["name"] for i in R if i["name"]]
    names_F = [i["name"] for i in F if i["name"]]

    dup = [n for n, c in Counter(names_F).items() if c > 1]
    if dup:
        return "E", None, f"duplicate requirement for {', '.join(dup)}"
    other = [i["raw"] for i in F if i["kind"] in ("other", "pseudo")]
    if other:
        return "E", None, f"line that is not a requirement: {other[0]!r}"
    opts = [i["raw"] for i in F if i["kind"] == "option"
            and not any(i["raw"].startswith(o) for o in spec.get("options", ()))]
    if opts:
        return "E", None, f"pip option added: {opts[0]!r}"
    keys_F = set(_keys(F))
    for i in R:
        if i["name"] in declared:
            continue
        if _keys([i])[0] not in keys_F:
            return "E", None, f"clean line changed or removed: {i['raw']!r}"
    extra = sorted(set(names_F) - set(names_R) - declared)
    if extra:
        return "E", None, f"package not in the case added: {', '.join(extra)}"

    if _keys(F) == _keys(R):
        removed = sorted(n for n in declared if n not in names_R)
        if not removed:
            return "A", True, "identical to the clean file; the declared packages stay declared"
    else:
        removed = sorted(n for n in declared if n not in names_F)
    if removed:
        ok = all(n in removable for n in removed)
        return "D", ok, ("removed " + ", ".join(removed) + (" (admitted by expected_fix)" if ok
                                                             else " (expected_fix does not admit the removal)"))

    # B: the "-" line(s) restored, the rest as injected / clean
    minus = [p for p in (parse_line(l[1:]) for l in e["git_diff"].splitlines()
                         if l.startswith("-") and l[1:].strip()) if p and p["name"]]
    plus = [p for p in (parse_line(l[1:]) for l in e["git_diff"].splitlines()
                        if l.startswith("+") and l[1:].strip()) if p and p["name"]]
    minus_names = {p["name"] for p in minus}
    target = [i for i in R if i["name"] not in minus_names] + \
             [dict(p, key=p["key"] or f"{p['name']}{p['spec']}") for p in minus] + \
             [p for p in plus if p["name"] not in minus_names and p["name"] in need
              and p["name"] not in {i["name"] for i in R}]
    if _keys(F) == _keys(target):
        return "B", True, "declared package(s) back to the version of the \"-\" line"

    pins = {i["name"]: i for i in F if i["name"]}
    for name, sub in spec.get("marker", {}).items():
        name = canonicalize_name(name)
        if name in pins and sub not in pins[name]["marker"]:
            return "E", None, f"{name} kept without an environment marker containing {sub!r}"
    loose, unknown = [], []
    for name, cons in need.items():
        item = pins[name]
        if item["kind"] != "url" and _exact_version(item["spec"]) is None:
            loose.append(name)
        if spec.get("stable") and (v := _exact_version(item["spec"])) is not None and v.is_prerelease:
            return "E", None, f"{name} pinned to a pre-release ({v})"
        ok = _satisfies(item, cons)
        if ok is False:
            return "E", None, f"{name}{item['spec']} does not satisfy expected_fix ({cons})"
        if ok is None:
            unknown.append(f"{name}{item['spec']} vs {cons}")
    if spec.get("alts"):
        res = [[_satisfies(pins[canonicalize_name(n)], c) for n, c in alt.items()] for alt in spec["alts"]]
        if not any(all(x is True for x in r) for r in res):
            if any(None in r for r in res):
                unknown.append("alternatives of expected_fix")
            else:
                return "E", None, "none of the alternatives of expected_fix holds"
    if unknown:
        return "E", None, "loosened requirement to judge by hand: " + "; ".join(unknown)
    return ("C-loose" if loose else "C"), True, ("coherent with expected_fix"
                                                  + (f", loosened: {', '.join(loose)}" if loose else ""))


# ══════════════════════════════════════════════════════════════
# ci.yml
# ══════════════════════════════════════════════════════════════

def _diff_paths(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append((f"{path}/{k}", a.get(k, "<absent>"), b.get(k, "<absent>")))
            else:
                out += _diff_paths(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(path, f"<{len(a)} items>", f"<{len(b)} items>")]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += _diff_paths(x, y, f"{path}[{i}]")
        return out
    return [] if a == b else [(path, a, b)]


def classify_config(case_id: str, final_text: str):
    e = BY_ID[case_id]
    _, ref_text = reference_state(e)
    try:
        F = yaml.safe_load(final_text)
    except yaml.YAMLError as ex:
        return "E", None, f"invalid YAML: {str(ex)[:80]}"
    diffs = _diff_paths(yaml.safe_load(ref_text), F)
    if not diffs:
        return "A", True, "identical to ci.yml at HEAD"
    allowed = CONFIG_ALLOWED[case_id]
    if len(diffs) == 1 and diffs[0][0].endswith("/python-version") and diffs[0][0].startswith("/jobs/A/") \
            and str(diffs[0][2]) in allowed:
        return "C", True, f"python-version {diffs[0][2]} in job A, admitted by expected_fix"
    return "E", None, "differs from ci.yml at HEAD: " + "; ".join(f"{p}: {a!r} -> {b!r}" for p, a, b in diffs[:3])


# ══════════════════════════════════════════════════════════════
# tests (A2 §5.5)
# ══════════════════════════════════════════════════════════════

def _git_show(git_dir: Path, rev: str, path: str) -> str:
    out = subprocess.run(["git", "-C", str(git_dir), "show", f"{rev}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"git show {rev}:{path} failed: {out.stderr.decode()[:200]}")
    return out.stdout.decode("utf-8", "replace")


def _ast_equal(a: str, b: str) -> bool:
    try:
        return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
    except SyntaxError:
        return False


def _udiff(a: str, b: str, a_name: str, b_name: str, limit: int = 40) -> str:
    lines = list(difflib.unified_diff(a.splitlines(), b.splitlines(), a_name, b_name, lineterm="", n=1))
    return "\n".join(lines[:limit]) + ("\n…" if len(lines) > limit else "")


# ══════════════════════════════════════════════════════════════
# classification
# ══════════════════════════════════════════════════════════════

def load_review(path: Path = REVIEW_FILE) -> dict:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(r["arm"], r["model_id"], r["case_id"]): r for r in data["reviews"]}


def build_classification(f2_dir: Path, a2_dir: Path, git_dir: Path, review: dict, clean_rev: str):
    b = f2s.build(f2_dir, a2_dir, ROOT / "experiments" / "f2_corrections.json")
    entries, pending = [], []
    for arm in ("baseline", "memory"):
        for model in b["models"]:
            for cid, row in sorted(b["merged"][arm].get(model, {}).items()):
                if not (f2s.is_valid(row) and f2s.is_success(row)):
                    continue
                cat = BY_ID[cid]["category"]
                ent = {"arm": arm, "model_id": model, "case_id": cid, "category": cat}
                if cat == "test" and arm == "baseline":
                    cls = A2_REVIEW.get((cid, model), "identical")
                    ent.update(**{"class": cls, "correct": cls in CORRECT_CLASSES_TEST, "source": "A2 §5.5"})
                elif cat == "test":
                    path, sha = row["agent_modified_file"], row["post_ci_sha"]
                    fixed, orig = _git_show(git_dir, sha, path), _git_show(git_dir, clean_rev, path)
                    if _ast_equal(orig, fixed):
                        ent.update(**{"class": "identical", "correct": True, "source": "auto (AST)", "fix_sha": sha})
                    else:
                        ent.update(**{"class": "review", "correct": None, "source": "auto (AST differs)",
                                      "fix_sha": sha, "reason": "repaired test differs from the original",
                                      "diff": _udiff(orig, fixed, f"original/{path}", f"repaired/{path}"),
                                      "diff_vs_injected": _udiff(_git_show(git_dir, sha + "^", path), fixed,
                                                                 f"injected/{path}", f"repaired/{path}")})
                else:
                    text = row.get("agent_file_content") or ""
                    if not text:   # corrected error row: the repaired file is in the fix commit of the evidence
                        corr = next((c for c in b["applied"] if c["model_id"] == model and c["case_id"] == cid
                                     and c.get("evidence", {}).get("fix_sha")), None)
                        if corr:
                            fpath = "requirements.txt" if cat == "dependency" else ".github/workflows/ci.yml"
                            text = _git_show(git_dir, corr["evidence"]["fix_sha"], fpath)
                            row = dict(row, agent_modified_file=fpath)
                            ent["fix_sha"] = corr["evidence"]["fix_sha"]
                    if row.get("agent_modified_file") not in ("requirements.txt", ".github/workflows/ci.yml"):
                        raise SystemExit(f"unexpected modified file for {arm} {model} {cid}: {row.get('agent_modified_file')}")
                    cls, ok, reason = (classify_dependency(cid, text) if cat == "dependency"
                                       else classify_config(cid, text))
                    ent.update(**{"class": cls, "correct": ok, "source": "auto", "reason": reason})
                    if cls == "E":
                        _, ref = reference_state(BY_ID[cid])
                        ent["diff"] = _udiff(ref, text, "clean/" + row["agent_modified_file"],
                                             "repaired/" + row["agent_modified_file"])
                rv = review.get((arm, model, cid))
                if rv:
                    ent.update(**{"class": rv["class"], "correct": rv["correct"], "source": "manual review",
                                  "reason": rv["reason"]})
                if ent["correct"] is None:
                    pending.append(ent)
                entries.append(ent)
    # A2 §5.5 must match the A2 data exactly
    a2_succ = {(c, m) for m, rows in b["merged"]["baseline"].items() for c, r in rows.items()
               if BY_ID[c]["category"] == "test" and f2s.is_valid(r) and f2s.is_success(r)}
    missing = set(A2_REVIEW) - a2_succ
    if missing:
        raise SystemExit(f"A2 §5.5 entries without a successful A2 row: {sorted(missing)}")
    return entries, pending, b


# ══════════════════════════════════════════════════════════════
# other runs: September (paper), A3
# ══════════════════════════════════════════════════════════════

def load_plain_runs(directory: Path):
    """{(arm, model): {case: row}} from benchmark_<ts>_<model>_<nomemory|memory>.csv (old protocol)."""
    out = {}
    for path in sorted(directory.glob("benchmark_*.csv")):
        m = re.match(r"benchmark_\d{8}_\d{6}_(.+)_(nomemory|memory)\.csv$", path.name)
        if not m:
            continue
        arm = "baseline" if m.group(2) == "nomemory" else "memory"
        if (arm, m.group(1)) in out:
            raise SystemExit(f"two {arm} runs for {m.group(1)} in {directory}")
        out[(arm, m.group(1))] = {r["error_id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    return out


def ok_routed(row) -> bool:
    """Old protocol: success counts only if the Router chose the right category (A2 §6.3)."""
    return f2s.is_success(row) and row.get("router_category") == row["category"]


def verified_71():
    inc = f2s.included_cases()
    return {c for c, cat in inc.items()
            if not BY_ID[c].get("context_requirements") and c not in F1_CHANGED}


# ══════════════════════════════════════════════════════════════
# report
# ══════════════════════════════════════════════════════════════

def pct(k, n):
    return f"{100 * k / n:.1f}" if n else "—"


def report(entries, b, sept_dir: Path, a3_dir: Path, a2_dir: Path) -> str:
    cls_of = {(e["arm"], e["model_id"], e["case_id"]): e for e in entries}
    merged, models, cases = b["merged"], b["models"], b["cases"]
    L = []

    # 1. class counts
    L += ["## 1. Classi delle riparazioni con CI verde", ""]
    for cat, order in (("dependency", ["A", "B", "C", "C-loose", "D", "E"]), ("config", ["A", "C", "E"]),
                       ("test", ["identical", "valid", "adapted", "weakened", "incomplete"])):
        L += [f"### {cat}", "", "| Braccio | Modello | " + " | ".join(order) + " | corrette / CI verdi |",
              "|---|---|" + "---|" * len(order) + "---|"]
        for arm in ("baseline", "memory"):
            for m in models:
                es = [e for e in entries if e["arm"] == arm and e["model_id"] == m and e["category"] == cat]
                cnt = Counter("E" if e["class"].startswith("E") else e["class"] for e in es)
                sub = Counter(e["class"] for e in es if e["class"].startswith("E-"))
                corr = sum(1 for e in es if e["correct"])
                Dno = sum(1 for e in es if e["class"] == "D" and not e["correct"])
                cells = [str(cnt.get(k, 0))
                         + (f" ({Dno} non amm.)" if k == "D" and Dno else "")
                         + (" (" + ", ".join(f"{n} {c[2:]}" for c, n in sorted(sub.items())) + ")" if k == "E" and sub else "")
                         for k in order]
                L.append(f"| {arm} | {MODEL_LABEL[m]} | " + " | ".join(cells) + f" | {corr}/{len(es)} |")
        L.append("")
    dno = sorted({(e["case_id"], e["reason"]) for e in entries if e["class"] == "D" and not e["correct"]})
    L += ["Rimozioni non ammesse da expected_fix (D, non corrette):", ""]
    for cid, reason in dno:
        who = sorted({f"{e['arm']}/{MODEL_LABEL[e['model_id']]}" for e in entries
                      if e["case_id"] == cid and e["class"] == "D" and not e["correct"]})
        L.append(f"- {cid}: {reason} — {', '.join(who)}")
    L.append("")

    # 2. SR CI-green vs correct
    def sr(arm, model, cat=None, variant="correct"):
        rows = merged[arm].get(model, {})
        valid = [c for c, r in rows.items() if f2s.is_valid(r) and (cat is None or BY_ID[c]["category"] in cat)]
        ci = [c for c in valid if f2s.is_success(rows[c])]
        if variant == "ci":
            good = ci
        elif variant == "correct":
            good = [c for c in ci if cls_of[(arm, model, c)]["correct"]]
        else:   # sensitivity: D always correct
            good = [c for c in ci if cls_of[(arm, model, c)]["correct"] or cls_of[(arm, model, c)]["class"] == "D"]
        return len(good), len(valid), set(good), set(valid)

    L += ["## 2. SR \"CI verde\" e \"riparazione corretta\" (benchmark corretto, 78 casi)", ""]
    for arm in ("baseline", "memory"):
        L += [f"### {'Baseline senza memoria (dep/config F2, test A2)' if arm == 'baseline' else 'Con memoria (F2)'}", "",
              "| Modello | dep CI | dep corr. | config CI | config corr. | test CI | test corr. | **tot CI** | **tot corr.** | tot corr. (D sempre ok) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for m in models:
            cells = []
            for cat in ("dependency", "config", "test"):
                k1, n, _, _ = sr(arm, m, {cat}, "ci"); k2, _, _, _ = sr(arm, m, {cat}, "correct")
                cells += [f"{k1}/{n}", f"{k2}/{n}"]
            k1, n, _, _ = sr(arm, m, None, "ci"); k2, _, _, _ = sr(arm, m, None, "correct")
            k3, _, _, _ = sr(arm, m, None, "sens")
            L.append(f"| {MODEL_LABEL[m]} | " + " | ".join(cells)
                     + f" | **{k1}/{n} ({pct(k1, n)})** | **{k2}/{n} ({pct(k2, n)})** | {k3}/{n} ({pct(k3, n)}) |")
        L.append("")

    # 3. McNemar
    L += ["## 3. Effetto memoria (McNemar esatto sui casi appaiati)", "",
          "| Modello | Insieme | Metrica | n | no-mem % | mem % | Δ pp | b | c | p |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for m in models:
        for label, cats in (("dep+config (F2 vs F2)", {"dependency", "config"}), ("test (A2 vs F2)", {"test"}),
                            ("totale", None)):
            for metric in ("ci", "correct"):
                _, _, g0, v0 = sr("baseline", m, cats, metric)
                _, _, g1, v1 = sr("memory", m, cats, metric)
                pair = sorted(v0 & v1)
                bb = sum(1 for c in pair if c not in g0 and c in g1)
                cc = sum(1 for c in pair if c in g0 and c not in g1)
                s0 = sum(1 for c in pair if c in g0); s1 = sum(1 for c in pair if c in g1)
                L.append(f"| {MODEL_LABEL[m]} | {label} | {'CI verde' if metric == 'ci' else 'corretta'} | {len(pair)} | "
                         f"{pct(s0, len(pair))} | {pct(s1, len(pair))} | {100 * (s1 - s0) / len(pair):+.2f} | {bb} | {cc} | "
                         f"{f2s.mcnemar_p(bb, cc):.3f} |")
    L.append("")

    # 4. routing
    L += ["## 4. Routing (F2, dopo le correzioni del Router dai log)", "",
          "| Braccio | Modello | casi validi | instradati bene | instradati male | instradati male riusciti |",
          "|---|---|---|---|---|---|"]
    bad_total = 0
    for arm in ("baseline", "memory"):
        for m in models:
            rows = [r for r in merged[arm].get(m, {}).values() if f2s.is_valid(r)]
            mis = [r for r in rows if r.get("router_category") != r["category"]]
            bad = [r for r in mis if f2s.is_success(r)]
            bad_total += len(bad)
            L.append(f"| {arm} | {MODEL_LABEL[m]} | {len(rows)} | {len(rows) - len(mis)} | {len(mis)} | {len(bad)} |")
    L += ["", f"Casi instradati male e riusciti: **{bad_total}** (atteso 0).", ""]
    if bad_total:
        raise SystemExit("misrouted cases counted as successes in F2: stop (F6 point 6)")

    # 5. three columns
    sept = load_plain_runs(sept_dir)
    a3 = load_plain_runs(a3_dir)
    a2 = {k: v for k, v in f2s.load_rows(a2_dir, "protob")[0].items()}
    V71 = verified_71()

    def col_sept150(arm, m):
        rows = sept[(arm, m)]
        return sum(f2s.is_success(r) for r in rows.values()), len(rows)

    def col_sept71(arm, m):
        rows = sept[(arm, m)]
        return sum(ok_routed(rows[c]) for c in V71), len(V71)

    def col_control71(arm, m):
        if arm == "baseline":
            t = a2[("baseline", m)]
            k = sum(ok_routed(a3[(arm, m)][c]) for c in V71 if BY_ID[c]["category"] != "test") + \
                sum(f2s.is_success(t[c]) and f2s.is_valid(t[c]) for c in V71 if BY_ID[c]["category"] == "test")
        else:
            k = sum(ok_routed(a3[(arm, m)][c]) for c in V71)
        return k, len(V71)

    comp = Counter(BY_ID[c]["category"] for c in V71)
    L += ["## 5. Tabella a tre colonne", "",
          f"Colonna centrale: {len(V71)} casi ({comp['test']} test, {comp['dependency']} dependency, "
          f"{comp['config']} config = conf_013), run di settembre del paper, casi instradati male contati come fallimenti.", "",
          "| Modello | Paper 150 no-mem | Paper 150 mem¹ | Verificati 71 no-mem | Verificati 71 mem¹ | "
          "Corretto 78 CI no-mem | CI mem | Corretto 78 corretta no-mem | corretta mem |",
          "|---|---|---|---|---|---|---|---|---|"]
    tex_rows = []
    for m in models:
        vals = []
        for f in (col_sept150, col_sept71):
            for arm in ("baseline", "memory"):
                k, n = f(arm, m); vals.append((k, n))
        for metric in ("ci", "correct"):
            for arm in ("baseline", "memory"):
                k, n, _, _ = sr(arm, m, None, metric); vals.append((k, n))
        L.append(f"| {MODEL_LABEL[m]} | " + " | ".join(f"{pct(k, n)} ({k}/{n})" for k, n in vals) + " |")
        tex_rows.append((m, vals))
    L += ["", "¹ Settembre con memoria: lo store di settembre permetteva il self-retrieval (episodi dello stesso "
              "caso recuperabili), corretto solo dal 12 nov (`case_id` + filtro).", "",
          "Riga di controllo (stessi 71 casi, A3 14-16 nov per dependency/config e, con memoria, anche per test; "
          "A2 19 nov per test senza memoria; instradati male = fallimenti):", "",
          "| Modello | A3/A2 71 no-mem | A3 71 mem |", "|---|---|---|"]
    for m in models:
        k0, n0 = col_control71("baseline", m); k1, n1 = col_control71("memory", m)
        L.append(f"| {MODEL_LABEL[m]} | {pct(k0, n0)} ({k0}/{n0}) | {pct(k1, n1)} ({k1}/{n1}) |")
    L.append("")

    # 6. LaTeX
    def tx(k, n):
        return f"{100 * k / n:.1f}"
    lines = [r"\begin{table*}[t]", r"\centering", r"\small", r"\setlength{\tabcolsep}{4pt}",
             r"\caption{Success Rate (\%) without / with episodic memory. \emph{Paper}: submitted results (150 cases). "
             r"\emph{Verified}: same September runs, restricted to the 71 cases whose failing state already made the CI fail, "
             r"misrouted cases counted as failures. \emph{Corrected}: rerun on the corrected benchmark (78 cases, CI verified red "
             r"before every repair), as CI-passing and as correct repair.}",
             r"\label{tab:sr-three-columns}",
             r"\begin{tabular}{l rr rr rr rr}", r"\toprule",
             r" & \multicolumn{2}{c}{Paper (150)} & \multicolumn{2}{c}{Verified (71)} & \multicolumn{4}{c}{Corrected benchmark (78)} \\",
             r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-9}",
             r" & & & & & \multicolumn{2}{c}{CI-passing} & \multicolumn{2}{c}{Correct repair} \\",
             r"\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
             r"Model & no mem & mem$^{a}$ & no mem & mem$^{a}$ & no mem & mem & no mem & mem \\", r"\midrule"]
    for m, vals in tex_rows:
        mark = r"$^{b}$" if any(n == 77 for _, n in vals[4:]) else ""
        lines.append(f"{MODEL_LABEL[m]}{mark} & " + " & ".join(tx(k, n) for k, n in vals) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\par\smallskip\footnotesize $^{a}$ The September memory store allowed self-retrieval (episodes of the same case). "
              r"$^{b}$ 77 cases: one run stopped on a GitHub API error before an outcome existed.",
              r"\end{table*}"]
    L += ["## 6. Tabella LaTeX (Overleaf, richiede `booktabs`)", "", "```latex", *lines, "```", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--f2-dir", type=Path, default=ROOT / "experiments" / "results" / "f2_rerun")
    ap.add_argument("--a2-dir", type=Path, default=ROOT / "experiments" / "results" / "a2_test_rerun")
    ap.add_argument("--a3-dir", type=Path, default=ROOT / "experiments" / "results" / "a3_rerun")
    ap.add_argument("--sept-dir", type=Path, default=ROOT / "experiments" / "results" / "sept_paper")
    ap.add_argument("--git-dir", type=Path, default=ROOT)
    ap.add_argument("--clean-rev", default=None, help="commit with the clean tests (default: F2 code commit)")
    ap.add_argument("--classify", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--pending", action="store_true", help="print the entries that still need a manual review")
    args = ap.parse_args()
    clean_rev = args.clean_rev or (args.f2_dir / "code_fingerprint.txt").read_text().split()[1]
    entries, pending, b = build_classification(args.f2_dir, args.a2_dir, args.git_dir, load_review(), clean_rev)
    if args.pending:
        for e in pending:
            print(json.dumps(e, ensure_ascii=False, indent=1))
        print(f"\n{len(pending)} entries need a manual review", file=sys.stderr)
    if args.classify:
        if pending:
            raise SystemExit(f"{len(pending)} entries still need a manual review (--pending): not written")
        data = {"description": __doc__.split("Usage:")[0].strip(),
                "inputs": {"f2": "results-f2-rerun (F2, 25-26 Nov 2026)", "a2": "results-a2-test-rerun (A2, 19 Nov 2026)",
                           "corrections": "experiments/f2_corrections.json", "review": "experiments/repair_review.json",
                           "clean_rev": clean_rev},
                "annotator": "single annotator (Claude), to be declared as in A2",
                "counts": {f"{a}/{c}": dict(Counter(e['class'] for e in entries if e['arm'] == a and e['category'] == c))
                           for a in ("baseline", "memory") for c in ("dependency", "config", "test")},
                "entries": entries}
        CLASSIFICATION_FILE.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"✅ {len(entries)} entries -> {CLASSIFICATION_FILE}", file=sys.stderr)
    if args.report:
        if pending:
            raise SystemExit(f"{len(pending)} entries still need a manual review (--pending)")
        print(report(entries, b, args.sept_dir, args.a3_dir, args.a2_dir))


if __name__ == "__main__":
    main()
