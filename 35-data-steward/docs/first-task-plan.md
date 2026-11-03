# First task plan: duplicate-party and duplicate-item report

Due 15 Nov 2026. Written 3 Nov, revised after review the same day, amended after the Keystone read (step 3), and
brought up to date after steps 5 and 6 and the Suryodaya read the same day.

## What we deliver

A read-only command that scans parties and items on one system and writes a report: one JSON file (the record of
truth) and a Markdown page made from it, both under `local/`, which is git-ignored because the report holds real
party data. Each proposal pairs two records, gives a confidence with the evidence behind it, suggests which record
survives, and lists what differs. Nothing on the platform changes and no record is created.

It runs on either system, one per run; both have been read. The report says which system it covers.

**Handed over on 15 Nov:** the merged pull request (code, tests, this plan), a summary with counts only in the pull
request description (rows read, proposals per band, exclusions per reason, no record data), and the full report
sent to the seat lead directly, not through the repository.

## What the Keystone read showed

- Both tables are small, far under the 5000-row limit, and were read whole.
- Addresses and roles come back inside each party row, so they can be used without fetching records one by one.
  Item variants are always empty there.
- Every reference filter narrows both the rows and the reported total, so a reference count is a small read.
- There are almost no natural duplicates. The duplicates that exist are another team's test records, created again
  on each of their test runs, with nothing in common but a name and, mostly, a role. A shared bracketed test tag at the start
  of their names also makes different test records look alike.

The Suryodaya read (3 Nov) showed the same: both tables small and read whole, every reference filter narrowing rows
and total, no shared email, phone or code, and nothing proposed. A few same-name parties with different emails sit
in review. Its items do carry SKUs and variants, which Keystone's do not.

So live data cannot tune or check the matcher. Made-up data does that instead: a tuning set and a separately written held-back set (steps 4, 4b and 7).

## Decisions

| Question | Decision | Why |
|---|---|---|
| Where proposals live | Local JSON plus Markdown. No platform records for 15 Nov. | Creating a shared record needs the person's approval each time, and we do not yet know what the Eval Harness seat will check. If they need a record, add an opt-in publish step later and leave the report as it is. |
| How matches are found | Rules only: normalize, group by shared keys, score. No model. | The same data always gives the same result, it costs no tokens, it works offline, and a verifier can recompute it. A model is worth adding later only if the checks show the rules miss real duplicates. |
| What confidence means | A score from 0 to 1 with the signals that produced it, and one band. **Propose:** 0.9 or more, with no conflict and no cap. **Review:** 0.6 to below 0.9, or 0.9 or more with a conflict or a cap (a conflict between strong values, a role difference, or party names that are only near). **Dropped:** below 0.6, whatever the conflicts; counted in the report, not listed. | It is a rule score, not a probability, and the report says so. The held-back set of made-up data gives how many in each band were right (step 7). Those figures come from made-up data that holds many duplicates, so the report says they do not predict how often a live proposal is right. A band with no checked examples is reported as unchecked. |
| Pairs or groups | Pairs. A record in two proposals is flagged so both are reviewed together. | A matches B and B matches C does not mean A matches C. |
| Pair identity | Party or item, plus the two record ids, sorted. The report is sorted by band, then pair id, so two runs on the same data write the same file. | Review labels must still apply after the weights are tuned. |
| Survivor | Suggested, never decided: more references, then older, then more fields filled, then the smaller id. If either side's reference count is unknown, the reference step is skipped and the report says so. | A person makes the call. The rule is printed so they can overrule it. |
| How a person acts | They mark each pair accepted or rejected in a labels file in `local/` that the command reads but never writes. Labels are shown beside each pair and never change its score, band or survivor. Accepting records intent only. Any change to a record is made by a person, through the platform, with approval. | There is no merge tool, and the agent never changes a record. |
| Write guard | Done (step 1). `McpClient.call` loads the tool list once and allows a tool only when it is on that list and marked both read-only and non-destructive. Every other tool is refused before anything is sent. Retries follow the same decision instead of the tool's name. | The login can see update tools for parties and items, and they are not marked destructive. Making the client refuse them is safer than relying on care. |

## Signals

An empty value never counts as a match, and neither does a placeholder such as "N/A" or a dummy phone number shared
by many records. A conflict between two filled strong values caps the pair at review.

- **Parties.** Strong: the same customer code, the same email, the same phone (at least 10 digits). Weaker: the same
  name after normalizing (case, spacing, punctuation, legal endings such as Pvt Ltd or Corporation), the same website,
  the same address city and postcode.
- **Near names.** Two normalized names with a similarity of 0.9 or more (about a letter or two apart) count as much
  as the same name, so a duplicate that differs only by a typo reaches review, once the two records meet in grouping
  (a shared word of three letters or more, or a shared key: a typo in a one-word name with nothing else shared is
  never compared). A party pair whose names are only near is held at review, because two people a letter apart can
  share a household email or phone, unless the two share a customer code, which belongs to one customer.
