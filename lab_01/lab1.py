import math
import matplotlib.pyplot as plt

class MyRandom:
    def __init__(self, seed=None):
        self.c = 2**31 - 1
        self.a = 16807
        self.b = 0
        if seed is None:
            import time
            self.state = int(time.time()) % self.c
        else:
            self.state = seed

    def next_u(self):
        self.state = (self.a * self.state + self.b) % self.c
        return self.state / self.c


def gen_poisson(rng, lam):
    X = -1
    S = 1.0
    q = math.exp(-lam)
    while S > q:
        U = rng.next_u()
        S *= U
        X += 1
    return X

def gen_normal(rng, mu, sigma):
    u1 = rng.next_u()
    u2 = rng.next_u()

    if u1 <= 0: u1 = 1e-10

    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + z0 * sigma

def run_simulation():
    n_samples = 10000
    lam = 4.0
    mu = 0.0
    sigma = 1.0
    seed_value = 42

    rng_p = MyRandom(seed=seed_value)
    rng_n = MyRandom(seed=seed_value)

    poisson_data = [gen_poisson(rng_p, lam) for _ in range(n_samples)]
    normal_data = [gen_normal(rng_n, mu, sigma) for _ in range(n_samples)]

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.hist(poisson_data, bins=range(min(poisson_data), max(poisson_data) + 2),
             density=True, alpha=0.7, color='blue', edgecolor='black')
    plt.title(fr"Rozkład Poissona ($\lambda$={lam})")
    plt.xlabel("Wartość")
    plt.ylabel("Prawdopodobieństwo")

    plt.subplot(1, 2, 2)
    plt.hist(normal_data, bins=50, density=True, alpha=0.7, color='green', edgecolor='black')
    plt.title(fr"Rozkład Normalny ($\mu$={mu}, $\sigma$={sigma})")
    plt.xlabel("Wartość")
    plt.ylabel("Gęstość")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()
