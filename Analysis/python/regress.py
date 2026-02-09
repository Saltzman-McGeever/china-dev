import statsmodels.api as sm
import matplotlib.pyplot as plt

def regress(model, y_value, x_value, label=""):
    """Regress reported cost on number of participants"""
    reg_data = model[[x_value, y_value]].dropna()
    X = sm.add_constant(reg_data[x_value])
    y = reg_data[y_value]

    reg = sm.OLS(y, X).fit()

    # Print simplified output
    print(reg.summary().tables[1])
    print(f"\nR²: {reg.rsquared:.4f}")
    print(f"Adj. R²: {reg.rsquared_adj:.4f}")
    print(f"N: {int(reg.nobs)}")
    print()

    # Create forest plot
    # Get coefficients and confidence intervals (exclude intercept)
    params = reg.params[1:]  # Exclude intercept
    conf_int = reg.conf_int()[1:]  # Exclude intercept
    param_names = [x_value]

    fig, ax = plt.subplots(figsize=(8, 2))

    # Plot point estimates and confidence intervals
    y_pos = range(len(params))
    ax.errorbar(params, y_pos,
                xerr=[(params - conf_int[0]).values, (conf_int[1] - params).values],
                fmt='o', markersize=8, capsize=5, capthick=2,
                color='steelblue', ecolor='steelblue')

    # Add vertical line at zero
    ax.axvline(x=0, color='red', linestyle='--', linewidth=1, alpha=0.5)

    # Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels(param_names)
    ax.set_xlabel('Coefficient Estimate (95% CI)')
    ax.set_title(f'Regress {y_value} on {x_value}')

    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.show()

    return reg