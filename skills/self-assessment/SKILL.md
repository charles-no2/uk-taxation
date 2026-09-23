---
name: self-assessment
description: >
  Walk an individual through their UK Self Assessment circumstances, records,
  return entries and review, one question at a time. Produce a personalised
  step-by-step filing guide and save progress for later sessions. Use when
  the user says "help me fill in my Self Assessment", "prepare my tax return",
  "resume my Self Assessment", or "make my filing guide". The user submits
  and pays themselves; company and other entity returns are outside this flow.
---

# Self Assessment

Produce a personalised filing guide through an interview in this session.
The user owns figures, claim choices, declaration, submission and payment.

`$ARGUMENTS` is the user's circumstances, year, or saved session path.
Use supplied facts; if empty, begin Circumstances without inventing a profile.

## Sequence

Resolve the project root from the workspace containing `docs/interactive-workflow.md`
and `docs/data-sources.md`; for the repository copy, this is two directories
above the skill. An installed copy must use the workspace, not its installation
folder. If no such workspace is available, ask for its path. Resolve all `docs/`,
`private/` and `CONTRIBUTING.md` paths from that root; skill references remain
relative to this file.
Read `docs/interactive-workflow.md` and `docs/data-sources.md` before the first
interview turn.

Follow Session, then Circumstances through Filing guide in order, revisiting
affected steps when an answer changes. Use the workflow's branch questions
and stage checkpoints; read only the annual sources needed for those branches.

Stop at the confirmed guide; submission, payment and recordkeeping remain user
actions. Follow Filing follow-up only if the user continues after the guide.

## 1. Session

Read [session fields](references/session.md) and follow Save and resume to
create or restore `session.md` in a private session folder.

Ask exactly one main question per turn, introduce it with a short sentence
explaining what the answer determines, offer “I'm not sure”, and save the answer
before asking the next question. Treat workflow question lists as an internal
coverage checklist, not a single prompt. For questions identifying arrangements,
payments, benefits, assets or records, give a few everyday, non-exhaustive
examples; do not imply that an example is automatically taxable or reportable.
Use the user's everyday description first; introduce and explain tax categories
only when relevant. Show progress through relevant sections only; never turn
uncertainty into No, zero or blank.

End each stage with its summary and “Confirm and continue”, “Change an answer”
and “Explain this”. Record confirmation only after the user agrees; allow a
missing item to remain open while an independent section proceeds.

Use session fields' statuses, dependencies and change history after each answer.
Never request login credentials; let users enter identifiers directly in their
filing service and supply verified figures without uploading documents.

## 2. Circumstances

Show the supplied year and exact dates, or 2025–26 provisionally, allowing
changes. Follow workflow step 1's behaviour-based questions individually,
skipping facts already supplied. Start with employer pay when unknown, then
cover other activities and an opportunity to mention anything missed. Do not
show an all-at-once income checklist unless requested. Explain that an activity
alone does not establish tax due or a requirement to file.

Confirm the tax year and exact dates before checking setup requirements.
Use workflow step 1's early readiness check only for prerequisites revealed by
the user's answers: registration or reactivation, filing access, digital-reporting
setup, and records or information that may take time to obtain.

Record each separate job, trade and other income source under a stable name,
such as Job A. Clarify contractor status from working arrangements; distinguish
company receipts from personal income and partnership income from its own return.

Confirm the initial profile, then establish any year details not settled during
the early readiness check, original return or amendment, individual return
ownership, UK residence and relevant regional moves using workflow step 2.
Do not infer residence from nationality or address; mark unresolved residence
treatment needs specialist review.

For an entity return, explain the scope mismatch and return the appropriate
official next route. For another year, verify that year's sources before using
its rules; never relabel the 2025–26 pack.

## 3. Filing plan

Establish the notice-to-file position, reason for filing, previous filing,
registration and access using workflow step 3, using early readiness answers
rather than asking them again. Check the official filing
checker and record its result and reason; a role label does not decide liability
to file, and an existing notice requires resolution with HMRC.

Expand HMRC as HM Revenue & Customs on first use. Verify filing-route support,
registration, filing and payment deadlines, including any individual notice;
record official links, applicable year and check date rather than fixed dates.

Screen for Making Tax Digital for Income Tax, the digital recordkeeping and
reporting process for qualifying individuals; assess its start year separately.

Apply one filing result: Return required, Return may be appropriate for a claim,
Another reporting route may apply, or Need to resolve this first. For another
route, explain and confirm the next action; do not manufacture a return guide
unless an individual return is still appropriate.

Run workflow step 4's completeness check, including reliefs, loans, Child
Benefit, losses and previous payments. Confirm a personalised section list,
repeated sources and conditional pages; use annual criteria for short/full
forms and recheck route support whenever the section list changes.

## 4. Records and sources

During the circumstances and branch interview, establish which records exist
and mark them available or missing; do not ask the user to transcribe figures
from a certificate or statement they have. Finish the applicable fact questions,
including relief and charge discovery, before workflow step 5's single folder
request. Build its checklist only from records that could change an entry or
required check on the established facts; explain each record's purpose.
Ordinary activity inside an Individual Savings Account (ISA) does not by itself
justify requesting statements; require a separate relevant issue and record it.

Ask for one local folder containing the relevant documents, including available
P60 annual pay-and-tax certificates and other applicable records. Keep taxpayer
files private. Do not require uploads: if the user prefers, accept verified
figures during entry preparation instead. Record missing files and continue
independent sections. Extract proposed figures with file/page/line references,
flag unreadable or ambiguous values, and obtain user confirmation; document
availability does not mean its figures are verified.

