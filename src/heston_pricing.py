import numpy as np
from scipy.integrate import quad

# Complex number
i = complex(0,1)

# First Implementation
def heston_charfunc(phi, S0, v0, kappa, theta, sigma, rho, lambd, tau, r):
    a = kappa * theta
    b = kappa + lambd
    rspi = rho * sigma * phi * 1j
    d = np.sqrt((rho * sigma * phi * 1j - b) ** 2 + (phi * 1j + phi ** 2) * sigma ** 2)
    g = (b - rspi + d) / (b - rspi - d)
    exp1 = np.exp(r * phi * 1j * tau)
    term2 = S0 ** (phi * 1j) * ((1 - g * np.exp(d * tau)) / (1 - g)) ** (-2 * a / sigma ** 2)
    exp2 = np.exp(a * tau * (b - rspi + d) / sigma ** 2 + v0 * (b - rspi + d) * ((1 - np.exp(d * tau)) / (1 - g * np.exp(d * tau))) / sigma ** 2)
    return exp1 * term2 * exp2

def integrand(phi, S0, v0, kappa, theta, sigma, rho, lambd, tau, r, K):
    args = (S0, v0, kappa, theta, sigma, rho, lambd, tau, r)
    numerator = np.exp(r * tau) * heston_charfunc(phi - 1j, *args) - K * heston_charfunc(phi, *args)
    denominator = 1j * phi * K ** (1j * phi)
    return numerator / denominator

def heston_price(S0, K, v0, kappa, theta, sigma, rho, lambd, tau, r):
    args = (S0, v0, kappa, theta, sigma, rho, lambd, tau, r, K)
    real_integral, err = quad(lambda phi: np.real(integrand(phi, *args)), 0, 100)
    return np.real((S0 - K * np.exp(-r * tau)) / 2 + real_integral / np.pi)

# Second Implementation
def fHeston(s, St, K, r, T, sigma, kappa, theta, volvol, rho):
    prod = rho * sigma * i * s 
    d1 = (prod - kappa) ** 2
    d2 = (sigma ** 2) * (i * s + s ** 2)
    d = np.sqrt(d1 + d2)
    g1 = kappa - prod - d
    g2 = kappa - prod + d
    g = g1 / g2
    exp1 = np.exp(np.log(St) * i * s) * np.exp(i * s * r * T)
    exp2 = 1 - g * np.exp(-d * T)
    exp3 = 1 - g
    mainExp1 = exp1 * np.power(exp2 / exp3, -2 * theta * kappa / (sigma ** 2))
    exp4 = theta * kappa * T / (sigma ** 2)
    exp5 = volvol / (sigma ** 2)
    exp6 = (1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T))
    mainExp2 = np.exp((exp4 * g1) + (exp5 * g1 * exp6))
    return mainExp1 * mainExp2

def priceHestonMid(St, K, r, T, sigma, kappa, theta, volvol, rho):
    P, iterations, maxNumber = 0, 1000, 100
    ds = maxNumber / iterations
    element1 = 0.5 * (St - K * np.exp(-r * T))
    for j in range(1, iterations):
        s1 = ds * (2 * j + 1) / 2
        s2 = s1 - i
        numerator1 = fHeston(s2, St, K, r, T, sigma, kappa, theta, volvol, rho)
        numerator2 = K * fHeston(s1, St, K, r, T, sigma, kappa, theta, volvol, rho)
        denominator = np.exp(np.log(K) * i * s1) * i * s1
        P += ds * (numerator1 - numerator2) / denominator
    element2 = P / np.pi
    return np.real((element1 + element2))

# Parameters to test model
S0 = 110. # initial asset price
K = 100. # strike
v0 = 0.21 # initial variance
r = 0.05 # risk free rate
kappa = 1.5768 # rate of mean reversion of variance process
theta = 0.0398 # long-term mean variance
volvol = 0.3 # volatility of volatility
sigma = 0.575 # risk premium of variance
rho = -0.711 # correlation between variance and stock process
tau = 1. # time to maturity

# First implementation
price1 = heston_price(S0, K, v0, kappa, theta, volvol, rho, sigma, tau, r)

# Second implementation
price2 = priceHestonMid(S0, K, r, tau, volvol, kappa, theta, v0, rho)

print(f"First implementation price: {price1}")
print(f"Second implementation price: {price2}")
