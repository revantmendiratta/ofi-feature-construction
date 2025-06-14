
import pandas as pd

try:
    df = pd.read_csv('first_25000_rows.csv')
    df['ts_event'] = pd.to_datetime(df['ts_event'], utc=True)
    df = df.set_index('ts_event')

    def calculate_ofi_level(df, level):
        bid_price = f'bid_px_{level:02d}'
        ask_price = f'ask_px_{level:02d}'
        bid_size = f'bid_sz_{level:02d}'
        ask_size = f'ask_sz_{level:02d}'

        if not all(col in df.columns for col in [bid_price, ask_price, bid_size, ask_size]):
            return pd.Series(0, index=df.index)

        d_bid = df[bid_size].diff()
        d_ask = df[ask_size].diff()

        d_bid[df[bid_price] > df[bid_price].shift(1)] = df[bid_size]
        d_bid[df[bid_price] < df[bid_price].shift(1)] = -df[bid_size]

        d_ask[df[ask_price] > df[ask_price].shift(1)] = -df[ask_size]
        d_ask[df[ask_price] < df[ask_price].shift(1)] = df[ask_size]

        return d_bid - d_ask

    df['best_level_ofi'] = calculate_ofi_level(df, 0)

    ofi_levels = [calculate_ofi_level(df, i) for i in range(5)]
    df['multi_level_ofi'] = sum(ofi_levels)

    df['integrated_ofi_1s'] = df['best_level_ofi'].rolling('1s').sum()
    df['cross_asset_ofi'] = float('NaN')

    result = df[['best_level_ofi', 'multi_level_ofi', 'integrated_ofi_1s', 'cross_asset_ofi']]
    result.to_csv("ofi_features.csv")

    print("OFI features have been calculated and saved to 'ofi_features.csv'.")

except FileNotFoundError:
    print("Error: 'first_25000_rows.csv' not found.")
except Exception as e:
    print(f"An error occurred: {e}")
