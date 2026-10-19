import numpy as np
from scipy.integrate import odeint
from typing import Dict, Any, List

def seir_deriv(y, t, N, beta, sigma, gamma, mu):
    """
    Differential equations for classical SEIR-D model:
    dS/dt = -beta * S * I / N
    dE/dt = beta * S * I / N - sigma * E
    dI/dt = sigma * E - gamma * I - mu * I
    dR/dt = gamma * I
    dD/dt = mu * I
    """
    S, E, I, R, D = y
    dSdt = -beta * S * I / N
    dEdt = (beta * S * I / N) - (sigma * E)
    dIdt = (sigma * E) - (gamma * I) - (mu * I)
    dRdt = gamma * I
    dDdt = mu * I
    return [dSdt, dEdt, dIdt, dRdt, dDdt]

class SEIRBaselineModel:
    """
    Classical non-spatial aggregate SEIR model for Kenya.
    Used as benchmark baseline for H1 hypothesis testing.
    """
    def __init__(
        self,
        population: int = 47564296,
        initial_infected: int = 50,
        initial_exposed: int = 150,
        beta: float = 0.35,      # Transmission rate
        sigma: float = 1.0 / 5.2, # Latency rate (incubation ~5.2 days)
        gamma: float = 1.0 / 10.0,# Recovery rate (~10 days)
        mu: float = 0.015         # Infection fatality rate (~1.5%)
    ):
        self.N = population
        self.I0 = initial_infected
        self.E0 = initial_exposed
        self.R0_init = 0
        self.D0 = 0
        self.S0 = self.N - self.I0 - self.E0
        self.beta = beta
        self.sigma = sigma
        self.gamma = gamma
        self.mu = mu

    def run(self, days: int = 180) -> Dict[str, Any]:
        t = np.linspace(0, days, days + 1)
        y0 = [self.S0, self.E0, self.I0, self.R0_init, self.D0]
        
        solution = odeint(seir_deriv, y0, t, args=(self.N, self.beta, self.sigma, self.gamma, self.mu))
        
        S, E, I, R, D = solution.T
        
        # Daily new cases calculation: sigma * E
        daily_new_cases = np.diff(np.insert(S[0] - S, 0, 0))
        daily_new_cases = np.maximum(0, daily_new_cases)
        
        return {
            "days": t.tolist(),
            "susceptible": np.round(S).tolist(),
            "exposed": np.round(E).tolist(),
            "infected": np.round(I).tolist(),
            "recovered": np.round(R).tolist(),
            "deceased": np.round(D).tolist(),
            "daily_new_cases": np.round(daily_new_cases).tolist(),
            "peak_infections": float(np.max(I)),
            "peak_day": int(np.argmax(I)),
            "total_deaths": float(D[-1])
        }
