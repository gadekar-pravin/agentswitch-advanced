"""Find duplicate parties and items in the rows a `.list` tool returns. Pure functions: no network, no platform calls.

Rules only, so the same rows always give the same pairs and a verifier can recompute them. A score is a rule score,
not a probability. See docs/first-task-plan.md for why each rule exists.
"""
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations

RULES_VERSION = "1"

PROPOSE, REVIEW = 0.9, 0.6
BAND_ORDER = {"propose": 0, "review": 1}

# Weights are starting values; step 7 tunes them on the tuning set and then freezes them.
PARTY_WEIGHTS = {"customer_code": 0.7, "email": 0.6, "phone": 0.5, "name": 0.6, "near_name": 0.25, "website": 0.2,
                 "city_postal": 0.15}
ITEM_WEIGHTS = {"code": 0.7, "name": 0.5, "near_name": 0.25, "category": 0.1}
NEAR_NAME = 0.9

# A strong value held by more records than this is a shared inbox, a switchboard or a dummy, not an identity.
SHARED_LIMIT = 5
# A name token in more records than this is too common to group on ("supply", "llc" survivors, a family name).
TOKEN_LIMIT = 50

PLACEHOLDERS = {"", "n/a", "na", "none", "null", "nil", "-", "--", "unknown", "tbd", "test", "x", "0"}
LEGAL_ENDINGS = {"pvt", "private", "ltd", "limited", "llp", "llc", "inc", "incorporated", "corp", "corporation", "co",
                 "company", "plc", "gmbh"}
ORDINARY_PRIVACY = "normal"

_TAG = re.compile(r"^\[([^\]]*)\]\s*")


def flag(value) -> bool:
    """A boolean field may arrive as a bool, an int or a string: "false" must not read as true."""
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return value is True or value == 1


def blank(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip().casefold() in PLACEHOLDERS)


def strip_tag(name: str, test_tags) -> tuple[str, bool]:
    """Drop one leading [..] only when its content starts with a confirmed test-run tag. Any other bracket is part of
    the name: "[North] Acme" and "[South] Acme" must not collapse into one."""
    m = _TAG.match(name or "")
    if m and any(m.group(1).strip().casefold().startswith(t.casefold()) for t in test_tags):
        return name[m.end():], True
    return name or "", False


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).split()


def norm_name(name: str, test_tags=()) -> str:
    """Case, spacing, punctuation, accents, token order and legal endings do not make two names different."""
    words = tokens(strip_tag(name, test_tags)[0])
    kept = [w for w in words if w not in LEGAL_ENDINGS] or words
    return " ".join(sorted(kept))


def norm_email(value) -> str:
    if blank(value) or "@" not in str(value):
        return ""
    return str(value).strip().casefold()


def norm_phone(value) -> str:
    """Last ten digits, so country codes and formatting do not matter. Fewer digits, or one digit repeated, is no
    phone at all."""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) < 10 or len(set(digits)) == 1:
        return ""
    return digits[-10:]


def norm_code(value) -> str:
    # SKU punctuation can be meaningful, so only case and outer spaces are ignored.
    return "" if blank(value) else str(value).strip().casefold()


def norm_website(value) -> str:
    if blank(value):
        return ""
    host = re.sub(r"^[a-z]+://", "", str(value).strip().casefold()).split("/")[0]
    return host.removeprefix("www.")


def active_roles(row) -> frozenset:
    roles = row.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    return frozenset((r if isinstance(r, str) else r.get("role")) for r in roles
                     if isinstance(r, str) or (r.get("role") and r.get("active", True) is not False))


def first_address(row) -> dict:
    addresses = row.get("addresses") or []
    return addresses[0] if isinstance(addresses, list) and addresses and isinstance(addresses[0], dict) else {}


def _party_keys(row, test_tags) -> dict:
    address = first_address(row)
    city, postal = tokens(str(address.get("city") or "")), norm_code(address.get("postal"))
    return {
        "customer_code": norm_code(row.get("customer_code")),
        "email": norm_email(row.get("email")),
        "phone": norm_phone(row.get("phone")),
        "name": norm_name(row.get("name") or "", test_tags),
        "website": norm_website(row.get("website")),
        "city_postal": f"{' '.join(city)}|{postal}" if city and postal else "",
    }


