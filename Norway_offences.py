import pandas as pd
import plotly.express as px
df = pd.read_csv('data/Norway_offence_by_citizenship09421.csv')
df.columns
df['offence'] = df['offence'].str.lstrip('¬ ')

for col in df.columns[2:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# df['Total'] = df[df.columns[2:]].sum(axis=1)
print(df['offence'].unique())

# print(df)
df = df[df['offence'] != 'All groups of offences']
df = df[df['citizenship'] != 'Total']
df = df[df['citizenship'] != 'All countries']
df = df[df['offence'] == 'Sexual offences']




df = df.melt(
    id_vars=["offence", "citizenship"],
    var_name="Year",
    value_name="crimes"
)

# print(df)
# Ensure Year is treated as numeric
df["Year"] = df["Year"].astype(int)

# # Plot
fig = px.line(
    df,
    x="Year",
    y="crimes",
    color="citizenship",
    line_dash="offence",  # Optional: different dash style per citrus type
    hover_name="citizenship",
    title="Citrus Exports by Country and Type",
    log_y=True,
)

fig.update_layout(
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
)

fig.show()