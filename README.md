# UK taxation and Self Assessment

A workspace for preparing an individual's UK Self Assessment return with an AI
assistant. It combines a guided interview, saved public tax references and local
tools for preparing financial records. You review the figures, choose any claims,
and submit and pay through your filing service yourself.

## What this repo does

- **Guided preparation:** the [self-assessment skill](skills/self-assessment/SKILL.md)
  asks one main question at a time, identifies relevant records and return
  sections, proposes entries for your confirmation, and produces a personalised
  `filing-guide.md` with evidence, sources and outstanding questions.
- **Save and resume:** progress is saved in a private `session.md`, including
  confirmed answers, missing information and the next question.
- **Tax reference library:** local copies of HM Revenue & Customs (HMRC)
  guidance, UK legislation, forms, notes and helpsheets, with indexes and
  retrieval records. The initial annual pack covers **2025–26
  (6 April 2025 to 5 April 2026)**.
- **Local document tools:** convert supported bank statements, pay-and-tax
  certificates and benefit forms from PDF documents into CSV (comma-separated
  values) files. A separate downloader retrieves HMRC monthly exchange rates.

This is a skill and reference workspace, not a standalone filing application or
a verified tax calculation engine. Downloaded sources still need checking for
the relevant year and circumstances. The skill covers individual returns;
company, partnership entity, trustee and executor returns are outside its scope.
Unresolved figures or treatment remain visible in the guide.

### As of date and source freshness

**As of 21 September 2026**, the repository has the following saved source
collections. This README's review date is not a claim that every source was
downloaded or every tax rule verified that day.

| Material | Recorded date / where to check |
| --- | --- |
| Privacy and skill-installation guidance in this README | Checked 21 September 2026 against provider documentation; Codex deletion commands checked against local version 0.155.1. |
| 2025–26 Self Assessment source pack | Download run finished 18 September 2026; see the [source manifest](docs/self-assessment/manifest.json). |
| Legislation collection | Downloaded 18 September 2026; see the [fetch record](docs/rules/FETCHED_AT.md), including its supplemental download. |
| Public tax explainers | Snapshot dated 19 September 2026; see the [snapshot index](docs/tax-explainers/20260919T080223011317Z/INDEX.md). |
| HMRC manuals | Check each manual's `manifest.json` and individual page retrieval dates, starting from the [guidance index](docs/guidance/INDEX.md). Dates and gaps vary by source. |
| Exchange-rate exports | Fetched when you run the downloader; each output row records its retrieval time and rate validity dates. See the [exchange-rate guide](docs/exchange-rates.md). |

A retrieval date says when a document was saved, not which tax year its rules
apply to. Refreshes are manual; follow [Data sources](docs/data-sources.md) and
update this table when refreshing the collections.

## Privacy and security — read before installation

Tax records can contain names, addresses, account numbers and detailed financial
history. Configure your assistant before sharing any of them. **A file stored
locally can still be sent to an AI provider when an assistant reads it or receives
its contents through a tool.** Running a local editor does not make its AI features
offline.

### Privacy disclaimer

The repository author does not seek to obtain your personal information. The
skill is not designed to collect personal information for the author or send it
to them; it asks for tax-related facts and records only to help prepare your
return, and saves your progress in your local workspace.

**This does not guarantee that the AI agent running the skill will not request,
access, transmit or retain personal information.** The author cannot control or
guarantee the behaviour of your chosen agent, its provider or connected tools.
Before using this skill, read the privacy policy and data-handling terms of
each agent and service you enable, including how they use data for training,
how long they retain it and how you can delete it. Review their permissions
and privacy settings, and share only information you are comfortable having
processed under those terms. The skill's instructions are not a privacy or
security guarantee.

### Turn off use of your data for model training

**As of 21 September 2026**, the linked official documentation describes the
controls below. Check the account and product you actually use; names and
policies can change.