def _item_keys(row, test_tags) -> dict:
    return {
        "code": norm_code(row.get("code")),
        "sku": norm_code(row.get("sku")),
        "name": norm_name(row.get("name") or "", test_tags),
        "category": norm_code(row.get("category_id")),
    }


PARTY_STRONG = ("customer_code", "email", "phone")
ITEM_STRONG = ("code", "sku")


def _drop_shared(keys: dict[str, dict], strong) -> dict[str, int]:
    """Blank out strong values held by too many records; returns how many values were dropped per key."""
    dropped = {}
    for key in strong:
        counts = Counter(k[key] for k in keys.values() if k[key])
        shared = {v for v, n in counts.items() if n > SHARED_LIMIT}
        if shared:
            dropped[key] = len(shared)
            for k in keys.values():
                if k[key] in shared:
                    k[key] = ""
    return dropped


def _candidates(keys: dict[str, dict], block_on) -> set[tuple[str, str]]:
    """Pairs sharing any exact key, or a name token that is not too common (so a typo in one word still meets)."""
    blocks = defaultdict(set)
    for rid, k in keys.items():
        for key in block_on:
            if k[key]:
                blocks[(key, k[key])].add(rid)
        for word in set(k["name"].split()):
            if len(word) >= 3:
                blocks[("token", word)].add(rid)
    pairs = set()
    for (kind, _), ids in blocks.items():
        if kind == "token" and len(ids) > TOKEN_LIMIT:
            continue
        pairs.update(combinations(sorted(ids), 2))
    return pairs


def _name_signal(a: str, b: str):
    if not a or not b:
        return None
    if a == b:
        return "name"
    return "near_name" if SequenceMatcher(None, a, b).ratio() >= NEAR_NAME else None


def _score_party(a, b, ka, kb):
    signals, conflicts, caps = [], [], []
    for key in ("customer_code", "email", "phone", "website", "city_postal"):
        if ka[key] and kb[key]:
            if ka[key] == kb[key]:
                signals.append(key)
            elif key in PARTY_STRONG:
                conflicts.append(key)
    name = _name_signal(ka["name"], kb["name"])
    if name:
        signals.append(name)
    ra, rb = active_roles(a), active_roles(b)
    if ra and rb and ra != rb:
        caps.append("roles differ")
    return signals, conflicts, caps, PARTY_WEIGHTS


def _score_item(_a, _b, ka, kb):
    signals, conflicts = [], []
    codes_a, codes_b = {ka["code"], ka["sku"]} - {""}, {kb["code"], kb["sku"]} - {""}
    if codes_a & codes_b:
        signals.append("code")  # code and SKU can be aliases: one match counts once
    for key in ITEM_STRONG:
        if ka[key] and kb[key] and ka[key] != kb[key] and not codes_a & codes_b:
            conflicts.append(key)
    name = _name_signal(ka["name"], kb["name"])
    if name:
        signals.append(name)
    if ka["category"] and ka["category"] == kb["category"]:
        signals.append("category")
    return signals, conflicts, [], ITEM_WEIGHTS


def _excluded_party(a, b) -> str | None:
    if flag(a.get("allow_duplicate")) or flag(b.get("allow_duplicate")):
        return "flagged as an allowed duplicate"
    if a.get("company_id") and b.get("company_id") and a["company_id"] != b["company_id"]:
        return "different companies"
    if a.get("type") and b.get("type") and a["type"] != b["type"]:
        return "individual and organisation"
    return None


def _variant_codes(row) -> set[str]:
    variants = row.get("variants") or []
    return {norm_code(v.get("sku") or v.get("code")) for v in variants if isinstance(v, dict)} - {""}


def _excluded_item(a, b) -> str | None:
    if a.get("company_id") and b.get("company_id") and a["company_id"] != b["company_id"]:
        return "different companies"
    for key, reason in (("product_type", "different kinds"), ("type", "different kinds"), ("uom", "different units")):
        if a.get(key) and b.get(key) and str(a[key]).casefold() != str(b[key]).casefold():
            return reason
    if norm_code(b.get("code")) in _variant_codes(a) or norm_code(a.get("code")) in _variant_codes(b):
        return "variant of the other item"
    return None


