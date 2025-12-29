import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_temporal_trends(df,
                          year_col='Commitment_Year',
                          amount_col='Amount_Constant_USD_2023',
                          project_col='AidData_Record_ID'):


    # Aggregate by year
    yearly_projects = df.groupby(year_col)[project_col].nunique().reset_index()
    yearly_projects.columns = ['Year', 'Project_Count']

    yearly_spending = df.groupby(year_col)[amount_col].sum().reset_index()
    yearly_spending.columns = ['Year', 'Total_Spending']

    # Convert spending to billions for readability
    yearly_spending['Total_Spending_Billions'] = yearly_spending['Total_Spending'] / 1e9

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add project count trace (YlOrRd color scheme to match map)
    fig.add_trace(
        go.Bar(
            x=yearly_projects['Year'],
            y=yearly_projects['Project_Count'],
            name='Number of Projects',
            marker_color='rgb(253, 141, 60)',
            opacity=0.8
        ),
        secondary_y=False,
    )

    # Add spending trace (Greens color scheme to match map)
    fig.add_trace(
        go.Scatter(
            x=yearly_spending['Year'],
            y=yearly_spending['Total_Spending_Billions'],
            name='Total Spending (Billions USD)',
            line=dict(color='rgb(49, 163, 84)', width=3),
            mode='lines+markers',
            marker=dict(size=8, color='rgb(35, 139, 69)')
        ),
        secondary_y=True,
    )

    # Update layout with clean, minimal styling to match maps
    fig.update_xaxes(
        title_text="Year",
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor='rgb(200, 200, 200)',
        mirror=False
    )

    fig.update_yaxes(
        title_text="Number of Projects",
        secondary_y=False,
        showgrid=True,
        gridwidth=1,
        gridcolor='rgb(240, 240, 240)',
        showline=False
    )

    fig.update_yaxes(
        title_text="Total Spending (Billions USD 2023)",
        secondary_y=True,
        showgrid=False,
        showline=False
    )

    fig.update_layout(
        hovermode='x unified',
        height=700,
        width=1400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(0, 0, 0, 0)',
            borderwidth=0
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=60, t=40, b=60),
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="rgb(80, 80, 80)"
        )
    )

    return fig

def create_flat_map_visualization(df,
                                   agg_col='AidData_Record_ID',
                                   agg_func='count',
                                   value_label='Projects',
                                   country_col='Country_of_Activity',
                                   color_scale='Greens'):
    # Perform aggregation by country
    if agg_func == 'count':
        country_agg = df.groupby(country_col).size().reset_index(name='Value')
    elif agg_func == 'nunique':
        country_agg = df.groupby(country_col)[agg_col].nunique().reset_index(name='Value')
    elif agg_func == 'sum':
        country_agg = df.groupby(country_col)[agg_col].sum().reset_index(name='Value')
    elif agg_func == 'mean':
        country_agg = df.groupby(country_col)[agg_col].mean().reset_index(name='Value')
    elif agg_func == 'median':
        country_agg = df.groupby(country_col)[agg_col].median().reset_index(name='Value')
    else:
        # For custom functions
        country_agg = df.groupby(country_col)[agg_col].agg(agg_func).reset_index(name='Value')

    # Create choropleth map
    fig = px.choropleth(
        country_agg,
        locations=country_col,
        locationmode='country names',
        color='Value',
        hover_name=country_col,
        hover_data={'Value': True, country_col: False},
        color_continuous_scale=color_scale,
        labels={'Value': value_label}
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
