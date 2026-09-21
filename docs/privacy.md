# Privacy, storage and cleanup

[Back to the README](../README.md). Guidance checked as of **21 September 2026**.


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

For **OpenAI**, you can also submit a **Do not train on my content** request
through the [OpenAI Privacy Portal](https://privacy.openai.com/). Complete the
portal's verification steps and keep any confirmation privately. As of
**21 September 2026**, OpenAI describes this as an alternative way to opt out:
the request is reflected in your account's data settings, rather than being an
additional required opt-out on top of the ChatGPT switch. Check that the setting
is off on the account you use. Neither route changes the separate Codex
full-environment training setting, which you must check independently. See
[OpenAI's explanation](https://help.openai.com/en/articles/7730893-data-controls-faq).

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

The current skill requires saved sessions under `private/self-assessment/`.
The other private paths below are conventions used in this repository's examples,
not required layouts. You can organise source documents and exports elsewhere
and pass those paths to the tools. If you choose another location inside the
repository, add appropriate Git exclusions before storing personal data there.

| Location | Contents |
| --- | --- |
| `private/self-assessment/<session>/` | Required by the current skill for saved answers in `session.md`, the personalised `filing-guide.md`, calculations and supporting notes. The skill creates a unique dated folder. |
| `private/pdfs/` | Suggested location for optional working copies of source documents, if you choose to keep them in the workspace. |
| `private/` | Suggested location for other sensitive working files, including mappings back to original filenames. |
| `exports/` | Suggested location for converted financial data and reports. Treat these as personal data too. |
| `docs/`, `skills/`, `scripts/` | Shared reference material and code only; never put taxpayer facts here. |

The repository's [`.gitignore`](../.gitignore) excludes `private/`, `exports/`, CSV
and tab-separated files. This helps prevent accidental commits; it is **not
encryption or an access restriction**. It cannot protect files already tracked
by Git or prevent an assistant from reading ignored files. Avoid force-adding
private files and inspect changes before committing or publishing.

The PDF converters run locally without an external extraction service. For
sensitive originals, run them yourself in a terminal, then review the output
before sharing selected figures. The batch converter reduces identifying
details, but dates, amounts and merchant names can still reveal personal
information. The older single-file converter preserves transaction descriptions.
See the [batch conversion guide](tax-pdf-batch-conversion.md).

### Housekeeping: delete a local session and its copies

**As of 21 September 2026**, these are useful places to check for assistant
data. `~` means your operating-system user's home directory. These are defaults,
not a complete inventory: versions, custom configuration, remote machines and
cloud sessions can store data elsewhere.

| Client / location | What to check |
| --- | --- |
| `~/.agents/skills/` | Installed skill instructions, including this skill when installed using the README instructions. This is not Codex's conversation store. Removing the skill does not delete conversations. See [Codex skills](https://developers.openai.com/codex/skills/). |
| Codex: `~/.codex/` | Local state, history, logs and caches. `CODEX_HOME`, an environment variable that selects Codex's data directory, can change this location. `history.jsonl` can contain saved prompt history; session storage details vary by version. Prefer the session deletion command below over deleting individual database files. See [Codex state locations](https://developers.openai.com/codex/config-advanced/). |
| Claude Code: `~/.claude/` | `projects/<project>/` contains transcripts and `memory/` notes; `history.jsonl` contains prompt history. Also check `file-history/`, `paste-cache/`, `uploads/` and `debug/` for copies. `CLAUDE_CONFIG_DIR` can relocate this directory. The `skills/` folder contains installed instructions, not the conversation history. See [Claude Code application data and cleanup](https://code.claude.com/docs/en/claude-directory#application-data). |
| Grok Build command-line client: `~/.grok/` | Local session history and configuration. This path applies to Grok Build, not automatically to Grok in a browser, on X or in the mobile app. See [Grok Build data lifecycle](https://docs.x.ai/build/enterprise#data-lifecycle). |
| Cursor and browser/mobile clients | Use the product's conversation-management controls and check its current documentation for local application data. Do not assume all data lives in a similarly named home-directory folder. For Grok web/mobile deletion, see [Grok data controls](https://x.ai/legal/faq). |

**Do not delete these entire directories as a routine cleanup step.** They can
also contain credentials, settings, installed skills and unrelated projects.
Identify the specific project or session first. Deleting a transcript may leave
prompt history, memories, file snapshots and provider-held copies behind.

First preserve any records you still need in secure storage. Check the applicable
[HMRC recordkeeping guidance](https://www.gov.uk/self-assessment-tax-returns/keeping-records)
before discarding evidence needed for your return. Then:

1. **Stop the assistant session** so it cannot recreate files during cleanup.
2. **Delete the saved tax session.** In your file manager, open
   `private/self-assessment/`, select the exact dated session folder, and delete
   it. This removes its saved answers, guide and any other files inside it.
   Empty the trash when you are sure you no longer need them. Deleting only the
   guide leaves the personal answers in `session.md`.
3. **Delete related working copies.** Review your chosen storage locations
   (such as `private/` and `exports/`), the original
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

## Source freshness

**As of 21 September 2026**, the repository has the following saved source
collections. The documentation review date is not a claim that every source was
downloaded or every tax rule verified that day.

| Material | Recorded date / where to check |
| --- | --- |
| Privacy and skill-installation guidance | Checked 21 September 2026 against provider documentation; Codex deletion commands checked against local version 0.155.1. |
| 2025–26 Self Assessment source pack | Download run finished 18 September 2026; see the [source manifest](self-assessment/manifest.json). |
| Legislation collection | Downloaded 18 September 2026; see the [fetch record](rules/FETCHED_AT.md), including its supplemental download. |
| Public tax explainers | Snapshot dated 19 September 2026; see the [snapshot index](tax-explainers/20260919T080223011317Z/INDEX.md). |
| HMRC manuals | Check each manual's `manifest.json` and individual page retrieval dates, starting from the [guidance index](guidance/INDEX.md). Dates and gaps vary by source. |
| Exchange-rate exports | Fetched when you run the downloader; each output row records its retrieval time and rate validity dates. See the [exchange-rate guide](exchange-rates.md). |

A retrieval date says when a document was saved, not which tax year its rules
apply to. Refreshes are manual; follow [Data sources](data-sources.md) and
update this table when refreshing the collections.
