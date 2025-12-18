
#%% Open AidData China's Global Loans and Grants Dataset, Version 1.0
import pandas as pd
clg = pd.read_excel("/Users/levisaltzman/Desktop/ChinaDev/AidDatas_CLG_Global_Dataset_v1.0.xlsx", 
                   sheet_name="CLG-Global 1.0_Records")

clg = clg[clg['Recommended_for_Aggregates'] == 'Yes']
clg
# %%
import plotly.express as px

# Count projects by country
country_counts = clg.groupby('Country_of_Activity').size().reset_index(name='Project_Count')

# Create a choropleth map showing project counts by country
fig = px.choropleth(country_counts,
                    locations='Country_of_Activity',
                    locationmode='country names',
                    color='Project_Count',
                    hover_name='Country_of_Activity',
                    hover_data={'Project_Count': True, 'Country_of_Activity': True},
                    color_continuous_scale='YlOrRd',
                    title='Chinese Development Projects by Country',
                    labels={'Project_Count': 'Number of Projects'})

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth'
    ),
    height=600
)

fig.show()
# %%
