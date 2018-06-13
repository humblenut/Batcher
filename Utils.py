import numpy as np


def beans_to_roast(df):
    df = remove_empty_beans(df)
    df = remove_instock_beans(df)
    df = remove_green_beans(df)
    df = add_green_lb_column(df, 1.16)
    df = add_green_gm_column(df, 1.16)
    df = round_bean_nearest_gram(df)
    return df


def df_labels(df):
    df = remove_empty_beans(df)
    df = remove_instock_beans(df)
    df = remove_green_beans(df)
    return df


def beans_remove_inventory(df):
    df = remove_empty_beans(df)
    df = remove_instock_beans(df)
    df = add_green_lb_column(df, 1.16)
    return df


# removes empty bean row
# removes rows with empty order id
def remove_empty_beans(df):
    return df[df['Order ID'].notnull()]

# removes instock beans
def remove_instock_beans(df):
    return df[df.IS != 'x']


def remove_green_beans(df):
    return df[df.Roast != 'Green']

# calculates green weight for each bean row.
def add_green_lb_column(df, shrink_rate):
    df['lb'] = (df['Bag Size (oz)'] / 16) * df['Qty'] * np.where(df.Roast == 'Green', 1, shrink_rate)
    return df


def add_green_gm_column(df, shrink_rate):
    df['gm'] = (df['Bag Size (oz)'] * 28.3495) * df['Qty'] * shrink_rate
    return df


def round_bean_nearest_gram(df):
    df.gm = df.gm.round()
    return df


def rename_labels(df):
    return df.rename({12: '12oz', 16: '1lb', 32: '2lb', 80: '5lb'}, axis='columns')
