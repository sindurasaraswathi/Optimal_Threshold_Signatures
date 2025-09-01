#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:33:27 2025

@author: ssarasw2
"""

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
import multiprocessing as mp

import pandas as pd
df = pd.DataFrame(columns=['k', 'a', 'b', 'v', 'w', 'w*', 't_opt', 't*'])

def main(a, b, value, k):
    def prob(t, param):
        return 1 - (param / k) * t**k #Ex: p = (1-(at^2/2 for k=2)
    
    
    def objective(t, a, b, v):
        p = prob(t, a)
        q = prob(t, b)
        return (v * p * q * 0.5) + v * (1 - p)
    
    # Find the optimal t using optimization objective
    result = minimize(objective, x0=1, args=(a, b, value), bounds=[(0, None)])
    
    # The optimal t found by the minimization
    t_opt = result.x[0]
    
    # The closed-form solution for t*
    t_star = np.power(((b - a) * k) / (2 * a * b), 1/k)
    
    # Calculate cost function value at the optimal t*
    w_opt = objective(t_opt, a, b, value)
    
    # Output results
    # print(f"Optimal t from optimization: {t_opt}")
    # print(f"t* from formula: {t_star}")
    # print(f"w(optimization): {result.fun}") 
    # print(f"w* at t*: {w_opt}")

    res = [k, round(a,2), round(b,2), value, result.fun, w_opt, t_opt, t_star]
    return res
    
    
if __name__ == '__main__':
    T_max = 0.99  # Choose a suitable value for T_max
    max_a_b = 2 / (T_max ** 2)
    
    # Now, ensure that a and b are bounded by max_a_b
    a = [i*0.01 for i in range(1, 1000) if i*0.01 < max_a_b]
    b = [i*0.01 for i in range(1, 1000) if i*0.01 < max_a_b]
    value  = 10
    
    work = []
    for k in range(1, 11):
      for i in a:
          for j in b[::-1]:
              if j>i:
                  work.append([i, j, value, k])
              else:
                  break
                    
    res_list = []
    pool = mp.Pool(processes=8)
    x = pool.starmap(main, work)
    res_list.append(x)
    
    for i in res_list[0]:
        if any(np.isnan(i)):
            continue
        if i[7] > 1:
            continue
        df.loc[(len(df))] = i
        
    for i, j in df.groupby('k'):
        # Pivot the DataFrame for t1* and t2* values
        pivot_t1 = j.pivot(index='a', columns='b', values='t*')
        
        # Create a figure for the heatmap
        plt.figure(figsize=(12, 6))
        
        # Heatmap for t1*
        plt.subplot(1, 2, 1)
        sns.heatmap(pivot_t1, cmap='YlGnBu', annot=False, fmt=".2f", cbar_kws={'label': 'Scale from 0 to 1'})
        plt.title(r'$\tau^*$ vs a and b for ${}$'.format(i))
        
        # Adjust layout and show the plot
        plt.tight_layout()
        plt.show()
        
        
    # # Pivot the DataFrame for t1* and t2* values
    # pivot_t1 = df.pivot(index='a', columns='b', values='t*')
    
    # # Create a figure for the heatmap
    # plt.figure(figsize=(12, 6))
    
    # # Heatmap for t1*
    # plt.subplot(1, 2, 1)
    # sns.heatmap(pivot_t1, cmap='YlGnBu', annot=False, fmt=".2f", cbar_kws={'label': 'Scale from 0 to 1'})
    # plt.title(r'$\tau^*$ vs a and b')
    
     
    # # Adjust layout and show the plot
    # plt.tight_layout()
    # plt.show()
    
    
    
    
    