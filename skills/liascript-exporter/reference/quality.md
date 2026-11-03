# Quality checks (spelling and style)

## 6. Quality Check Tools

### 6.1 CSpell (Spell Checking)

```bash
npm install -g cspell
npx cspell --locale en-US --show-suggestions "**/*.md"

# German support
npm install -g @cspell/dict-de-de
npx cspell --locale en-US,de-DE --show-suggestions "**/*.md"
```

**Config file `.cspell.json`:**
```json
{
  "version": "0.2",
  "language": "en-US",
  "ignoreWords": [
    "LiaScript", "Markdown", "GitHub", "workflow"
  ],
  "dictionaries": ["en_US"]
}
```

**Inline language switching:**
```markdown
<!-- cspell:language de-DE -->
Hier ist ein deutscher Absatz.
<!-- cspell:language en-US -->
Here is an English paragraph.
```

### 6.2 Write-Good (Style Checking)

Flags: passive voice, weasel words, clichés, redundant phrases.

```bash
npm install -g write-good
npx write-good *.md
npx write-good *.md --no-passive    # disable passive voice check
```

Options: `--no-passive`, `--no-illusion`, `--no-so`, `--no-adverb`, `--no-tooWordy`, `--no-cliches`

**German:** `npm install -g schreib-gut && write-good *.md --checks=schreib-gut`

### 6.3 Alex (Inclusive Language)

Flags: gender bias, ableist language, racially insensitive terms.

```bash
npm install -g alex
npx alex *.md
```

**Config `.alexrc`:**
```json
{ "allow": ["special"] }
```

### 6.4 Proselint (Advanced Style)

Flags: redundancy, jargon, typography, consistency.

```bash
npm install -g proselint && pip install proselint
npx proselint *.md
```

**Config `.proselintrc`:**
```json
{
  "checks": {
    "typography.diacritical_marks": false,
    "typography.exclamation": false
  }
}
```
