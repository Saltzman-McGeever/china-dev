
#%% Open AidData China's Global Loans and Grants Dataset, Version 1.0
import pandas as pd
clg = pd.read_excel("/Users/levisaltzman/Desktop/ChinaDev/Analysis/AidDatas_CLG_Global_Dataset_v1.0.xlsx", 
                   sheet_name="CLG-Global 1.0_Records")

clg = clg[clg['Recommended_for_Aggregates'] == 'Yes']
clg
# %%
import plotly.express as px

def create_flat_map_visualization(df, country_col='Country_of_Activity', color_scale='Greens'):

    # Count projects by country
    country_counts = df.groupby(country_col).size().reset_index(name='Project_Count')

    # Create a choropleth map showing project counts by country
    fig = px.choropleth(
        country_counts,
        locations=country_col,
        locationmode='country names',
        color='Project_Count',
        hover_name=country_col,
        hover_data={'Project_Count': True, country_col: True},
        color_continuous_scale=color_scale,
        labels={'Project_Count': 'Number of Projects'}
    )

    # Update layout with flat projection
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='rgb(150, 150, 150)',
            coastlinewidth=0.5,
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(217, 204, 178)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            showocean=True,
            oceancolor='rgb(166, 206, 227)',
            showlakes=True,
            lakecolor='rgb(166, 206, 227)'
        ),
        width=1400,
        height=900,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig
