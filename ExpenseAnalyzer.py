	import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Simple keyword‑based categorization map
CATEGORY_MAP = {
    'grocery': 'Food',
    'supermarket': 'Food',
    'restaurant': 'Food',
    'cafe': 'Food',
    'uber': 'Transport',
    'lyft': 'Transport',
    'gas': 'Transport',
    'rent': 'Housing',
    'mortgage': 'Housing',
    'electric': 'Utilities',
    'water': 'Utilities',
    'internet': 'Utilities',
    'salary': 'Income',
    'paycheck': 'Income',
    'interest': 'Income',
    'gym': 'Health',
    'pharmacy': 'Health',
    'movie': 'Entertainment',
    'concert': 'Entertainment'
}

def categorize(description: str) -> str:
    """Return a category based on keyword lookup; default to 'Other'."""
    desc = description.lower()
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in desc:
            return cat
    return 'Other'

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, add month period and category columns."""
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    df['Category'] = df['Description'].apply(categorize)
    return df

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction amounts per month and category."""
    summary = df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
    return summary

def plot_spending(summary: pd.DataFrame, output_file: str = 'monthly_spending.png'):
    """Create a stacked bar chart of spending (excluding income)."""
    pivot = summary.pivot(index='Month', columns='Category', values='Amount').fillna(0)
    if 'Income' in pivot.columns:
        pivot = pivot.drop(columns=['Income'])
    ax = pivot.plot(kind='bar', stacked=True, figsize=(10, 6))
    ax.set_ylabel('Amount')
    ax.set_title('Monthly Spending by Category')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def main():
    # Minimal inline sample data covering a few months
    data = [
        {'Date': '2024-01-05', 'Description': 'Supermarket purchase', 'Amount': -150.75},
        {'Date': '2024-01-10', 'Description': 'Salary for January', 'Amount': 3000.00},
        {'Date': '2024-01-12', 'Description': 'Uber ride', 'Amount': -23.40},
        {'Date': '2024-01-15', 'Description': 'Electric bill', 'Amount': -60.00},
        {'Date': '2024-02-03', 'Description': 'Restaurant dinner', 'Amount': -85.20},
        {'Date': '2024-02-10', 'Description': 'Salary for February', 'Amount': 3000.00},
        {'Date': '2024-02-14', 'Description': 'Gym membership', 'Amount': -45.00},
        {'Date': '2024-02-20', 'Description': 'Internet service', 'Amount': -55.00},
        {'Date': '2024-03-01', 'Description': 'Mortgage payment', 'Amount': -1200.00},
        {'Date': '2024-03-05', 'Description': 'Coffee at cafe', 'Amount': -12.50},
        {'Date': '2024-03-10', 'Description': 'Salary for March', 'Amount': 3000.00},
    ]
    df = pd.DataFrame(data)
    df = preprocess(df)
    summary = monthly_summary(df)
    print('Monthly Summary:')
    print(summary.to_string(index=False))
    plot_spending(summary)
    print('Spending chart saved as monthly_spending.png')

if __name__ == '__main__':
    main()
