# Contributing

Useful additions often emerge while preparing a return: a missing public
source, support for another document layout, or a clearer interview question.
Capture those improvements so other users can benefit. Contributing is optional
and does not block preparing or completing a filing guide.

## Identify useful changes

At a session pause or after the filing guide is confirmed, inspect the changes
already made for reusable additions and offer to prepare a contribution.
For feedback without a fix, offer to prepare an issue. No separate contribution
log is needed. Keep the offer separate from the interview's next question,
respect a declined offer, and honour an existing request without asking again.

## What belongs in a contribution

| Addition | Include |
| --- | --- |
| Public guidance or reference data | Direct source URL, retrieval date, applicable tax year or explicitly unresolved applicability, retained source, and relevant source-record/index updates. Use the existing downloader where it supports the source; record how to reproduce a new download. |
| New or improved tool | Reusable code under `scripts/`, usage and dependency instructions, supported inputs and limitations, and checks using fictional data. Extend an existing tool when it already owns the task. |
| Workflow or skill improvement | The confusing or missing behaviour, the proposed behaviour, and an everyday fictional example. Update the workflow or skill that owns the instruction. |
| Problem without a fix | An issue describing expected and actual behaviour, steps to reproduce with fictional inputs where relevant, and any public supporting sources. A code change is not required. |

For retained sources, follow [the data-source guide](docs/data-sources.md) and
update its source record plus the relevant local index or summary. Record
retrieval failures and unresolved applicability honestly: downloading a source
does not establish that its rules apply to a particular year or circumstance.
Contribute focused source additions rather than unrelated bulk refreshes.

Installing an external tool alone need not become a contribution. If others
need it to repeat the work, document its purpose, installation, tested version
and usage. Do not commit installed environments or copy third-party code or
data without checking its redistribution terms and preserving required notices.

## Prepare and submit

1. Select one coherent improvement. Inspect the existing changes and include
   only files belonging to that improvement; leave unrelated work alone.
2. Prepare the source, code or documentation and the evidence described above.
   For tool changes, run relevant existing tests and add meaningful checks for
   new behaviour using fictional inputs. For example, a bank-statement converter
   should demonstrate that extracted transaction totals reconcile with a
   fictional statement. For documentation, check links and consistency with
   the existing workflow. Record what was checked and any checks not run.
3. Review the complete proposed change and its attachments for private data.
   Keep taxpayer records, extracted figures, filing guides, session history,
   credentials and identifying filenames out of shared files, issue text,
   screenshots and commit history. Create fictional examples from scratch;
   changing a name on a real statement is not sufficient. See
   [privacy and storage](docs/privacy.md#where-personal-data-should-live).
   Git exclusions help but do not protect files already tracked by Git.
4. Prepare a pull request (PR), a proposed change for the maintainer to review,
   from a contribution branch or fork. Describe the problem, resulting
   behaviour, relevant sources or tax year, verification and limitations.
   For a problem without a fix, prepare an issue instead. Write the public
   description using reusable details and fictional examples, not session notes.
5. Publish only when the collaborator has requested submission. Preparing a
   return does not authorize sending feedback. If
   submission is already authorized, proceed without repeated confirmation.
   If publishing is unavailable, leave the prepared changes and description
   locally and report what remains. After submission, return the issue or PR
   link; submission does not mean the change is accepted.

You can ask your assistant:

> Prepare the new converter and its fictional example as a contribution using
> CONTRIBUTING.md. Show me the changes and proposed pull request description.

Or, when ready to publish:

> Submit the prepared converter contribution as a pull request.