Search local guidance and legislation first, using `docs/data-sources.md`,
`docs/guidance/INDEX.md`, `docs/rules/INDEX.md` and `docs/self-assessment/INDEX.md`.
Inspect retrieval metadata in `docs/self-assessment/manifest.json` and relevant
source records. Check year and applicability; a download is not a reviewed rule.
Use current official external sources to fill gaps or check time-sensitive
rules, and whenever required to verify tax guidance. Record the year, exact
passage or box, official link and review date.

Whenever a web source supports a conclusion given to the user, retain the exact
official page or file under the relevant `docs/` topic. Record its direct URL,
local path, retrieval date and purpose in `docs/data-sources.md`, and add it to
the relevant local index or summary. Update `docs/interactive-workflow.md` if
it materially changes a question, branch, record, entry or specialist route.
A search snippet or chat citation is not a retained source. If retrieval or
saving fails, record the gap and retry or request the missing access; do not
claim the source is retained.

Treat downloads as source material, not reviewed rules. Establish the selected
section's field definitions, selection criteria, calculation checks and example
basis from applicable annual notes before confirming entries; inspect the
original form when extracted text leaves field layout ambiguous.

Verify online labels against the chosen service's actual wording or official
guidance. Where only a paper box is verified, label it Form reference; do not
present technical mappings or paper ordering as verified online screens.

If a source is missing, inaccessible, conflicting or for another year, record
the affected entry as needs information with the required source check.
If treatment remains unresolved after applicable guidance, use needs specialist
review and name the question to resolve; proceed only with unaffected entries.

## 5. Entries

Repeat workflow step 6's field loop for each applicable field and separate
income source: explain the exact label and period, identify record evidence,
offer a clearly fictional example, propose the evidenced figure from the supplied
records (or collect a user-supplied figure), check it, then
ask the user to confirm the proposed value and treatment.

Include a Why link to the annual notes; explain inclusions, exclusions and
before/after-deduction treatment. Show calculation inputs and working, apply
field-specific currency, rounding, sign, date and blank/zero rules, and keep
fictional values out of the entry register and filing guide.

Use workflow step 6's branch questions before confirming each section; check
for previous-employment totals counted twice and for assets, including crypto,
that may require both income and disposal treatment. Save unknown figures as
needs information, with the record or answer needed next.

Follow workflow step 7 for reliefs, adjustments and charges. Check relief
already given, explain eligibility and effects on other years, and record the
user's choice; unresolved claims remain visible and block affected entries.

## 6. Whole-return review

Follow workflow step 8: compare the profile to completed sources, check missing
sections, duplicates, arithmetic, year allocation, residence, disclosures and
earlier reports/payments. Present each mismatch as an action and return to the
question that resolves it; repeat checks after corrections.

Use provisional figures only if official guidance permits and the user confirms
their basis, disclosure and correction task; keep them marked provisional.

Follow workflow step 9 using a verified calculation or the chosen service's
calculation; identify its source and limitations. Separate return-year tax,
remaining balance and payments on account, advance instalments for a later
tax bill; reconcile payments with the user's account information.

Resolve material calculation differences before marking the review confirmed.
If the service calculates only after entry, leave calculation review pending
and put the comparison in the guide as a required pre-submission check;
never invent a final bill to complete the guide.

## 7. Filing guide

Read [the guide template](assets/filing-guide.md); write `filing-guide.md` in the
session folder with confirmed facts, applicable steps and explicit open items.

Order entries by verified service order, or by official form sections labelled
as form references when screen order is unverified. Give every entry its exact
label, source name, confirmed answer, evidence, reason, official citation and
required disclosure; mark private identifiers Enter directly in the service.

Include tailored transfer and calculation checks, declaration and submission
instructions, confirmation evidence, payments, retention and amendment tasks
from workflow steps 10–12. Verify applicable retention periods and amendment
rules; do not describe these future actions as already completed.

Return Draft — unresolved items while any required answer or treatment remains
open. Return Guide prepared — submission not confirmed when entries and whole-
return checks are confirmed and remaining service checks are explicitly listed;
ask the user to confirm the guide, revising it for corrections or new questions.

## 8. Filing follow-up

If the user continues, follow workflow steps 10–12 to reconcile transferred
entries and calculations, clarify unfamiliar questions and record user-reported
submission evidence. Preserve submitted versions before amendments, rerun
affected checks and track payment separately using session fields.

## Contribution checkpoint

At a session pause or after guide confirmation, inspect existing changes for
useful public sources, reusable tools or workflow improvements. Offer to prepare
a pull request for useful changes, or an issue for feedback without a fix.
Read the workspace's `CONTRIBUTING.md` when preparing a contribution; no separate
contribution log is needed. Keep the offer separate from the next interview
question, respect a declined offer, and honour an existing request without
asking again. Contributing is optional and never blocks the filing guide.

Before sharing, sanity-check the complete contribution: selected files and
changes, commits to be published, examples, filenames, attachments, and issue or
pull request text. Exclude all user private details, including names, addresses,
tax and account identifiers, actual financial figures, records, session content
and credentials. Use fictional examples created from scratch. Do not rely on
Git exclusions or a name replacement to make content safe. Remove private
material from the proposed contribution and recheck; if anything cannot be
verified safe to share, leave it out. Publish only when submission is requested.

## Return

- Guide: path and status, or the confirmed alternative reporting route.
- Session: saved path, year, filing route and next unanswered question.
- Open items: missing evidence, source checks or specialist questions.
- User actions: transfer checks, submission, payment and recordkeeping tasks.

Done when the user confirms the guide and its remaining filing actions.
A draft is a checkpoint; resume when the required answer becomes available.

## When not to use

- Company, partnership entity, trustee or executor returns: identify the
  appropriate official route and explain the individual-return boundary.
- General tax research without preparing a return: answer the specific question.
- Automatic submission, accepting a declaration or paying tax for the user.