- **Items.** Strong: the same SKU or code. Weaker: the same name after normalizing, the same category and unit of
  measure (not weight unit).
- **Test tags.** Only the test-run tags found in the read, listed in `local/`, are removed from the start of a name
  before names are compared, so a shared tag adds nothing to the score. Any other bracketed prefix is part of the
  name and is kept. Tags never exclude a pair or keep it out of grouping, and the report keeps the original names. A
  pair where either name carried a test tag keeps its score and band but is shown under its own heading, and is left
  out of the band totals in the pull request summary. The report says where the tag came from (on Keystone, another
  team's test runs) only as far as the read showed it.

## Never proposed

These are listed in their own section of the report, with the reason, and never become a proposal.

- Either party is flagged as an allowed duplicate.
- Either party's privacy state is anything other than the ordinary one. These are counted, and their details are
  left out of the report. Which states exist is noted in `local/`, not here.
- Both records name a company and the companies differ. A missing company proves nothing either way.
- An individual and an organisation.
- Items of different kinds or different units of measure. When an item lists variants, also variants of one item.

Parties whose active roles differ (for example a customer and a supplier, or an employee and a customer) stay in
**review** at most. A person decides whether one party should hold both roles. A party with no active role has no role
evidence; that alone is not a role difference.

## Reference counts

For proposed pairs only, count the records that point at each side: orders, payments, ledger entries, leads,
deals and relationships for parties (every link to the party, from either side), and stock movements for items. A
count that could not be read is **unknown**, never zero. Each count is the number of filtered rows, read page by
page until an empty page; the reported total is not used, since a system may report the whole table's total or cap a
page below the limit asked for. A row that does not carry the filter value means the filter was ignored, and the
count is unknown, as it is for a row seen twice, more than 5000 rows, an error or a dropped connection. An unknown
count makes the survivor rule skip the reference step and say so. Either way, matching goes ahead.

## Build order (about 25 hours)

| # | Step | Hours | Status or needs |
|---|---|---|---|
| 1 | Write guard, with offline tests: an update refused, a delete refused, a list allowed, an unknown tool refused | 2 | done |
| 2 | Ask the Eval Harness seat what they will check, and whether their copies of the systems hold seeded duplicates. Get the person's approval for the Keystone reads. | 0.5 | approval given 3 Nov; the message is still to send |
| 3 | Keystone read: counts, both tables into `local/`, filter checks, child rows, what duplicates look like | 2 | done |
| 4 | `data_steward/dedupe.py`: normalize, group, score, exclusions, with tests on hand-made pairs. A made-up tuning set of parties and items with known duplicates and known non-duplicates. It covers typos, case and spacing, legal endings, phone formats, the same email under two names, records sharing a name prefix that are different, ordinary names that start with a bracketed prefix, different records sharing a city and postcode, items with near names and different codes, role differences, and repeated test records. Run from grouping to report, so a duplicate the grouping never finds shows up as a miss. Every value is invented, test tags included (tests pass their own tag list); nothing is copied from a live record. | 8 | none |
| 4b | The other person on the seat writes the held-back set the same way, with no entity shared with the tuning set, commits it, and does not tune. The person tuning does not open it until step 7. | (in 4) | none |
| 5 | Proposals: survivor suggestion, field differences, reference counts | 4 | done |
| 6 | JSON and Markdown report and the `python -m data_steward.dedupe` command. Under the harness runner the instance comes from the runner. The report states rows read, whether any table was cut off, and that an incomplete scan does not mean there are no duplicates. | 3 | done; run on both systems 3 Nov |
| 7 | Tune the weights and the 0.6 and 0.9 cuts on the tuning set, then freeze the whole matcher (code and settings, by commit) before opening the held-back set. Run once on the held-back set and report how many examples each band had, wrong proposals and known misses, as a check on made-up data only. Any later change that can affect which pairs are found, their scores, bands or exclusions voids that check and needs a new held-back set from the other person. Run on Keystone; one person and the seat lead review every pair it reports. | 2 | tuned and frozen at rules version 2 (3 Nov); the held-back run waits on 4b |
| 8 | README and AGENTS.md updates, pull request, review | 2 | step 7 |
| | Buffer | 1.5 | |

**Not for 15 Nov:** a model in the loop, platform records, merges, missing-field
and orphan checks, and the 12-task suite (30 Nov).

## Checks that could change this plan

- **The Suryodaya read.** Done 3 Nov: both tables far under 5000 rows and every reference filter works, so nothing
  in this plan changes.
- **The Eval Harness seat's answer.** If their check needs a platform record per proposal, add an opt-in publish
  step that needs the person's OK each run. If their copies hold seeded duplicates, use those as a further check.
