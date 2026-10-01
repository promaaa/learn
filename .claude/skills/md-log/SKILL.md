---
name: md-log
description: Link a markdown file to this session so it is mirrored to Obsidian and opened there (the Claude Code port of the pi `/md-log` command). Use for "/md-log <file>" and "/md-log off".
argument-hint: <file.md> | off
disable-model-invocation: true
---

# md-log

Arguments: `$ARGUMENTS`

- If the argument is `off` (or `unlink`), run `python3 .claude/hooks/md_log.py unlink`.
- Otherwise run `python3 .claude/hooks/md_log.py link "<file>"`. The file must already exist; if it doesn't, say so and offer to create it with a single `# <topic> · <date>` heading.

Report the result in one line. From then on, follow "The Obsidian log" in the `teach` skill.
