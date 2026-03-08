from itertools import combinations

# Dataset
transactions = [
    {"bread", "butter", "milk"},
    {"bread", "butter"},
    {"beer", "cookies", "diapers"},
    {"milk", "diapers", "bread", "butter"},
    {"beer", "diapers"},
]

MIN_SUPPORT    = 0.40   # 40%
MIN_CONFIDENCE = 0.60   # 60%
N = len(transactions)

# Helper utilities
def support(itemset: frozenset) -> float:
    """Fraction of transactions that contain all items in itemset."""
    count = sum(1 for t in transactions if itemset.issubset(t))
    return count / N


def get_frequent_itemsets(candidates: list[frozenset]) -> dict[frozenset, float]:
    """Return candidates that meet the minimum support threshold."""
    return {c: support(c) for c in candidates if support(c) >= MIN_SUPPORT}


def generate_candidates(prev_frequent: list[frozenset], k: int) -> list[frozenset]:
    prev = sorted([sorted(s) for s in prev_frequent])
    candidates = set()
    for i in range(len(prev)):
        for j in range(i + 1, len(prev)):
            # Join step: share first k-2 items
            if prev[i][:k - 2] == prev[j][:k - 2]:
                candidate = frozenset(prev[i]) | frozenset(prev[j])
                # Prune step: all (k-1)-subsets must be frequent
                if all(
                    frozenset(sub) in prev_frequent
                    for sub in combinations(candidate, k - 1)
                ):
                    candidates.add(candidate)
    return list(candidates)


# Apriori – mine frequent itemsets
def apriori() -> dict[frozenset, float]:
    all_items = frozenset().union(*transactions)

    # k = 1
    k1_candidates = [frozenset([item]) for item in all_items]
    frequent = get_frequent_itemsets(k1_candidates)
    all_frequent = dict(frequent)

    k = 2
    while frequent:
        candidates = generate_candidates(list(frequent.keys()), k)
        if not candidates:
            break
        frequent = get_frequent_itemsets(candidates)
        all_frequent.update(frequent)
        k += 1

    return all_frequent


# Association rule generation
def generate_rules(frequent_itemsets: dict[frozenset, float]):
    rules = []
    for itemset, sup in frequent_itemsets.items():
        if len(itemset) < 2:
            continue
        for r in range(1, len(itemset)):
            for antecedent in map(frozenset, combinations(itemset, r)):
                consequent = itemset - antecedent
                conf = sup / frequent_itemsets.get(antecedent, support(antecedent))
                if conf >= MIN_CONFIDENCE:
                    lift = conf / support(consequent)
                    rules.append((antecedent, consequent, sup, conf, lift))
    return rules


# Run & display results
def fmt(itemset: frozenset) -> str:
    return "{" + ", ".join(sorted(itemset)) + "}"


if __name__ == "__main__":
    print("=" * 60)
    print("  APRIORI ALGORITHM")
    print(f"  Transactions : {N}")
    print(f"  Min Support  : {MIN_SUPPORT:.0%}")
    print(f"  Min Confidence: {MIN_CONFIDENCE:.0%}")
    print("=" * 60)

    # ── Frequent Itemsets ──────────────────
    frequent_itemsets = apriori()

    print("\n FREQUENT ITEMSETS")
    print("-" * 40)
    for size in sorted(set(len(k) for k in frequent_itemsets)):
        print(f"\n  {size}-itemset(s):")
        for itemset, sup in sorted(frequent_itemsets.items(), key=lambda x: -x[1]):
            if len(itemset) == size:
                print(f"    {fmt(itemset):<35} support = {sup:.2%}")

    # ── Association Rules ──────────────────
    rules = generate_rules(frequent_itemsets)

    print("\n\n📐 ASSOCIATION RULES")
    print("-" * 60)
    if not rules:
        print("  No rules meet the confidence threshold.")
    else:
        print(f"  {'Rule':<40} {'Sup':>6}  {'Conf':>6}  {'Lift':>6}")
        print("  " + "-" * 58)
        for ant, cons, sup, conf, lift in sorted(rules, key=lambda x: -x[3]):
            rule_str = f"{fmt(ant)} → {fmt(cons)}"
            print(f"  {rule_str:<40} {sup:>5.2%}  {conf:>5.2%}  {lift:>5.2f}")

    print("\n" + "=" * 60)