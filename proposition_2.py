import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize
import multiprocessing as mp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.DataFrame(columns = ['a', 'b', 'v', 'lambda', 'gamma', "w", 'w*', "T", "T*", 't1', 't1*', 't2', 't2*'])


# Define p(t1) and q(t1)
def main2(v, a, b, lambda_, gamma):
    def p_t(t1, t, a):
        return (1-a*0.5*t1**2) * np.exp(-lambda_ * t)
    
    def q_t(t1, t, b):
        return (1-b*0.5*t1**2) * np.exp(-gamma * t)
    
    # Define integrals for objective function
    def integral_0_T(t1, T):
        # Function for integral from 0 to T
        term1 = lambda t: p_t(t1, t, a) * q_t(t1, t, b) 
        term2 = lambda t: (1 - p_t(t1, t, a))
        result1, _ = quad(term1, 0, T)
        result2, _ = quad(term2, 0, T)
        return result1 + result2
    
    def integral_T_inf(t2, T):
        # Function for integral from T to inf
        term1 = lambda t: p_t(t2, t, a) * q_t(t2, t, b) 
        term2 = lambda t: (1 - p_t(t2, t, a))
        result1, _ = quad(term1, T, np.inf)
        result2, _ = quad(term2, T, np.inf)
        return result1 + result2
    
    # Define objective function to minimize
    def objective(x):
        t1, t2, T = x
        integral_0_T_val = integral_0_T(t1, T)
        integral_T_inf_val = integral_T_inf(t2, T)
        return (v / 2) * integral_0_T_val + v * integral_T_inf_val
    
    # Optimization setup
    x0 = [1, 1, 1]  # Initial guesses for t1, t2, and T
    bounds = [(0, None), (0, None), (0, None)]  # Bounds for t1, t2, and T
    
    # Minimize the objective function
    result = minimize(objective, x0, bounds=bounds)
    
    # Get the optimal values
    t1_opt, t2_opt, T_opt = result.x
    # print(result)
    
    
    term_y = lambda t: np.exp(-lambda_ *t)
    term_z = lambda t: np.exp(-(lambda_+gamma) *t)
    y1 = quad(term_y, 0, T_opt)[0]
    z1 = quad(term_z, 0, T_opt)[0]
    
    # Closed-form formulas for t1* and T*
    t1_star = np.sqrt((b + a * (1 - 2 * (y1+1e-6) / (z1+1e-6))) / (a * b))  
    
    y2 = quad(term_y, T_opt, np.inf)[0]
    z2 = quad(term_z, T_opt, np.inf)[0]
    
    
    # Closed-form formulas for t2* and T*
    t2_star = np.sqrt((b + a * (1 - 2 * (y2+1e-6) / (z2+1e-6))) / (a * b))  
    # print((b + a * (1 - 2 * (y2+1e-6) / (z2+1e-6))) / (a * b))
    def prob(t, flag):
        if flag == "p":
            return (1-a*0.5*t**2)
        else:
            return (1-b*0.5*t**2)
        
    T_star = (1 / gamma) * np.log(((prob(t1_star, 'p')*prob(t1_star, 'q')) - (prob(t2_star, 'p')*prob(t2_star, 'q')))/(2*(prob(t1_star, 'p') - prob(t2_star, 'p'))))
    
    # Calculate w*(t*) as per the problem
    def w(t1star, t2star, T_star, a, b, v):
        integral_0_T_val = integral_0_T(t1star, T_star)
        integral_T_inf_val = integral_T_inf(t2star, T_star)
        return (v / 2) * integral_0_T_val + v * integral_T_inf_val
        
    # Calculate w at the optimal t*
    w_opt = w(t1_star, t2_star, T_star, a, b, v)


    # print(result.fun, w_opt)
    # # Output the results
    # print(f"Optimal t1: {t1_opt}")
    # print(f"Optimal t2: {t2_opt}")
    # print(f"Optimal T: {T_opt}")
    # print(f"Closed-form t1*: {t1_star}")
    # print(f"Closed-form t1*: {t2_star}")
    # print(f"Closed-form T*: {T_star}")


    res = [round(a,2), round(b,2), v, lambda_, gamma, result.fun, w_opt, T_opt, T_star, t1_opt, t1_star, t2_opt, t2_star]
    # df1.loc[(len(df1))] = res
    return res


