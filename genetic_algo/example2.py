import random
import string

# ─────────────────────────────────────────
# Target password
# ─────────────────────────────────────────
TARGET   = "123helloworld156" # Change this for a password to be guessed by the algorithm
GENE_POOL = string.ascii_lowercase + string.digits   # a-z + 0-9

# ─────────────────────────────────────────
# GA Parameters
# ─────────────────────────────────────────
POP_SIZE      = 200
MUTATION_RATE = 0.05
ELITE_SIZE    = 10


# ─────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────
def random_individual() -> str:
    return "".join(random.choice(GENE_POOL) for _ in range(len(TARGET)))


def fitness(individual: str) -> int:
    """Count how many characters match the target at the same position."""
    return sum(a == b for a, b in zip(individual, TARGET))


def tournament_select(population: list[str], k: int = 5) -> str:
    contestants = random.sample(population, k)
    return max(contestants, key=fitness)


def crossover(parent1: str, parent2: str) -> str:
    """Single-point crossover."""
    point = random.randint(1, len(TARGET) - 1)
    return parent1[:point] + parent2[point:]


def mutate(individual: str) -> str:
    """Randomly replace a character with a new one from the gene pool."""
    chars = list(individual)
    for i in range(len(chars)):
        if random.random() < MUTATION_RATE:
            chars[i] = random.choice(GENE_POOL)
    return "".join(chars)


def highlight(individual: str) -> str:
    """Show correct chars as-is, wrong chars as '_'."""
    return "".join(c if c == t else "_" for c, t in zip(individual, TARGET))


# ─────────────────────────────────────────
# Main GA loop
# ─────────────────────────────────────────
def genetic_algorithm():
    population = [random_individual() for _ in range(POP_SIZE)]
    best       = max(population, key=fitness)

    print("=" * 50)
    print("  GENETIC ALGORITHM — PASSWORD GUESSER")
    print("=" * 50)
    print(f"  Target      : {'*' * len(TARGET)}")
    print(f"  Length      : {len(TARGET)} characters")
    print(f"  Gene pool   : '{GENE_POOL}'  ({len(GENE_POOL)} chars)")
    print(f"  Population  : {POP_SIZE}")
    print(f"  Mutation    : {MUTATION_RATE:.0%}")
    print("=" * 50)
    print(f"\n  {'Gen':>5}  {'Best Guess':<12}  {'Hint':<12}  {'Score':>5}")
    print("  " + "-" * 42)

    for gen in range(1, 10_001):
        fits = [fitness(ind) for ind in population]

        # Elitism
        elite_idx = sorted(range(len(population)), key=lambda i: fits[i], reverse=True)
        new_pop   = [population[i] for i in elite_idx[:ELITE_SIZE]]

        # Breed next generation
        while len(new_pop) < POP_SIZE:
            p1    = tournament_select(population)
            p2    = tournament_select(population)
            child = crossover(p1, p2)
            child = mutate(child)
            new_pop.append(child)

        population = new_pop
        best       = max(population, key=fitness)
        best_score = fitness(best)

        # Print progress every 10 generations, or on improvement
        if gen % 10 == 0 or best_score == len(TARGET) or gen == 1:
            print(f"  {gen:>5}  {best:<12}  {highlight(best):<12}  {best_score:>2}/{len(TARGET)}")

        if best_score == len(TARGET):
            print("\n" + "=" * 50)
            print(f"  ✅ Password cracked in generation {gen}!")
            print(f"  🔑 Password : {best}")
            print("=" * 50)
            return best, gen

    print("\n  ❌ Could not crack password within 10,000 generations.")
    return best, 10_000


# ─────────────────────────────────────────
# Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    random.seed(99)
    genetic_algorithm()