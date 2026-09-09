# https://www.ssb.no/en/statbank/table/10725
import pandas as pd
import plotly.graph_objects as go
from utils import hsv_to_hex

def preprocess_expenses(path='data/Norway_government_expenditure.csv'):
    df = pd.read_csv(path)

    # Select only general government;drop columns that won't be used
    df = df[df['government level'] == 'General government'][['function', '2023']] # General gvt = central + local - transfers
    df.rename(columns={'2023': 'NOK'}, inplace=True)
    # df['NOK'] *= 

    # split function code and function name
    df['code'] = df['function'].str.extract(r'^(\d{2,4})')
    df['function'] = df['function'].str.replace(r'^\d{2,4}\s+', '', regex=True)

    # build parent category lookup dict
    df_lookup = df[df['code'].str.len() == 2]
    category_lookup = {
        row['code']: row['function']
        for _, row in df_lookup.iterrows()
    }
    print(category_lookup)

    # drop parent categories
    df = df[df['code'].str.len() != 2].dropna()

    # df = df.groupby('function', as_index=False)['NOK'].sum() # sum entries for all categories of government

    df['category'] = df['code'].apply(lambda x: category_lookup.get(x[:2], pd.NA))
    df = df.rename(columns={
        'category': 'source', 
        'function': 'target', 
        'NOK': 'value'
    })
    # df.sort_values(by=df['code'].astype(int), inplace=True)
    totals = df.groupby(['source'], as_index=False)['value'].sum()
    totals['target'] = totals['source']
    totals['code'] = totals['target'].apply(lambda x: df_lookup[df_lookup['function'] == x]['code'].unique()[0])
    totals['source'] = 'Total Expenses'  # New root node
    # print(totals)

    # totals
    df = pd.concat([
        totals,
        df,  
    ], ignore_index=True)
    df.sort_values(
        by='code',
        key=lambda x: x.str.len().astype(str) + x, # first by length, then lexicographically 
        inplace=True
    )
    return df

df = preprocess_expenses()
print(df)

# Sankey
print(df['source'].unique())
# exit()
labels = pd.unique(pd.concat([df['source'], df['target']])) # unique source and target labels
# print(df['source'].unique())
# selector = df['source'] == 'Total Expenses'
# total_layer = ['Total Expenses']
# category_layer = sorted(df[selector]['target'].unique())
# subcategory_layer = sorted(df[~selector]['target'].unique())
# labels = total_layer + category_layer + subcategory_layer

label_indices = {name: i for i, name in enumerate(labels)}

# print(labels)
# for i, l in enumerate(labels):
#     print(f"{i}:{l}")
# print(label_indices)
# exit()
def colormap(row):
    # if row['source'] == 'Total Expenses':
    #     # total_max = df[df['source' == 'Total Expenses']]['target_idx'].max()
    #     return hsv_to_hex(-0.1 + row['target_idx']/10, 1)
    # else:
    #     # min_idx = df[df['source_idx'] == row['source_idx']].min()
    #     # max_idx = df[df['source_idx'] == row['source_idx']].max()
    #     # variation = 0.55/10*(0.5 - (row['source_idx']-min_idx)/(max_idx-min_idx)) 
    #     return hsv_to_hex(
    #         -0.1 + row['source_idx']/10, 1
    #     )
    return hsv_to_hex(float(label_indices[row['source']])/83*10)
df['color'] = df.apply(lambda row: colormap(row), axis=1)

fig = go.Figure(data=[go.Sankey(
    arrangement='fixed',
    valueformat=".0f",
    valuesuffix="M",
    node=dict(
        pad=15,
        thickness=20,
        # line=dict(color="black", width=0.5),
        label=labels,
    ),
    link=dict(
        label=labels,
        source=df['source'].map(label_indices),
        target=df['target'].map(label_indices),
        # source=df['source_idx'],
        # target=df['target_idx'],
        value=df['value'],
        color=df['color']
    )
)])

fig.update_layout(
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
)


fig.show()