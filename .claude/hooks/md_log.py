#!/usr/bin/env python3
"""md-log for Claude Code: mirror a tutoring session to a markdown file rendered in Obsidian.

Port of `extensions/md-log.ts` (the pi extension). Claude Code keeps no reliable copy of the
assistant's visible text in its transcript, so the work is split:

  hooks (this script, automatic)       Claude (explicitly, via `say`)
  ------------------------------       ------------------------------
  user prompts    > [!quote] YOU       lesson prose, grading, plans, summaries
  questions, live > [!question]          > [!abstract] CLAUDE  (and success/failure
  answers         > [!example]  (appended below the question)            callouts when grading)

Usage:
  md_log.py link <file>     link an existing .md file to this project's session and open it in Obsidian
  md_log.py unlink          stop logging
  md_log.py say             append stdin as a CLAUDE block (or as-is with --raw)
  md_log.py hook            called by Claude Code hooks; reads the event JSON on stdin

The link lives in <project>/.md-log.json. A fresh session (startup or /clear) drops it; resume keeps it.
Append-only like the original: the question keeps its numbered options and the answer is added below it. Never prints to stdout from a hook, so nothing reaches the model.
"""

import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path


def project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def state_path() -> Path:
    return project_dir() / ".md-log.json"


def linked_file() -> Path | None:
    try:
        f = json.loads(state_path().read_text()).get("file")
    except (OSError, ValueError):
        return None
    return Path(f) if f else None


def append(text: str) -> None:
    f = linked_file()
    if not f:
        return
    try:
        current = f.read_text(encoding="utf-8") if f.exists() else ""
        prefix = "\n\n" if current.strip() else ""
        f.write_text(current.rstrip("\n") + prefix + text.rstrip("\n") + "\n", encoding="utf-8")
    except OSError:
        pass  # file deleted or moved externally; ignore


def callout(kind: str, title: str, body: list[str]) -> str:
    lines = [f"> [!{kind}] {title}"]
    lines += [">" if not line else f"> {line}" for line in body]
    return "\n".join(lines)


def open_in_obsidian(f: Path) -> None:
    uri = "obsidian://open?path=" + urllib.parse.quote(str(f), safe="")
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.Popen([opener, uri], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


# --- Formatting of the mirrored events ---


def question_block(questions: list[dict]) -> str:
    blocks = []
    for q in questions:
        body = q.get("question", "").split("\n")
        opts = q.get("options") or []
        if opts:
            body.append("")
            for i, o in enumerate(opts, 1):
                line = f"{i}. {o.get('label', '')}"
                if o.get("description"):
                    line += f": {o['description']}"
                body.append(line)
                if o.get("preview"):
                    # Previews hold matrices / code; keep them readable in a fence
                    # unless they are already LaTeX.
                    prev = o["preview"].split("\n")
                    body += prev if "$" in o["preview"] else ["```", *prev, "```"]
        title = f"Question: {q['header']}" if q.get("header") else "Question"
        if q.get("multiSelect"):
            title += " (several answers)"
        blocks.append(callout("question", title, body))
    return "\n\n".join(blocks)


def answer_label(q: dict, answer: str) -> str:
    """'2. label' when the answer is one of the options (as in the pi log), else the free text."""
    for i, o in enumerate(q.get("options") or [], 1):
        if o.get("label") == answer:
            return f"{i}. {answer}"
    return f"Other: {answer}" if answer else "(no answer)"


def answer_block(tool_input: dict, tool_response) -> str:
    """The learner's answers, appended below the live question block (which keeps its options)."""
    answers = {}
    annotations = {}
    if isinstance(tool_response, dict):
        answers = tool_response.get("answers") or {}
        annotations = tool_response.get("annotations") or {}
    answers = answers or tool_input.get("answers") or {}
    blocks = []
    for q in tool_input.get("questions") or []:
        text = q.get("question", "")
        # Several answers (multiSelect) come back comma-separated.
        raw = answers.get(text, "")
        parts = [a.strip() for a in raw.split(",")] if q.get("multiSelect") and raw else [raw]
        body = [f"Your answer: {answer_label(q, a)}" for a in parts]
        notes = (annotations.get(text) or {}).get("notes")
        if notes:
            body += ["", f"Note: {notes}"]
        title = f"Answer: {q['header']}" if q.get("header") else "Answer"
        blocks.append(callout("example", title, body))
    if not blocks and isinstance(tool_response, str) and tool_response.strip():
        blocks.append(callout("example", "Answer", [tool_response.strip()]))
    return "\n\n".join(blocks) or callout("example", "Answer", ["(no answer)"])


def user_block(prompt: str) -> str:
    return f"> [!quote] YOU\n\n{prompt.strip()}"


# --- Commands ---


def cmd_link(arg: str) -> int:
    f = Path(arg).expanduser()
    if not f.is_absolute():
        f = project_dir() / f
    f = f.resolve()
    # Like /md-log in pi: link an existing file only, never create one from a typo'd path.
    if not f.is_file():
        print(f"md-log: file does not exist: {f}", file=sys.stderr)
        return 1
    state_path().write_text(json.dumps({"file": str(f)}) + "\n")
    if not os.environ.get("MD_LOG_NO_OPEN"):  # set in tests
        open_in_obsidian(f)
    print(f"md-log: linked {f} (opened in Obsidian)")
    return 0


def cmd_unlink() -> int:
    f = linked_file()
    try:
        state_path().unlink()
    except FileNotFoundError:
        pass
    print(f"md-log: unlinked {f.name}" if f else "md-log: no file linked")
    return 0


def cmd_say(raw: bool) -> int:
    if not linked_file():
        print("md-log: no file linked; run `md_log.py link <file>` first", file=sys.stderr)
        return 1
    text = sys.stdin.read().strip()
    if text:
        append(text if raw else f"> [!abstract] CLAUDE\n\n{text}")
    return 0


def cmd_hook() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    name = event.get("hook_event_name")

    if name == "SessionStart":
        if event.get("source") in ("startup", "clear"):
            try:
                state_path().unlink()
            except FileNotFoundError:
                pass
        return 0

    if not linked_file():
        return 0

    if name == "UserPromptSubmit":
        prompt = event.get("prompt") or ""
        if prompt.strip():
            append(user_block(prompt))
    elif name == "PreToolUse" and event.get("tool_name") == "AskUserQuestion":
        # Written before the learner answers, so the question renders live in Obsidian.
        qs = (event.get("tool_input") or {}).get("questions") or []
        if qs:
            append(question_block(qs))
    elif name == "PostToolUse" and event.get("tool_name") == "AskUserQuestion":
        # Like the pi log: the question block stays (with its options), the answer goes below it.
        append(answer_block(event.get("tool_input") or {}, event.get("tool_response")))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "link" and len(args) == 2:
        return cmd_link(args[1])
    if args[0] == "unlink":
        return cmd_unlink()
    if args[0] == "say":
        return cmd_say("--raw" in args)
    if args[0] == "hook":
        return cmd_hook()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
