# Metalog and metalog logit quantile and probability density functions implemented using the following resources:
# http://www.metalogdistributions.com/home.html
# http://www.metalogdistributions.com/images/The_Metalog_Distributions_-_Keelin_2016.pdf

import math
import numpy as np

def build_y(n, y):
    def row(y):
        half = y - 0.5
        ln = math.log(y / (1 - y))

        result = [1, ln]

        if n >= 3:
            result.append(half * ln)
        if n >= 4:
            result.append(half)
        for i in range(5, n + 1):
            if i % 2 == 1:
                result.append(half ** (i // 2))
            else:
                result.append(ln * (half ** (i // 2 - 1)))

        return result

    Y = []

    for y_i in y:
        Y.append(row(y_i))

    return Y

def metalog_func(n, x, y, z):
    Y = np.array(build_y(n, y))
    a = (np.linalg.inv(Y.T @ Y) @ Y.T) @ np.array(z)

    assert a.size >= n
    assert n >= 2

    u = [(a[0], 0)]
    s = [(a[1], 0)]

    if n >= 3:
        s.append((a[2], 1))
    if n >= 4:
        u.append((a[3], 1))
    for i in range(5, n + 1):
        if i % 2 == 1:
            u.append((a[i - 1], i // 2))
        else:
            s.append((a[i - 1], i // 2 - 1))

    def metalog(y):
        half = y - 0.5
        ln = math.log(y / (1 - y))

        u_summed = sum([a * (half ** b) for (a, b) in u])
        s_summed = sum([a * (half ** b) for (a, b) in s])
        return u_summed + s_summed * ln

    return metalog

def metalog_logit_func(n, x, y, z):
    metalog = metalog_func(n, x, y, z)

    def metalog_logit(y):
        if y == 0:
            return p0
        elif y == 1:
            return p100

        e = math.exp(metalog(y))
        return (p0 + p100 * e) / (1 + e)

    return metalog_logit

def metalog_pdf_func(n, x, y, z):
    Y = np.array(build_y(n, y))
    a = (np.linalg.inv(Y.T @ Y) @ Y.T) @ np.array(z)

    assert a.size >= n
    assert n >= 2

    def metalog_pdf(y):
        y_one_m = y * (1 - y)
        half = y - 0.5
        ln = math.log(y / (1 - y))

        terms = [a[1] / y_one_m]

        if n >= 3:
            terms.append(a[2] * (half / y_one_m + ln))
        if n >= 4:
            terms.append(a[3])
        for i in range(5, n + 1):
            if i % 2 == 1:
                halved = i // 2
                terms.append(a[i - 1] * halved * (half ** (halved - 1)))
            else:
                halved = i // 2 - 1
                term_sum = (half ** halved) / y_one_m + halved * (half ** (halved - 1)) * ln
                terms.append(a[i - 1] * term_sum)

        return 1 / sum(terms)

    return metalog_pdf

def metalog_logit_pdf_func(n, x, y, z):
    metalog = metalog_func(n, x, y, z)
    metalog_pdf = metalog_pdf_func(n, x, y, z)

    def metalog_logit_pdf(y):
        if y == 0 or y == 1:
            return 0

        e = math.exp(metalog(y))
        return metalog_pdf(y) * ((1 + e) ** 2) / ((p100 - p0) * e)

    return metalog_logit_pdf

def logit_z(x, p0, p100):
    return [math.log((x_i - p0) / (p100 - x_i)) for x_i in x]


p0 = 0
p10 = 0.05 # 50 milliseconds
p50 = 0.1 # 100 milliseconds
p90 = 0.3 # 300 milliseconds
p95 = 0.5 # 500 milliseconds
p99 = 0.9 # 900 milliseconds
p99_9 = 1.7
p100 = 3

x = [p10, p50, p90, p95, p99, p99_9]
y = [0.1, 0.5, 0.9, 0.95, 0.99, 0.999]
z = logit_z(x, p0, p100)


def plot_quantile_func(n):
    metalog = metalog_logit_func(n, x, y, z)

    rng = np.random.default_rng()
    horizontal = rng.random(10000)
    vertical = [metalog(x) for x in horizontal.flat]

    fig, ax = plt.subplots()
    ax.hist(vertical, bins=100, linewidth=0.3, edgecolor="white")
    ax.set(xlim=(p0, p100))
    plt.show()

def plot_pdf_func(n):
    metalog = metalog_logit_func(n, x, y, z)
    metalog_pdf = metalog_logit_pdf_func(n, x, y, z)

    y_vals = np.linspace(0, 1, num=100)
    horizontal = np.array([metalog(x) for x in y_vals.flat])
    vertical = np.array([metalog_pdf(x) for x in y_vals.flat])
    vertical = vertical / np.sum(vertical)

    fig, ax = plt.subplots()
    ax.plot(horizontal, vertical, linewidth=2.0)
    ax.set(xlim=(p0, p100))
    plt.show()

    cdf = np.array([sum(vertical[:i]) for i in range(vertical.size)])

    fig, ax = plt.subplots()
    ax.plot(horizontal, cdf, linewidth=2.0)
    ax.set(xlim=(p0, p100))
    plt.show()