if __name__ == '__main__':
    T_max = 0.99  # Choose a suitable value for T_max
    max_a_b = 2 / (T_max ** 2)
    value = 10
    
    # Now, ensure that a and b are bounded by max_a_b
    a = [i*0.01 for i in range(1, 100)]
    b = [i*0.01 for i in range(1, 100)]
    
    lmda = [i*0.2 for i in range(1, 2)]
    gma = [i*0.02 for i in range(1, 5)]
    
    work = []
    for aa in a:
        for bb in b[::-1]:
            if bb>aa:
                for ld in lmda:
                    for gm in gma: 
                        work.append([value, aa, bb, ld, gm])
            else:
                break
    
    print(len(work))
    res_list = []
    pool = mp.Pool(processes=8)
    x = pool.starmap(main2, work)
    res_list.append(x)
    # res = main2(value, aa, bb, ld, gm)
    # print(res)
    for i in res_list[0]:
        if any(np.isnan(i)):
            continue
        if i[10] > 1 or i[12] > 1:
            continue
        df.loc[(len(df))] = i
    
    # Pivot the DataFrame for t1* and t2* values
    df_unique = df.drop_duplicates(subset=['a', 'b'])
    pivot_t1 = df_unique.pivot(index='a', columns='b', values='t1*')
    pivot_t2 = df_unique.pivot(index='a', columns='b', values='t2*')
    
    # Create a figure for the heatmap
    plt.figure(figsize=(12, 6))
    
    # Define the color scale (from 0 to 1)
    vmin, vmax = 0, 1
    
    # Heatmap for t1*
    plt.subplot(1, 2, 1)
    sns.heatmap(pivot_t1, cmap='YlGnBu', annot=True, fmt=".2f", vmin=vmin, vmax=vmax, cbar_kws={'label': 'Scale from 0 to 1'})
    plt.title(r'$\tau_1^*$ vs a and b')
    
    # Heatmap for t2*
    plt.subplot(1, 2, 2)
    sns.heatmap(pivot_t2, cmap='YlGnBu', annot=True, fmt=".2f", vmin=vmin, vmax=vmax, cbar_kws={'label': 'Scale from 0 to 1'})
    plt.title(r'$\tau_2^*$ vs a and b')
    
    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()


    # Scatter plot of b vs T*
    # plt.figure(figsize=(10, 6))
    # sns.scatterplot(data=df, x='b', y='T*', color='blue')
    
    # # Set the title and labels
    # plt.title('Scatter Plot of b vs T*')
    # plt.xlabel('b')
    # plt.ylabel('T*')


    # # Show the plot
    # plt.show()
    
    # # Scatter plot of b vs T*
    # plt.figure(figsize=(10, 6))
    # sns.scatterplot(data=df, x='a', y='T*', color='blue')
    
    # # Set the title and labels
    # plt.title('Scatter Plot of a vs T*')
    # plt.xlabel('a')
    # plt.ylabel('T*')


    # # Show the plot
    # plt.show() --   


    # # Create a scatter plot with a regression line to visualize the relationship
    # plt.figure(figsize=(10, 6))
    
    # # Using regplot to add a regression line
    # sns.regplot(data=df, x='a', y='T*', scatter_kws={'color': 'blue'}, line_kws={'color': 'red'}, ci=None)
    
    # # Set the title and labels
    # plt.title('Relationship Between a and T*')
    # plt.xlabel('a')
    # plt.ylabel('T*')
    
    # # Show the plot
    # plt.show()
