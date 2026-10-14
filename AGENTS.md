# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI, …) working on this repository.

## What this repository is

A collection of [Agent Skills](https://agentskills.io) — portable, agent-agnostic instruction packages for working with LiaScript and Open Educational Resources (OER). There is no build, lint, or test tooling: the content is Markdown/YAML, plus a few helper scripts inside some skills, consumed directly by AI agents via the `npx skills` CLI or a manual copy into an agent's skills directory.

Each skill is a self-contained "mini system prompt" that an agent loads on demand when its `description` matches the user's request. Because the `description` field is the *only* signal agents use to decide whether to activate a skill, it is the most important content in the repo.

This file is for working *on* the repository. `npx skills add` only installs the folders under `skills/`, so nothing here reaches the users of the skills.

## Repository layout

```
skills/<skill-name>/
  SKILL.md            # required: YAML frontmatter (name, description, license) + instructions
  examples/           # optional: ready-made reference files linked from SKILL.md
  reference/          # optional: topic files linked from SKILL.md
  scripts/            # optional: helper scripts the skill tells the agent to run
README.md              # human-facing catalog — one table row + one section per skill
AGENTS.md              # this file; CLAUDE.md only imports it
LICENSE                # repo-level MIT license (distinct from each skill's own license field)
```

The list of published skills lives in `README.md`; it is not repeated here so it cannot go stale. Folders under `skills/` that are listed in `.gitignore` (currently `creativity`) are local only: not published, not in the README, not to be referenced from published skills. Adding a skill means adding a `skills/<name>/SKILL.md` directory — there is no registry or index file to update besides `README.md`. A skill's reference material can be nested as deep as its structure needs; pick whichever layout fits.

## Working on a skill

- **`description` is the activation trigger, not documentation.** It must state concretely *when* to use the skill — include example user phrasings, including non-English ones where relevant (see the German trigger phrases in `reference-checker` and `liascript-theming`). Vague descriptions ("helps with X") cause agents to miss or misfire the skill.
- For descriptions longer than a single sentence, use a YAML block scalar (`description: >`) rather than one giant single-line string — see commit `a56a630`, which reformatted two skills for this reason.
- Every `SKILL.md` must open with the three required frontmatter fields: `name`, `description`, `license`. `name` must match the folder name. A missing or thin `description` is treated as a bug (commit `a56a630`, "fix: 2 skills were missing important metadata").
- `license` in frontmatter is per skill (currently `CC0-1.0` for all skills) and independent of the repository's own `LICENSE` file (MIT, for the repo's own code/structure).
- **Naming:** skills that only make sense for LiaScript start with `liascript-`. Generic skills (`oersi-metadata`, `reference-checker`) do not.
- Long skills put copy-paste-ready reference material in `examples/` or `reference/` and link to it from `SKILL.md` rather than inlining everything — follow this pattern for large templates/configs.
- Skills encode hard-won operational gotchas as explicit rules (e.g. liascript-exporter's "never export into the repository source tree" / `force_orphan: true` / `libasound2t64` on Ubuntu 24). When editing, preserve these callouts — they exist because of specific past failures, not generic advice.
- **Scripts** inside a skill are called with paths relative to the skill folder (`python3 scripts/check.py`), never with a path into one person's home directory. Keep them dependency-free where possible (Python standard library); name any required external tool (ImageMagick, `elm`, `chromium`, …) in `SKILL.md`.
- **Cross-reference, don't duplicate.** When two skills touch the same topic (e.g. `liascript-syntax` for course syntax, `liascript-templates` for macro templates, `liascript-asciiart` for drawing diagrams), one explains it and the other points to it by skill name.

## LiaScript versions

The LiaScript skills are checked against the interpreter source. Behaviour that changed between versions is written with the version it depends on, e.g. "after LiaScript 2.1.2 …; up to 2.1.2 …", so a course author knows what works on the interpreter they actually run. Keep the old behaviour as a fallback until most users have the new release, and verify new claims against the source or a test course before writing them down.

## Updating `README.md`

`README.md` is a manually maintained catalog, not generated. When adding, renaming, or removing a skill, update in lockstep:
1. The summary table near the top (`| Skill | Description |`).
2. That skill's own `##` section with a longer description and an "Activates when:" line.
3. The `npx skills add LiaScript/skills --skill <name>` example commands.
4. Cross-references to the skill's name in other skills.

The repo/owner slug used throughout install examples is `LiaScript/skills` — keep it consistent (a prior commit fixed placeholder `OWNER/REPO` values that had leaked in).

## Domain context worth knowing

- **LiaScript** is the interactive-course Markdown dialect these skills target; courses are plain `README.md` files with a header HTML-comment block defining metadata/macros. `liascript-syntax` is the authoring-syntax reference (quizzes, effects, charts, presentation patterns); `liascript-templates` is about building reusable *macro* templates for other courses to `import:`.
- **OERSI** (`oersi-metadata` skill) indexes OER from GitHub repos that carry a `metadata.yml` in schema.org/LRMI/KIM vocabulary and the `open-educational-resources` GitHub topic.
- **`liaex`** (`@liascript/exporter` CLI, `liascript-exporter` skill) turns a LiaScript course into SCORM/PDF/ePub/DOCX/xAPI/Android/web output, and can build multi-course catalog sites from a `project.yaml`.
- **LiaTemplates** (`liascript-templates` skill) is the ecosystem of reusable LiaScript macro templates, each itself a runnable LiaScript course whose header defines the macros.
- **elm-svgbob** renders LiaScript's ` ```ascii ` blocks to SVG (`liascript-asciiart` skill); LiaScript pins a specific package version, so drawing features depend on the LiaScript release.
