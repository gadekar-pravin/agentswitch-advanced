# First task plan: duplicate-party and duplicate-item report

Due 15 Nov 2026. Written 3 Nov, revised after review the same day.

## What we deliver

A read-only command that scans parties and items on one system and writes a report: one JSON file (the record of
truth) and a Markdown page made from it, both under `local/`, which is git-ignored because the report holds real
party data. Each proposal pairs two records, gives a confidence with the evidence behind it, suggests which record
survives, and lists what differs. Nothing on the platform changes and no record is created.

Keystone only until the Suryodaya login works. The report says which system it covers.

**Handed over on 15 Nov:** the merged pull request (code, tests, this plan), a summary with counts only in the pull
request description (rows read, proposals per band, exclusions per reason, no record data), and the full report
sent to the seat lead directly, not through the repository.

## Decisions

| Question | Decision | Why |
|---|---|---|
| Where proposals live | Local JSON plus Markdown. No platform records for 15 Nov. | Creating a shared record needs the person's approval each time, and we do not yet know what the Eval Harness seat will check. If they need a record, add an opt-in publish step later and leave the report as it is. |
| How matches are found | Rules only: normalize, group by shared keys, score. No model. | The same data always gives the same result, it costs no tokens, it works offline, and a verifier can recompute it. A model is worth adding later only if the review shows the rules miss real duplicates. |
| What confidence means | A score from 0 to 1 with the signals that produced it, and one band. **Propose:** 0.9 or more, with no conflict and no cap. **Review:** 0.6 to below 0.9, or 0.9 or more with a conflict or a cap (a conflict between strong values, or a customer-versus-vendor twin). **Dropped:** below 0.6, whatever the conflicts; counted in the report, not listed. | It is a rule score, not a probability, and the report says so. The review with the seat lead gives how many in each band were right. |
| Pairs or groups | Pairs. A record in two proposals is flagged so both are reviewed together. | A matches B and B matches C does not mean A matches C. |
| Pair identity | Party or item, plus the two record ids, sorted. The report is sorted by band, then pair id, so two runs on the same data write the same file. | Review labels must still apply after the weights are tuned. |
| Survivor | Suggested, never decided: more references, then older, then more fields filled, then the smaller id. If either side's reference count is unknown, the reference step is skipped and the report says so. | A person makes the call. The rule is printed so they can overrule it. |
| How a person acts | They mark each pair accepted or rejected in a labels file in `local/` that the command reads but never writes. Labels are shown beside each pair and never change its score, band or survivor. Accepting records intent only. Any change to a record is made by a person, through the platform, with approval. | There is no merge tool, and the agent never changes a record. |
| Write guard | Lands first, before any party or item read. `McpClient.call` loads the tool list once and allows a tool only when it is on that list and marked both read-only and non-destructive. Every other tool is refused before anything is sent. Retries follow the same decision instead of the tool's name. | The login can see update tools for parties and items, and they are not marked destructive. Making the client refuse them is safer than relying on care. |

## Signals

An empty value never counts as a match, and neither does a placeholder such as "N/A" or a dummy phone number shared
by many records. A conflict between two filled strong values caps the pair at review.

- **Parties.** Strong: the same customer code, the same email, the same phone (at least 10 digits). Weaker: the same
  name after normalizing (case, spacing, punctuation, legal endings such as Pvt Ltd or Corporation), the same website.
- **Items.** Strong: the same SKU or code. Weaker: the same name after normalizing, the same category and unit of
  measure (not weight unit).
- **Only if the list rows include them** (checked in step 3): address city and postcode for parties, and variants for
  items. Otherwise these are left out and the report says so, rather than fetching each record one by one.

## Never proposed

These are listed in their own section of the report, with the reason, and never become a proposal.

- Either party is flagged as an allowed duplicate.
- Either party's privacy state is anything other than the ordinary one. These are counted, and their details are
  left out of the report. Which states exist is noted in `local/` at step 3, not here.
- Both records name a company and the companies differ. A missing company proves nothing either way.
- An individual and an organisation.
- Items of different kinds or different units of measure. If variant data is in the list rows, also variants of one
  item.

Customer-versus-vendor twins stay in **review** at most. A person decides whether one party should hold both roles.

## Reference counts

For proposed pairs only, count the records that point at each side: orders, payments, ledger entries, leads,
deals and relationships for parties (every link to the party, from either side), and stock movements for items. A
count that could not be read is **unknown**, never zero. If step 3 shows that a filter narrows the rows but not the
reported total, the rows are counted. If a filter does not narrow the rows, reference counts are left out and the
survivor rule starts at age. Either way, matching goes ahead. This is the first thing cut if hours run short.

## Build order (about 25 hours)

| # | Step | Hours | Needs |
|---|---|---|---|
| 1 | Write guard, with offline tests: an update refused, a delete refused, a list allowed, an unknown tool refused | 2 | none |
| 2 | Ask the Eval Harness seat what they will check. Ask the person for one approval covering the full party and item reads on Keystone, the reference reads, keeping the data in `local/` (including parties under privacy restrictions, which never reach the report), and reruns while tuning. | 0.5 | messages |
| 3 | Keystone read: counts, page both tables into `local/`, check whether a filter narrows the rows returned and whether it narrows the reported total (if only the rows, count the rows), check which child rows the list includes, see what duplicates look like | 2 | approval |
| 4 | `data_steward/dedupe.py`: normalize, group, score, exclusions. Tests on hand-made pairs, plus a small made-up dataset with known duplicates and known non-duplicates run from grouping to report, so a duplicate the grouping never finds shows up as a miss. Can start before step 3. | 7 | none |
| 5 | Proposals: survivor suggestion, field differences, reference counts | 4 | step 3 |
| 6 | JSON and Markdown report and the `python -m data_steward.dedupe` command. Under the harness runner the instance comes from the runner. The report states rows read, whether any table was cut off, and that an incomplete scan does not mean there are no duplicates. | 3 | step 4 |
| 7 | One person with the seat lead: run on Keystone, label 20 to 30 pairs, tune the weights, then check the result on pairs held back from tuning and report wrong proposals and known misses | 3 | step 6 |
| 8 | README and AGENTS.md updates, pull request, review | 2 | step 7 |
| | Buffer | 1.5 | |

**Not for 15 Nov:** a model in the loop, Suryodaya (until the login works), platform records, merges, missing-field
and orphan checks, and the 12-task suite (30 Nov).

## Checks that could change this plan

- **The Keystone read.** If a party or item table has more than 5000 rows, full-table matching needs a new approach:
  re-plan before step 4 is finished. A filter that does not work only affects reference counts, as described under Reference counts.
- **The Eval Harness seat's answer.** If their check needs a platform record per proposal, add an opt-in publish
  step that needs the person's OK each run.
