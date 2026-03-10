# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Skills collection** — a set of modular AI agent skills designed to automate research, analysis, and content generation workflows. Each skill lives in its own directory with a `SKILL.md` that defines the agent's behavior, data flow, and output format.

## Skills in This Repository

| Directory | Purpose | Output |
|-----------|---------|--------|
| `job-market-analyzer/` | Salary research for tech roles (Chinese & global companies) | Markdown reports + JSON stats |
| `deep-research-electronics/` | Quarterly AI trend analysis for consumer electronics companies | Minimalist PPT via python-pptx |
| `ai-opportunity-map-generator/` | Transform business processes into AI opportunity maps | Single-file HTML+CSS |
| `prototype-prompt-generator/` | Convert product ideas into UI/UX prompts for AI tools (v0, Claude Artifacts) | Structured Markdown prompts |
| `data-visualizer-pro/` | Transform structured data (CSV/Excel/JSON) into interactive HTML chart reports | Single-file interactive HTML |

## Architecture

Each skill follows this structure:
```
<skill-name>/
├── SKILL.md          # Agent definition: workflow, data parsing rules, output format
├── scripts/          # Python helper scripts (data processing, file generation)
├── assets/           # Templates (report_template.md, etc.)
├── references/       # Design/content guidelines referenced in the skill
├── evals/            # Test cases (evals.json) for validating skill output
└── reports/          # Generated output (gitignored or committed as samples)
```

The `SKILL.md` is the primary artifact — it defines the complete agent prompt, multi-step workflow, and output specifications.

## Running Scripts

**Salary calculator** (job-market-analyzer):
```bash
python job-market-analyzer/scripts/salary_calculator.py job-market-analyzer/reports/salary_data.json
# or pipe JSON data via stdin
```

**PPT generator** (deep-research-electronics):
```bash
pip install python-pptx
python deep-research-electronics/scripts/generate_ppt.py input.json output.pptx
```

## Skill Development Patterns

- **SKILL.md files** contain the full agent prompt, including step-by-step instructions, data schemas, example inputs/outputs, and error handling. When modifying a skill, keep the workflow steps explicit and numbered.
- **Chinese tech salary data** uses non-standard formatting: `16薪` (16-month salary), `总包` (total comp), `基础薪资` (base). The salary calculator normalizes these into annual figures.
- **Reports are saved** to `reports/{company}_{level}_{date}/` with `stats.json` for structured data and a Markdown file for the human-readable report.
- **Evals** (`evals/evals.json`) define test cases with `input` and `expected_output` fields for verifying skill quality.
- **Design references** (e.g., `references/prompt_zh.md`) contain CSS/layout guidelines in Chinese — consult these when modifying visual output skills.
- The `ai-opportunity-map-generator.skill` file is a packaged/exported version of the skill directory.
