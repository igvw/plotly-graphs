import pandas as pd

def read_norsk_demographics():
    df = pd.read_csv('data/norway_migration_background.csv', sep=';')
    for col in df.columns[1:]:
        df[col] = df[col].str.replace(' ', '').astype(int)
    df = df[df['country'] != 'Total']
    df = df[df['country'] != 'Norway']
    # 3rd gen;1st gen;2nd gen;foreign-born to 1 native parent;local-born to 1 foreign parent;foreign-born to 2 native parents
    df['total'] = df[['3rd gen', '1st gen', '2nd gen', 'foreign-born to 1 native parent', 'local-born to 1 foreign parent', 'foreign-born to 2 native parents']].sum(axis=1)
    df.sort_values(by='total', inplace=True, ascending=False)
    return df

def merged_data():
    df = read_norsk_demographics()
    df_region = pd.read_csv('data/countries_by_region.csv')[['name', 'region', 'sub-region']]
    df = pd.merge(df, df_region, left_on='country', right_on='name', how='left')
    df.dropna(inplace=True)
    df.fillna('none', inplace=True)
    return df

def melted():
    df = merged_data()
    df_melted = df.melt(
    id_vars=['sub-region', 'region', 'country'],
    value_vars=['3rd gen', '1st gen', '2nd gen', 'foreign-born to 1 native parent', 
                'local-born to 1 foreign parent', 'foreign-born to 2 native parents'],
    var_name='category',
    value_name='population'
    )
    df_melted = df_melted[['region', 'sub-region', 'country', 'category', 'population']] # reorder columns
    return df_melted

print(melted())
# print(df_melted)