| Provider / product | Setting to check |
| --- | --- |
| **OpenAI — ChatGPT and personal-plan Codex** | In ChatGPT, open **Settings → Data Controls** and turn off **Improve the model for everyone**. This applies to new ChatGPT conversations and Codex tasks. Also disable any separate permission for training on **full environments** in Codex Settings; the ChatGPT switch does not change that setting. See [OpenAI data controls](https://help.openai.com/en/articles/7730893-data-controls-faq). |
| **Anthropic — Claude and consumer-plan Claude Code** | Open **Settings → Privacy** and turn off **Help Improve our AI models**. This covers chats and coding sessions on the relevant consumer account. See [Anthropic model improvement settings](https://privacy.claude.com/en/articles/12109829-how-do-i-change-my-model-improvement-privacy-settings). |
| **xAI — Grok** | On grok.com, open **Settings → Data** and turn off **Improve the Model**; the mobile app uses **Settings → Data Controls**. Grok within X has separate controls: follow [X's Grok guidance](https://help.x.com/en/using-x/about-grok). See [Grok data controls](https://x.ai/legal/faq). |
| **Cursor** | Enable **Privacy Mode** in Cursor settings. Cursor states that this prevents training on customer data by Cursor and its model providers, subject to documented exceptions for abuse investigations and separately designated models. Requests still pass through Cursor's servers, including when using your own provider key. See [Cursor data use](https://cursor.com/data-use). |

**Opting out of training does not mean no transmission, no storage or immediate
deletion.** Safety, legal and feedback exceptions can apply; avoid submitting
sensitive conversations as feedback. Business plans and application programming
interfaces (APIs) have their own terms—check those separately. An opt-out also
does not undo training that has already happened. Review the linked policies,
including [Anthropic's retention guidance](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data).

### Where personal data should live

Keep original documents in a dedicated folder on an encrypted local drive, outside
the repository if possible. Use a folder that is not automatically shared or
synced to a cloud service. Give the assistant access only to the records needed
for the current task; you can instead supply verified figures without giving it
the documents. Never provide login passwords, recovery codes or access keys.
Enter tax identifiers directly in the filing service.

Within this workspace, use the existing private locations:

| Location | Contents |
| --- | --- |
| `private/self-assessment/<session>/` | Saved answers in `session.md`, the personalised `filing-guide.md`, calculations and supporting notes. The skill creates a unique dated folder. |
| `private/pdfs/` | Optional working copies of source documents, if you choose to keep them in the workspace. |
| `private/` | Other sensitive working files, including mappings back to original filenames. |
| `exports/` | Converted financial data and reports. Treat these as personal data too. |
| `docs/`, `skills/`, `scripts/` | Shared reference material and code only; never put taxpayer facts here. |

The repository's [`.gitignore`](.gitignore) excludes `private/`, `exports/`, CSV
and tab-separated files. This helps prevent accidental commits; it is **not
encryption or an access restriction**. It cannot protect files already tracked
by Git or prevent an assistant from reading ignored files. Avoid force-adding
private files and inspect changes before committing or publishing.

The PDF converters run locally without an external extraction service. For
sensitive originals, run them yourself in a terminal, then review the output
before sharing selected figures. The batch converter reduces identifying
details, but dates, amounts and merchant names can still reveal personal
information. The older single-file converter preserves transaction descriptions.
See the [batch conversion guide](docs/tax-pdf-batch-conversion.md).

### Housekeeping: delete a local session and its copies

First preserve any records you still need in secure storage. Check the applicable
[HMRC recordkeeping guidance](https://www.gov.uk/self-assessment-tax-returns/keeping-records)
before discarding evidence needed for your return. Then:

1. **Stop the assistant session** so it cannot recreate files during cleanup.
2. **Delete the saved tax session.** In your file manager, open
   `private/self-assessment/`, select the exact dated session folder, and delete
   it. This removes its saved answers, guide and any other files inside it.
   Empty the trash when you are sure you no longer need them. Deleting only the
   guide leaves the personal answers in `session.md`.
3. **Delete related working copies.** Review `private/`, `exports/`, the original
   input folder and any temporary folders for that session's PDFs, converted
   tables, filename mappings, screenshots and downloads. Delete only the copies
   you no longer need; files outside the session folder survive step 2.
4. **Delete the assistant conversation separately.** Use your client's conversation
   deletion controls. Clearing the screen, starting a new chat or archiving a
   conversation is not deletion. Also review saved memories and project notes
   for copied facts.
5. **Review other copies.** Check terminal scrollback and saved command history,
   editor history, clipboard history, cloud sync, backups and shared conversation
   links. Local deletion does not remove provider-held copies; use the provider's
   deletion controls or privacy request process too.

For **Codex command-line sessions**, `codex-cli 0.155.1` provides the following
commands (checked using its local help). Run them from a separate terminal after
ending the target session:

```sh
codex delete --help
codex delete 'YOUR-SESSION-ID'
```

Replace the placeholder with the exact assistant session ID, not the tax folder
name. Review the confirmation prompt. If your version does not have `delete`,
consult that version's session-management documentation; do not blindly remove
the entire assistant configuration directory. This command deletes a saved
Codex session; it does not replace the file cleanup above or a provider-side
deletion request.

Ordinary deletion does not guarantee recovery is impossible, especially where
backups or drive snapshots exist. Use encrypted storage from the outset and
manage backup retention deliberately. This repo has no automatic cleanup command.

## Installation

A **skill** is a folder of instructions and supporting files that an AI assistant
loads for a task. Install the complete `self-assessment` folder, including its
`references/` and `assets/`, rather than copying only `SKILL.md`.

### 1. Clone the workspace

You need Git and a local AI assistant that supports skills and can read this
workspace. The examples below use a macOS or Linux shell.

```sh
git clone https://github.com/charles-no2/uk-taxation.git
cd uk-taxation
```

Keep the clone: the installed skill needs the repository's `docs/` and scripts.
Review [the skill instructions](skills/self-assessment/SKILL.md) before enabling it.

### 2. Install the skill for your assistant

Run **one** of these from the repository root. If a `self-assessment` installation
already exists, inspect it and back up any customisations before replacing it.
The commands below skip copying when that destination already exists.

**Codex — personal installation:**

```sh
mkdir -p "$HOME/.agents/skills"
if [ ! -e "$HOME/.agents/skills/self-assessment" ]; then
  cp -R skills/self-assessment "$HOME/.agents/skills/self-assessment"
fi
```

Codex's current documented personal skill location is `~/.agents/skills/`.
See [Codex skill discovery](https://developers.openai.com/codex/skills/).

**Claude Code — personal installation:**

```sh
mkdir -p "$HOME/.claude/skills"
if [ ! -e "$HOME/.claude/skills/self-assessment" ]; then
  cp -R skills/self-assessment "$HOME/.claude/skills/self-assessment"
fi
```

See [Claude Code skills](https://code.claude.com/docs/en/skills). For other clients,
use their documented local skill installation mechanism; privacy guidance above
does not imply that every listed product supports this workflow.

Open or restart your assistant in the cloned repository and confirm that
`self-assessment` is available. Installed copies do not update automatically when
you update the repository; review and replace the copied folder when needed.

### 3. Start or resume

Ask your assistant:

> Use the self-assessment skill to help me prepare my 2025–26 Self Assessment.

The skill asks about your circumstances, confirms relevant sections, gathers
records and checks entries with you. It saves progress after each answer and
reports the private session path. To continue later, supply that path:

> Resume my Self Assessment from private/self-assessment/MY-SESSION/session.md.

The final guide records remaining actions; approval of the guide does not mean
your return has been submitted or your tax paid.

### 4. Optional document-conversion setup

For the Python tools, use Python 3.10 or newer. Create a separate dependency
environment for PDF conversion:

```sh
python3 -m venv .venv-bank
.venv-bank/bin/python -m pip install -r scripts/bank-pdf-requirements.txt
```

Follow the [batch conversion guide](docs/tax-pdf-batch-conversion.md) for supported
layouts and commands. The [exchange-rate downloader](docs/exchange-rates.md)
uses Python's standard library; its monthly customs reference rates are not
automatically the appropriate conversion method for every tax entry.

## Reference and maintenance guides

- [Walkthrough design](docs/interactive-workflow.md): interview stages and checks.
- [Data sources](docs/data-sources.md): source coverage, known gaps and refresh commands.
- [Annual Self Assessment index](docs/self-assessment/INDEX.md): forms and supporting material.
- [HMRC guidance](docs/guidance/INDEX.md) and [legislation](docs/rules/INDEX.md): local source indexes.
- [PDF batch conversion](docs/tax-pdf-batch-conversion.md) and [exchange rates](docs/exchange-rates.md): utility usage, limitations and tests.

Saved publications are snapshots. Check retrieval records and applicable tax
years, and verify time-sensitive rules against current official sources before
relying on an entry.
