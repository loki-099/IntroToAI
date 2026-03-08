import random
import math

# ─────────────────────────────────────────
# Cities (name, x, y)
# ─────────────────────────────────────────
CITIES = {
    "Manila":    (14.5995, 120.9842),
    "Cebu":      (10.3157, 123.8854),
    "Davao":     (7.1907,  125.4553),
    "Iloilo":    (10.7202, 122.5621),
    "Cagayan":   (8.4542,  124.6319),
    "Bacolod":   (10.6769, 122.9560),
    "Zamboanga": (6.9214,  122.0790),
    "Baguio":    (16.4023, 120.5960),
}

CITY_NAMES = list(CITIES.keys())
N_CITIES   = len(CITY_NAMES)

# ─────────────────────────────────────────
# GA Parameters
# ─────────────────────────────────────────
POP_SIZE        = 200
GENERATIONS     = 500
MUTATION_RATE   = 0.02
ELITE_SIZE      = 20
TOURNAMENT_SIZE = 5


# ─────────────────────────────────────────
# Distance utilities
# ─────────────────────────────────────────
def haversine(c1: str, c2: str) -> float:
    """Great-circle distance in km between two cities."""
    lat1, lon1 = CITIES[c1]
    lat2, lon2 = CITIES[c2]
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def route_distance(route: list[str]) -> float:
    """Total round-trip distance of a route."""
    total = sum(haversine(route[i], route[i + 1]) for i in range(len(route) - 1))
    total += haversine(route[-1], route[0])   # return to start
    return total


def fitness(route: list[str]) -> float:
    return 1 / route_distance(route)


# ─────────────────────────────────────────
# GA Operators
# ─────────────────────────────────────────
def create_individual() -> list[str]:
    ind = CITY_NAMES[:]
    random.shuffle(ind)
    return ind


def tournament_select(population: list, fitnesses: list[float]) -> list[str]:
    contestants = random.sample(range(len(population)), TOURNAMENT_SIZE)
    best = max(contestants, key=lambda i: fitnesses[i])
    return population[best][:]


def ordered_crossover(parent1: list[str], parent2: list[str]) -> list[str]:
    """Order Crossover (OX)."""
    size = len(parent1)
    a, b = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[a:b+1] = parent1[a:b+1]
    remaining = [c for c in parent2 if c not in child]
    idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = remaining[idx]
            idx += 1
    return child


def mutate(route: list[str]) -> list[str]:
    """Swap mutation."""
    route = route[:]
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route


# ─────────────────────────────────────────
# Main GA loop
# ─────────────────────────────────────────
def genetic_algorithm():
    # Initialise population
    population = [create_individual() for _ in range(POP_SIZE)]
    best_route  = None
    best_dist   = float("inf")
    history     = []

    for gen in range(1, GENERATIONS + 1):
        fits = [fitness(ind) for ind in population]

        # Track best
        gen_best_idx  = max(range(len(population)), key=lambda i: fits[i])
        gen_best_dist = route_distance(population[gen_best_idx])
        if gen_best_dist < best_dist:
            best_dist  = gen_best_dist
            best_route = population[gen_best_idx][:]

        history.append(best_dist)

        # Elitism – carry top individuals unchanged
        elite_idx  = sorted(range(len(population)), key=lambda i: fits[i], reverse=True)
        new_pop    = [population[i][:] for i in elite_idx[:ELITE_SIZE]]

        # Fill rest via selection → crossover → mutation
        while len(new_pop) < POP_SIZE:
            p1 = tournament_select(population, fits)
            p2 = tournament_select(population, fits)
            child = ordered_crossover(p1, p2)
            child = mutate(child)
            new_pop.append(child)

        population = new_pop

        if gen % 100 == 0 or gen == 1:
            print(f"  Generation {gen:>4} │ Best distance: {best_dist:,.2f} km")

    return best_route, best_dist, history


# ─────────────────────────────────────────
# Display results
# ─────────────────────────────────────────
if __name__ == "__main__":
    random.seed(42)

    print("=" * 55)
    print("  GENETIC ALGORITHM — TRAVELLING SALESMAN PROBLEM")
    print("=" * 55)
    print(f"\n  Cities       : {N_CITIES}")
    print(f"  Population   : {POP_SIZE}")
    print(f"  Generations  : {GENERATIONS}")
    print(f"  Mutation rate: {MUTATION_RATE:.0%}")
    print(f"  Elitism size : {ELITE_SIZE}")
    print(f"  Tournament   : {TOURNAMENT_SIZE}\n")
    print("-" * 55)

    best_route, best_dist, history = genetic_algorithm()

    print("\n" + "=" * 55)
    print("  BEST ROUTE FOUND")
    print("=" * 55)
    full_route = best_route + [best_route[0]]   # close loop
    for i, city in enumerate(full_route):
        arrow = " →" if i < len(full_route) - 1 else ""
        leg   = f"  ({haversine(full_route[i], full_route[i+1]):,.1f} km)" \
                if i < len(full_route) - 1 else ""
        print(f"  {i+1:>2}. {city:<12}{leg}{arrow}")

    print(f"\n  Total distance : {best_dist:,.2f} km")
    print(f"  Improvement    : {history[0] - best_dist:,.2f} km "
          f"({(history[0] - best_dist) / history[0]:.1%} reduction)")
    print("=" * 55)