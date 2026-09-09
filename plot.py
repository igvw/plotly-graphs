import plotly.express as px
import plotly.io as pio
import pandas as pd
import math
import colorsys
from utils import translate
import worldbank
import Norway_migrants

def minimal_scatter(df, html_path=None, hover_data=None, hover_name=None):
    fig = px.scatter(
        df, 
        x=df.columns[0], 
        y=df.columns[1], 
        size=df.columns[2], 
        color=df.columns[3],
        hover_name=hover_name, 
        hover_data=hover_data,
        log_x=True
    )
    fig.update_traces(
        mode='markers', 
        marker=dict(
            sizemode='area', 
            sizeref=2.*max(df[df.columns[2]])/(100**2), 
            showscale=False, 
            line=dict(width=0),
        )
    )

    fig.update_layout(
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        showlegend=False,  # Hide legend if not needed
        margin=dict(l=0, r=0, t=0, b=0),  # Remove padding/margins
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    fig.update_coloraxes(showscale=False)

    fig.show()
    if html_path:
        pio.write_html(fig, html_path, full_html=True)


def world_bank_data(lang='no'):
    indicators = ['NY.GDP.PCAP.CD', 'SP.DYN.TFRT.IN', 'SP.POP.TOTL','SP.DYN.LE00.IN']
    df = worldbank.get_indicators(countries=['all'], indicators=indicators, years=['2022'])
    df = df[df['iso2code'].isin(open('data/countries_only_filter.csv').read().strip().split(','))] # filter for only countries, not regions
    df = df[indicators + ['country']] # reorder columns and remove useless ones
    # make columns more readable
    print(df)
    columns = translate(['GDP Per Capita', 'Fertility Rate', 'Population', 'Life Expectancy'], lang)
    df.rename(columns={"NY.GDP.PCAP.CD":columns[0], "SP.DYN.TFRT.IN":columns[1], 'SP.POP.TOTL':columns[2], 'SP.DYN.LE00.IN': columns[3]}, inplace=True)
    df['country'] = df['country'].apply(lambda x: translate(x, lang))
    minimal_scatter(
        df, 
        html_path='outputs/worldbank.html', 
        hover_data={
            columns[0]:':.2e', # customize hover for column of y attribute
            columns[1]:':.2f', # add other column, customized formatting
            columns[2]:':.2e',
            columns[3]:':.2f'
        }, 
        hover_name='country'
    )

def styled_suburst(df, path, values, html_path=None, color_map=None):
    fig = px.sunburst(
    df,
    path=path,
    values=values,
    maxdepth=3,
    # sort=False
    )
    all_labels = fig.data[0].labels
    fig.update_traces(
        insidetextorientation='radial',
        marker=dict(
            colors=[color_map.get(label, 'beige') for label in all_labels]
        ),
        opacity=1
    )
    fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
    fig.update_layout(
        showlegend=False,  # Hide legend if not needed
        template='plotly_dark',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    # print(fig.data[0])
    fig.show()

    pio.write_html(fig, html_path, full_html=True)

# with open('data/dictionaries/ordbok.csv') as f:
#     ordbok = {
#         line.split(';')[0]: line.split(';')[1].strip()
#         for line in f.readlines()
#     }

# def translate(key, language='no'):
#     assert language in ['en', 'no']
#     if language == 'no':
#         translation_dict = ordbok
#     elif language == 'en':
#         return key
#     if isinstance(key, list):
#         for k in key:
#             assert k in translation_dict, key
#         return [translation_dict[k] for k in key]
#     elif isinstance(key, str):
#         assert key in ordbok, key
#         return translation_dict[key]
    
    
def norway_migration_sunburst(language='no'):
    '''
        Make a sunburst with custom color map

        None of the location categories are accessed directly in order to make the graph multilingual,
        look at the index in the location_categories list out the df accesses
    '''
    # some additional data prep and translation
    df = Norway_migrants.melted()
    df.rename(columns=lambda col: translate(col, language))
    cols = list(df.columns)
    location_categories = list(cols[:-1])
    values = cols[-1]
    categories = translate( # I could just use df[cols[4]].unique(), but it does not preserve the order I want
        [
            '1st gen',
            '2nd gen',
            '3rd gen',
            'foreign-born to 2 native parents',
            'local-born to 1 foreign parent',
            'foreign-born to 1 native parent',
        ],
        'no'
    )
    regions = translate([
            'Oceania',
            'Asia',
            'Africa',
            'Europe',
            'Americas'
        ],
        'no'
    )

    # completely natural language agnostic code
    for col in cols[:-1]:
        df[col] = df[col].apply(lambda x: translate(x, 'no'))

    region_hues = {
        k: (i*25+150)/360 # these parameters tweak the hue of the continent
        for i, k in enumerate(regions)
    }
    print(df)

    def hsv_to_hex(h, s=0.7, v=0.7):
        """Convert HSV values to HEX."""
        rgb = colorsys.hsv_to_rgb(h, s, v)  # Normalize H to [0,1]
        return f"#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}"

    def hierarchy_norm(key, row):
        '''Normalize the value of an index with regards to the parent category'''
        lookup = location_categories[:-1]
        assert key in lookup[1:]
        i = lookup.index(key)
        norm = (
            df[df[lookup[i]]==row[lookup[i]]][values].sum()/ # sum of location category (e.g. Australia)
            df[df[lookup[i-1]]==row[lookup[i-1]]][values].sum() # sum of location parent category (e.g. Oceania)
            ) 
        return norm 

    '''
        The color map derives hsv values for different values of the sunburst
        hue is based on region/continent
        saturation goes from high to low over {region, subregion, country}
        brightness is dependent on the proportion between the parent and child categories
        migration_category is custom, but within the same scheme
    '''
    color_map =  {
        k: hsv_to_hex( # region
            v,
            0.8,
            0.8,
        )
        for k, v in region_hues.items()
    } | { # subregion; a bit hacky, computes multiple times
        row[cols[1]]: hsv_to_hex(
            region_hues.get(row[cols[0]],0), # Hue based on region
            0.74,   # gradient of saturations for each layer of sunburst
            hierarchy_norm(cols[1], row)*0.7+0.3,  # Brightness based on proportion of subregion in region
        )
        for _, row in df.iterrows()
    } | { # country
        row[cols[2]]: hsv_to_hex(
            region_hues.get(row[cols[0]],0),
            0.68,
            hierarchy_norm(cols[2], row)*0.6+0.4,
        )
        for _, row in df.iterrows()
    } | {
        k : hsv_to_hex((i*20+150)/360) # Category hues
        for i, k in  enumerate(categories)
    }

    styled_suburst(
        df, 
        location_categories, 
        values, 
        html_path='outputs/norway_migration.html', 
        color_map=color_map
    )

world_bank_data()
# norway_migration_sunburst()