
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_and_prepare_data(file_path):
    data = pd.read_excel(file_path, sheet_name='bids')
    # Filter data for IPO bids only
    ipo_data = data[data['action'] == 'IPO bid']
    return ipo_data


def filter_data(ipo_data, max_bid_amount=350):
    # Filter out bids higher than 350
    filtered_data = ipo_data[ipo_data['amount'] <= max_bid_amount]
    return filtered_data


def calculate_statistics(filtered_data):
    # Calculate basic statistics
    desc_stats = filtered_data['amount'].describe()
    total_bids = len(filtered_data)
    median_bid = filtered_data['amount'].median()
    highest_bid = filtered_data['amount'].max()
    lowest_bid = filtered_data['amount'].min()
    return desc_stats, total_bids, median_bid, highest_bid, lowest_bid


def total_bids_by_color_and_size(filtered_data):
    # Count bids by color and shoe size
    total_bids_by_color_size = filtered_data.groupby(['product_type', 'shoe_size']).size().unstack(fill_value=0)

    return total_bids_by_color_size


# calculate market clearing prices
def calculate_clearing_prices(filtered_data):
    clearing_prices = []
    for (ptype, size), group in filtered_data.groupby(['product_type', 'shoe_size']):
        sorted_bids = group.sort_values('amount', ascending=False)
        supply_limit = sorted_bids['ipo_supply'].iloc[0]
        if len(sorted_bids) >= supply_limit:
            clearing_price = sorted_bids['amount'].iloc[supply_limit - 1]
        else:
            clearing_price = sorted_bids['amount'].iloc[-1]  # all bids clear if less than supply
        clearing_prices.append({'product_type': ptype, 'shoe_size': size, 'clearing_price': clearing_price, 'supply_limit': supply_limit})
    return pd.DataFrame(clearing_prices)


def plot_demand_supply(filtered_data, color, size):
    # Filter data for specific color and shoe size
    specific_data = filtered_data[(filtered_data['product_type'] == color) & (filtered_data['shoe_size'] == size)]

    # Sort data by amount in descending order
    demand_data = specific_data.sort_values('amount', ascending=False).reset_index()
    demand_data['cumulative_bids'] = range(1, len(demand_data) + 1)

    # Get supply limit
    supply_limit = specific_data['ipo_supply'].iloc[0]

    # Create plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='cumulative_bids', y='amount', data=demand_data, label='Demand', marker='o')
    plt.axhline(y=supply_limit, color='r', linestyle='--', label='Supply = ' + str(supply_limit))
    plt.title(f'Demand and Supply Curves for {color.capitalize()} Shoes Size {size}')
    plt.xlabel('Number of Bids (cumulative)')
    plt.ylabel('Bid Amount ($)')
    plt.legend()
    plt.grid(True)
    plt.show()


def analyze_outliers(filtered_data):
    # detect outliers based on the IQR method
    Q1 = filtered_data['amount'].quantile(0.25)
    Q3 = filtered_data['amount'].quantile(0.75)
    IQR = Q3 - Q1
    outlier_condition = ((filtered_data['amount'] < (Q1 - 1.5 * IQR)) | (filtered_data['amount'] > (Q3 + 1.5 * IQR)))
    outliers = filtered_data[outlier_condition]
    return outliers


def analyze_bids_by_color_and_size(filtered_data):
    # Average bids by color and shoe size
    average_bids_by_color = filtered_data.groupby('product_type')['amount'].mean()
    average_bids_by_size = filtered_data.groupby('shoe_size')['amount'].mean()
    return average_bids_by_color, average_bids_by_size


def revenue_impact_of_supply_changes(filtered_data, supply_change):
    # Calculate initial revenue
    initial_revenue = filtered_data['amount'].sum()
    # Adjusting supply and assuming price stays constant
    adjusted_revenue = initial_revenue * (1 + supply_change)
    return initial_revenue, adjusted_revenue


def main():
    file_path = 'StockX.xlsx'

    ipo_data = load_and_prepare_data(file_path)
    filtered_data = filter_data(ipo_data)
    statistics, total_bids, median_bid, highest_bid, lowest_bid = calculate_statistics(filtered_data)

    print(f"Total Bids: {total_bids}")
    print(f"Median Bid: {median_bid:.2f}")
    print(f"Highest Bid: {highest_bid:.2f}")
    print(f"Lowest Bid: {lowest_bid:.2f}")

    clearing_prices = calculate_clearing_prices(filtered_data)
    print(f" clearing prices: \n{clearing_prices}")

    plot_demand_supply(filtered_data, 'black', 10)
    plot_demand_supply(filtered_data, 'red', 10)

    total_bids_by_color_size = total_bids_by_color_and_size(filtered_data)
    print(f"Total Bids by Color:\n{total_bids_by_color_size}\n")

    outliers = analyze_outliers(filtered_data)
    print(f"Number of Outliers: {len(outliers)}")

    avg_bids_color, avg_bids_size = analyze_bids_by_color_and_size(filtered_data)
    print(f"Average Bids by Color:\n{avg_bids_color}\n")
    print(f"Average Bids by Shoe Size:\n{avg_bids_size}\n")

    initial_revenue, increased_revenue = revenue_impact_of_supply_changes(filtered_data, 0.10)  # 10% increase
    _, decreased_revenue = revenue_impact_of_supply_changes(filtered_data, -0.10)  # 10% decrease

    print(f"Initial Revenue: ${initial_revenue:.2f}")
    print(f"Revenue with 10% Increased Supply: ${increased_revenue:.2f}")
    print(f"Revenue with 10% Decreased Supply: ${decreased_revenue:.2f}")


if __name__ == "__main__":
    main()


