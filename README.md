# UK taxation and Self Assessment

Prepare an individual's UK Self Assessment return with an AI assistant. The
[self-assessment skill](skills/self-assessment/SKILL.md) asks one question at a
time, saves progress and produces a personalised filing guide for your review.
**You check the figures, choose claims, submit the return and pay yourself.**

The repo includes saved HM Revenue & Customs (HMRC) guidance, legislation and
forms, plus local tools for converting supported financial documents and fetching
exchange rates. It is not a standalone filing app or a verified tax calculator;
company and other entity returns are outside the skill's scope.

**As of 21 September 2026:** setup and privacy guidance have been checked. The
annual pack covers **2025–26 (6 April 2025–5 April 2026)**, downloaded on
18 September; legislation was fetched on 18 September and public tax explainers
on 19 September. Other sources have individual retrieval dates. Downloads do not
establish that rules apply to your circumstances; see [source freshness](docs/privacy.md#source-freshness).

## Privacy and security — before installation

The author does not seek your personal information, and the skill is not designed
to collect it for the author. **The author cannot guarantee that your AI agent
will not access, transmit or retain personal data.** Local files can reach the
provider when an agent reads them. Read your agent's privacy policy and review
its permissions before use.

- **Disable model training:** OpenAI — turn off *Improve the model for everyone*
  or request *Do not train on my content* through its Privacy Portal; separately
  check Codex full-environment training. Anthropic — turn off *Help Improve our
  AI models*. Grok — turn off *Improve the Model* (X has separate controls).
  Cursor — enable *Privacy Mode*. These settings do not guarantee no retention.
  [Settings, exceptions and official links](docs/privacy.md#turn-off-use-of-your-data-for-model-training).
- **Keep records private:** use encrypted local storage, preferably outside the
  repo. The skill requires `private/self-assessment/` for saved sessions;
  `private/pdfs/` and `exports/` are optional conventions. Those example folders
  are excluded from Git, but that does not restrict agent access. Add exclusions
  for alternative locations inside the repo. Never share login credentials.
- **Clean up afterwards:** preserve required tax evidence, then delete unwanted
  session files, working copies and the agent conversation separately. Check
  memories, backups and provider-held copies too. Deleting a skill or archiving
  a chat does not erase the conversation.
  [Storage paths and deletion steps](docs/privacy.md#housekeeping-delete-a-local-session-and-its-copies).

## Installation

You need Git and a local assistant that supports **skills**—folders of task
instructions and supporting files. These commands use a macOS or Linux shell.

```sh
git clone https://github.com/charles-no2/uk-taxation.git
cd uk-taxation
```

Review [the skill](skills/self-assessment/SKILL.md), then run **one** installation
below. Both copy its complete folder and skip an existing installation; inspect
and back up customisations before replacing one.

**Codex** ([skill locations](https://developers.openai.com/codex/skills/)):

```sh
mkdir -p "$HOME/.agents/skills"
if [ ! -e "$HOME/.agents/skills/self-assessment" ]; then
  cp -R skills/self-assessment "$HOME/.agents/skills/self-assessment"
fi
```

**Claude Code** ([skill locations](https://code.claude.com/docs/en/skills)):

```sh
mkdir -p "$HOME/.claude/skills"
if [ ! -e "$HOME/.claude/skills/self-assessment" ]; then
  cp -R skills/self-assessment "$HOME/.claude/skills/self-assessment"
fi
```

Keep the clone: the skill needs its reference documents. Open or restart your
assistant **in this repository**, confirm the skill is available, then ask:

> Use the self-assessment skill to help me prepare my 2025–26 Self Assessment.

Progress is saved after each answer. To resume, provide the saved path:

> Resume my Self Assessment from private/self-assessment/MY-SESSION/session.md.

Installed copies do not update automatically; review and replace them when you
update the repo. Other clients need their own supported installation mechanism.

## Tools and reference guides

- [PDF conversion](docs/tax-pdf-batch-conversion.md): local extraction, supported
  layouts, dependency installation and checks. Requires Python 3.10 or newer;
  review output before sharing—it is not guaranteed anonymous.
- [Exchange rates](docs/exchange-rates.md): downloader usage and limitations.
- [Data sources](docs/data-sources.md): coverage, known gaps and manual refresh commands.
- [Walkthrough design](docs/interactive-workflow.md): interview stages and checks.
- [Privacy guide](docs/privacy.md): provider settings, storage locations and cleanup.

## Contributing

Found missing public guidance, added a useful tool, or spotted a confusing
interview question? See [the contribution guide](CONTRIBUTING.md) for what to
include and how to prepare an issue or pull request. The Self Assessment skill
reviews existing changes at a natural checkpoint and offers to prepare a
contribution, checking for private details before sharing. Sharing is optional;
personal records and session files stay private.
