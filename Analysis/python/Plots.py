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

    # Add spending trace (Steel Blue)
    fig.add_trace(
        go.Scatter(
            x=yearly_spending['Year'],
            y=yearly_spending['Total_Spending_Billions'],
            name='Total Spending (Billions USD)',
            line=dict(color='rgb(70, 130, 180)', width=3),
            mode='lines+markers',
            marker=dict(size=8, color='rgb(54, 100, 139)')
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
        autosize=True,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(0, 0, 0, 0)',
            borderwidth=0,
            font=dict(size=10)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=30, b=50),
        font=dict(
            family="Arial, sans-serif",
            size=11,
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

    # Customize hover template to use ": " instead of "="
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' + value_label + ': %{z}<extra></extra>'
    )

    # Update layout with flat projection (transparent backgrounds, centered on China)
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='rgb(150, 150, 150)',
            coastlinewidth=0.5,
            projection_type='natural earth',
            center=dict(lon=53),
            showland=True,
            landcolor='rgb(230, 230, 230)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            showocean=True,
            oceancolor='rgba(255, 255, 255, 0)',
            showlakes=True,
            lakecolor='rgba(255, 255, 255, 0)',
            bgcolor='rgba(255, 255, 255, 0)'
        ),
        width=1000,
        height=600,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        coloraxis_colorbar=dict(
            len=0.9,
            thickness=15,
            tickfont=dict(size=10),
            y=0.5,
            yanchor='middle'
        )
    )

    return fig


def create_public_opinion_map(df,
                               value_col='net_positive_adj',
                               country_col='country',
                               value_label='Net Positive Opinion'):
    """
    Create a choropleth map for GPOC public opinion data.
    Uses a diverging color scale: blue for negative, green for positive.
    """
    # Get unique country-level data (take mean if multiple entries per country)
    country_data = df.groupby(country_col)[value_col].mean().reset_index()
    country_data.columns = [country_col, 'Value']

    # Define custom diverging colorscale: blue (negative) -> white (neutral) -> green (positive)
    diverging_colorscale = [
        [0.0, 'rgb(33, 102, 172)'],      # Dark blue (most negative)
        [0.25, 'rgb(103, 169, 207)'],    # Light blue
        [0.5, 'rgb(247, 247, 247)'],     # White/neutral (zero)
        [0.75, 'rgb(120, 198, 121)'],    # Light green
        [1.0, 'rgb(35, 139, 69)']        # Dark green (most positive)
    ]

    # Create choropleth map with diverging color scale centered at 0
    fig = px.choropleth(
        country_data,
        locations=country_col,
        locationmode='country names',
        color='Value',
        hover_name=country_col,
        hover_data={'Value': ':.1f', country_col: False},
        color_continuous_scale=diverging_colorscale,
        color_continuous_midpoint=0,
        labels={'Value': value_label}
    )

    # Customize hover template
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' + value_label + ': %{z:.1f}<extra></extra>'
    )

    # Update layout with flat projection (transparent ocean, centered on Middle East)
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='rgb(150, 150, 150)',
            coastlinewidth=0.5,
            projection_type='natural earth',
            center=dict(lon=53),
            showland=True,
            landcolor='rgb(230, 230, 230)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            showocean=True,
            oceancolor='rgba(255, 255, 255, 0)',
            showlakes=True,
            lakecolor='rgba(255, 255, 255, 0)',
            bgcolor='rgba(255, 255, 255, 0)'
        ),
        coloraxis_colorbar=dict(
            title=value_label,
            tickvals=[-50, -25, 0, 25, 50],
            ticktext=['-50 (Negative)', '-25', '0 (Neutral)', '+25', '+50 (Positive)'],
            len=0.9,
            thickness=15,
            tickfont=dict(size=10),
            title_font=dict(size=11),
            y=0.5,
            yanchor='middle'
        ),
        width=1000,
        height=600,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)'
    )

    return fig