def band(score: float, capped: bool) -> str:
    if score < REVIEW:
        return "dropped"
    return "propose" if score >= PROPOSE and not capped else "review"


def find_duplicates(entity: str, rows: list[dict], test_tags=()) -> dict:
    """Every candidate pair of `rows`, scored and banded.

    entity: "party" or "item". test_tags: confirmed test-run tags (from local/, never hard-coded here).
    Parties under a privacy state other than the ordinary one are counted and left out before grouping, so no detail
    of theirs reaches a pair.
    """
    if entity not in ("party", "item"):
        raise ValueError(f"unknown entity {entity!r}")
    withheld = 0
    by_id = {}
    for row in rows:
        if entity == "party" and row.get("privacy_state") != ORDINARY_PRIVACY:
            withheld += 1
            continue
        by_id[str(row["id"])] = row
    key_fn, score_fn, exclude_fn, strong, block_on = (
        (_party_keys, _score_party, _excluded_party, PARTY_STRONG, ("customer_code", "email", "phone", "website"))
        if entity == "party" else
        (_item_keys, _score_item, _excluded_item, ITEM_STRONG, ("code", "sku")))
    keys = {rid: key_fn(row, test_tags) for rid, row in by_id.items()}
    ignored_shared = _drop_shared(keys, strong)

    pairs, excluded, dropped = [], [], 0
    for ida, idb in sorted(_candidates(keys, block_on + ("name",))):
        a, b = by_id[ida], by_id[idb]
        signals, conflicts, caps, weights = score_fn(a, b, keys[ida], keys[idb])
        score = round(min(1.0, sum(weights[s] for s in signals)), 2)
        if conflicts:
            caps = [f"{c} differs" for c in conflicts] + caps
        result = {
            "id": f"{entity}:{ida}:{idb}",
            "entity": entity,
            "ids": [ida, idb],
            "score": score,
            "band": band(score, bool(caps)),
            "signals": signals,
            "caps": caps,
            "tagged": strip_tag(a.get("name") or "", test_tags)[1] or strip_tag(b.get("name") or "", test_tags)[1],
        }
        if result["band"] == "dropped":
            dropped += 1
            continue
        reason = exclude_fn(a, b)
        if reason:
            excluded.append({**result, "band": "excluded", "reason": reason})
            continue
        pairs.append(result)

    in_pairs = Counter(rid for p in pairs for rid in p["ids"])
    for p in pairs:
        p["shared_record"] = any(in_pairs[rid] > 1 for rid in p["ids"])
    pairs.sort(key=lambda p: (BAND_ORDER[p["band"]], p["id"]))
    excluded.sort(key=lambda p: p["id"])
    return {"entity": entity, "rules_version": RULES_VERSION, "rows": len(rows), "withheld_private": withheld,
            "ignored_shared": ignored_shared, "pairs": pairs, "excluded": excluded, "dropped": dropped}


def evaluate(result: dict, duplicates, distinct) -> dict:
    """Compare a result with known answers. `duplicates` and `distinct` are lists of id pairs.

    A known duplicate that is not in a listed band is a miss, whether grouping never met the pair or its score fell
    below review. A known non-duplicate in a band is a wrong proposal for that band.
    """
    known_dup = {tuple(sorted(map(str, p))) for p in duplicates}
    known_distinct = {tuple(sorted(map(str, p))) for p in distinct}
    by_band = {"propose": Counter(), "review": Counter()}
    listed = set()
    for p in result["pairs"]:
        pair = tuple(p["ids"])
        listed.add(pair)
        by_band[p["band"]]["right" if pair in known_dup else "wrong" if pair in known_distinct else "unlabelled"] += 1
    return {
        "bands": {b: dict(c) for b, c in by_band.items()},
        "missed": sorted(known_dup - listed),
        "wrong": sorted((p["band"], tuple(p["ids"])) for p in result["pairs"] if tuple(p["ids"]) in known_distinct),
    }
