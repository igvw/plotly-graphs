import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from utils import translate

def add_trace(fig, x, y, values, name, marker_color, lang, textposition='auto'):
    # print(text)
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        name=name,
        text=x if name==translate('Females', lang) else None,
        marker=dict(
            color='black',
            line=dict(width=0),#, color='black')  # Removes the border
        ),
        customdata=values,
        hovertemplate = f"{name}: %{{y:,}}<br>{translate('Total', lang)}: %{{customdata:,}}<extra></extra>", # ' ' + name.split()[0]
        # hovertemplate = f'{text}: %{y}<extra></extra>',
        # hovertext=text,
        marker_color=marker_color,
        textposition=textposition,
        textangle=90,
        width=0.8,
        textfont={'color': 'white'}
        # outsidetextfont={'size': 12}
    ))
    print(fig.data[0].hovertemplate)

def pre_process():
    df = pd.read_csv('data/Norway_naturalizations.csv')

    df = df[['Gender', 'Country', 'Total']]

    # sort and rearrange
    df = df.groupby(['Country', 'Gender'])['Total'].sum().unstack('Gender').reset_index(['Country'])
    df['gender_diff'] = df['Females'] - df['Males']
    df['Total'] = df['Females'] + df['Males']
    df.sort_values(by='gender_diff', inplace=True)

    # filter bad values
    df = df[df['Country'] != 'Total']
    df = df[df['Total'] > 500]


    # print(df)
    # print(df.columns)

    df['gender_min'] = df[['Females', 'Males']].min(axis=1)
    df['femdiff'] = df['gender_diff'].clip(lower=0)
    df['malediff'] = df['gender_diff'].clip(upper=0)
    print(df)

    return df


def plot_natrualizations(df, html_path=None, lang='en'):
    fig = go.Figure()
    df['Country'] = df['Country'].apply(lambda x: translate(x, lang))

    categories = translate(['Excess Females', 'Excess Males', 'Males', 'Females'], lang)
    add_trace(fig, df['Country'], df['femdiff'], df['Females'], categories[0], 'salmon', lang)
    add_trace(fig, df['Country'], df['malediff'], df['Males'], categories[1], 'teal', lang)
    add_trace(fig, df['Country'], -df['gender_min'], df['Males'], categories[2], 'navy', lang)
    add_trace(fig, df['Country'], df['gender_min'], df['Females'], categories[3], 'maroon', lang)

    fig.update_layout(
        # title='Population by Gender (Diverging Chart)',
        barmode='relative',
        xaxis=dict(
            # title='Population',
            visible=False, showgrid=False, zeroline=False,
        ),
        yaxis=dict(
            # title='Population',
            # titlefont=dict(color='green'),
            tickfont=dict(color='white'),
            gridcolor='dimgray',
            zerolinecolor='gray',
        ),
        bargap=0.01,
        uniformtext=dict(minsize=12, mode='show'),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        showlegend=False,  # Hide legend if not needed

    )

    if html_path:
        pio.write_html(fig, html_path, full_html=True)

    fig.show()

df = pre_process()
plot_natrualizations(df, 'outputs/norway_naturalizations.html')