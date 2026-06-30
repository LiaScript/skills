# Skills

A collection of [Agent Skills](https://agentskills.io) for working with LiaScript and Open Educational Resources. Compatible with GitHub Copilot, Claude Code, Cursor, Gemini CLI, and [50+ other agents](https://agentskills.io/clients).

---

## Available Skills

| Skill | Description |
|-------|-------------|
| [oersi-metadata](skills/oersi-metadata/) | Generate OERSI-compatible `metadata.yml` for GitHub-hosted OER |
| [reference-checker](skills/reference-checker/) | Verify scientific literature references and detect hallucinated citations |
| [exporter-workflow](skills/exporter-workflow/) | Generate LiaScript export workflows, GitHub Actions, and `project.yaml` catalog pages |
| [template-development](skills/template-development/) | Develop LiaScript templates — reusable macros, JS library integration, and async patterns |

---

## oersi-metadata

Generates a valid `metadata.yml` for publishing Open Educational Resources on [OERSI](https://oersi.org). Collects required fields, uses correct Schema.org / LRMI / KIM vocabulary (SKOS URIs for subjects, HCRT URIs for resource types), and explains how to configure the GitHub repository for automatic indexing.

**Activates when:** a user wants to publish OER on OERSI, create or update a `metadata.yml`, or asks about the `open-educational-resources` GitHub topic.

---

## reference-checker

Systematically verifies scientific literature references using web search. Outputs a structured three-tier report (✅ correct / ⚠️ warning / 🚨 critical error) with a mandatory summary table. Explicitly flags potentially hallucinated AI-generated citations. Output language matches the user's input language.

**Activates when:** a user asks to check, verify, or validate bibliographic entries, citations, or references — including single entries.

---

## exporter-workflow

Generates `liaex` CLI commands, GitHub Actions workflows, and `project.yaml` catalog files for LiaScript repositories. Covers all export formats (PDF, SCORM 1.2/2004, IMS, ePub, DOCX, xAPI, Android, web), automated deployment to GitHub Pages, multi-project site patterns, and quality check pipelines. Includes ready-made examples for common scenarios.

**Activates when:** a user wants to export a LiaScript course to any format; create or update a GitHub Actions workflow; build a project website that aggregates multiple courses; set up automated deployment to GitHub Pages; or asks anything involving the `liaex` CLI, `@liascript/exporter`, or LiaScript CI/CD.

---

## template-development

Expert guidance for building LiaScript templates — standard `README.md` courses whose header comment defines reusable macros via `import:`. Covers single-line and block macro syntax, integrating external JavaScript libraries, handling async execution, and the established conventions from the LiaTemplates ecosystem.

**Activates when:** a user wants to build, modify, or debug a LiaScript template; create reusable macros; or integrate a JavaScript library into a LiaScript course.

---

## Installation

### Via `npx skills` (recommended)

[`npx skills`](https://github.com/vercel-labs/skills) is the open CLI for the Agent Skills ecosystem. It auto-detects installed agents and places skills in the correct directories.

```bash
# Preview skills in this repo before installing
npx skills add OWNER/REPO --list

# Install all skills (interactive — detects your agents)
npx skills add OWNER/REPO

# Install a specific skill
npx skills add OWNER/REPO --skill oersi-metadata
npx skills add OWNER/REPO --skill reference-checker
npx skills add OWNER/REPO --skill template-development

# Install to all agents without prompts
npx skills add OWNER/REPO --all

# Install as personal skills (available across all projects)
npx skills add OWNER/REPO --global

# Install for a specific agent
npx skills add OWNER/REPO -a claude-code
npx skills add OWNER/REPO -a github-copilot
npx skills add OWNER/REPO -a cursor
```

> Replace `OWNER/REPO` with the actual GitHub repository path (e.g. `andre-dietrich/skills`).

#### Other useful commands

```bash
npx skills list                  # List all installed skills
npx skills update                # Update installed skills
npx skills remove oersi-metadata # Remove a skill
```

---

### Manual Installation

Copy the skill directory into the skills folder for your agent:

**Project scope** (skills available only in the current project):

| Agent | Directory |
|-------|-----------|
| GitHub Copilot, Cursor, Gemini CLI, Codex | `.agents/skills/` |
| Claude Code | `.claude/skills/` |
| Roo Code | `.roo/skills/` |
| Windsurf | `.windsurf/skills/` |

```bash
# Example: install for Claude Code (project scope)
cp -r skills/oersi-metadata .claude/skills/
cp -r skills/reference-checker .claude/skills/

# Example: install for any agent that uses .agents/skills/
cp -r skills/oersi-metadata .agents/skills/
cp -r skills/reference-checker .agents/skills/
```

**Personal scope** (skills available across all projects):

| Agent | Directory |
|-------|-----------|
| GitHub Copilot | `~/.copilot/skills/` |
| Claude Code | `~/.claude/skills/` |
| Any agent | `~/.agents/skills/` |

```bash
# Example: personal install for GitHub Copilot
cp -r skills/oersi-metadata ~/.copilot/skills/
cp -r skills/reference-checker ~/.copilot/skills/
```

---

## Related

- [Agent Skills specification](https://agentskills.io/specification)
- [npx skills CLI](https://github.com/vercel-labs/skills)
- [Skills directory](https://skills.sh)
- [LiaScript](https://liascript.github.io)
- [OERSI](https://oersi.org)
