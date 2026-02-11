import pandas as pd
import numpy as np
import argparse
from datetime import datetime, timedelta
import uuid
import random

def generate_sales_data(rows, output_file, start_date_str, randomness):
    """
    Generates a dummy CSV file for the Foreat platform.
    """
    items = [
        ('Pizza', 12.0),
        ('Burger', 8.0),
        ('Salad', 7.0),
        ('Soda', 2.0)
    ]
    locations = ['Loc_A', 'Loc_B', 'Loc_C', 'Loc_D']
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    data = []

    print(f"Generating {rows} rows of data...")

    for i in range(rows):
        # Calculate a date
        date_offset = random.randint(0, 365)
        current_date = start_date + timedelta(days=date_offset)
        
        item_name, base_price = random.choice(items)
        
        # Apply randomness factor to quantity and price
        # randomness=0 means strict defaults, randomness=1.0 means high variance
        qty = max(1, int(random.gauss(3, 1 + randomness)))
        price_variation = random.uniform(1 - (randomness * 0.2), 1 + (randomness * 0.2))
        total_price = round(base_price * qty * price_variation, 2)
        
        data.append({
            'T-Date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Order_ID': str(uuid.uuid4())[:8].upper(),
            'Category': item_name,
            'Price': total_price,
            'Shop_ID': random.choice(locations),
            'Units': qty
        })

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Successfully saved {rows} rows to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate dummy sales CSV for Foreat.')
    parser.add_argument('--rows', type=int, default=1000, help='Number of rows to generate')
    parser.add_argument('--output', type=str, default='dummy_sales_upload.csv', help='Output filename')
    parser.add_argument('--start-date', type=str, default='2025-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--randomness', type=float, default=0.5, help='Randomness factor (0.0 to 1.0)')

    args = parser.parse_args()
    
    generate_sales_data(args.rows, args.output, args.start_date, args.randomness)
