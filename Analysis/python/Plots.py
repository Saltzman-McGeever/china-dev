import pandas as pd
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
                                   color_scale='Greens',
                                   zmax=None,
                                   outlier_countries=None,
                                   is_currency=True):
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

    # Build choropleth kwargs, optionally capping the color scale
    choropleth_kwargs = dict(
        locations=country_col,
        locationmode='country names',
        color='Value',
        hover_name=country_col,
        hover_data={'Value': True, country_col: False},
        color_continuous_scale=color_scale,
        labels={'Value': value_label}
    )
    if zmax is not None:
        choropleth_kwargs['range_color'] = [0, zmax]

    # Exclude outlier countries from the main choropleth so they can be rendered separately
    main_agg = country_agg[~country_agg[country_col].isin(outlier_countries.keys())].copy() \
        if outlier_countries else country_agg.copy()

    # Pre-format values as B/M units for hover tooltips
    def _fmt(v):
        if not is_currency:
            return f'{v:,.0f}'
        if v >= 1e9:
            return f'${v / 1e9:.2f}B'
        elif v >= 1e6:
            return f'${v / 1e6:.2f}M'
        else:
            return f'${v:,.2f}'

    main_agg['_fmt'] = main_agg['Value'].apply(_fmt)
    choropleth_kwargs['custom_data'] = ['_fmt']

    # Create choropleth map
    fig = px.choropleth(main_agg, **choropleth_kwargs)

    # Customize hover template using pre-formatted B/M value
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' + value_label + ': %{customdata[0]}<extra></extra>'
    )

    # Update layout with enhanced visual styling
    fig.update_layout(
        geo=dict(
            showframe=True,
            framecolor='rgb(100, 100, 100)',
            framewidth=1.5,
            showcoastlines=True,
            coastlinecolor='rgb(120, 120, 120)',
            coastlinewidth=0.8,
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(242, 242, 242)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            countrywidth=1,
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            bgcolor='rgba(255, 255, 255, 0)'
        ),
        autosize=True,
        height=500,
        showlegend=False,
        margin=dict(l=0, r=100, t=10, b=10),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        coloraxis_colorbar=dict(
            len=0.8,
            thickness=15,
            tickfont=dict(size=10),
            y=0.5,
            yanchor='middle',
            x=1.0,
            xanchor='left'
        )
    )

    # Render outlier countries as a darker green than the scale maximum, with a text label
    OUTLIER_GREEN = 'rgb(0, 35, 14)'  # darker than Plotly Greens scale max (~rgb(0,68,27))
    if outlier_countries:
        for country_name, _ in outlier_countries.items():
            country_rows = country_agg[country_agg[country_col] == country_name]
            if not country_rows.empty:
                actual_value = country_rows['Value'].values[0]
                if not is_currency:
                    value_str = f'{actual_value:,.0f}'
                elif actual_value >= 1e9:
                    value_str = f'${actual_value / 1e9:.2f}B'
                elif actual_value >= 1e6:
                    value_str = f'${actual_value / 1e6:.2f}M'
                else:
                    value_str = f'${actual_value:,.2f}'

                # Solid dark-green fill for the outlier country
                fig.add_trace(go.Choropleth(
                    locations=[country_name],
                    locationmode='country names',
                    z=[1],
                    colorscale=[[0, OUTLIER_GREEN], [1, OUTLIER_GREEN]],
                    showscale=False,
                    hovertemplate=(
                        f'<b>{country_name}</b><br>'
                        f'{value_label}: {value_str}<br>'
                        f'<i>Outlier — exceeds color scale</i><extra></extra>'
                    ),
                    showlegend=False
                ))


    return fig


def create_public_opinion_map(df,
                               value_col='net_positive_adj',
                               country_col='country',
                               year_col='year',
                               year=None,
                               value_label=None):
    """
    Create a choropleth map for GPOC public opinion data.
    Uses a diverging color scale: red for negative, green for positive.

    Parameters:
    - year: Optional year to filter data. If None, averages across all years.
    """
    # Filter by year if specified
    if year is not None:
        # For each country, use its latest available year up to the requested year
        def get_latest_opinion(country_df):
            # Filter to years <= requested year
            country_df = country_df[country_df[year_col] <= year]

            if len(country_df) == 0:
                return None

            # Find latest year for this country
            latest_year = country_df[year_col].max()
            latest_opinion = country_df[country_df[year_col] == latest_year][value_col].mean()

            return latest_opinion

        # Apply to each country
        country_data = df.groupby(country_col).apply(get_latest_opinion).reset_index()
        country_data.columns = [country_col, 'Value']

        # Remove countries with no data
        country_data = country_data[country_data['Value'].notna()]

        print(f"Showing public opinion (using latest year ≤ {year} for each country)")
        if value_label is None:
            value_label = f'Net Positive Opinion (≤ {year})'
    else:
        # Get country-level data (take mean if multiple entries per country)
        country_data = df.groupby(country_col)[value_col].mean().reset_index()
        country_data.columns = [country_col, 'Value']

        print("Showing average public opinion across all years")
        if value_label is None:
            value_label = 'Net Positive Opinion (Average)'

    # Define custom diverging colorscale: red (negative) -> white (neutral) -> green (positive)
    diverging_colorscale = [
        [0.0, 'rgb(178, 34, 34)'],       # Dark red (most negative)
        [0.25, 'rgb(220, 130, 130)'],    # Light red
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
        hovertemplate='<b>%{hovertext}</b><br>' +
                      value_label + ': %{z:.1f}<extra></extra>'
    )

    # Update layout with enhanced visual styling and title
    fig.update_layout(
        title=dict(
            text=value_label,
            font=dict(size=14, color='rgb(80, 80, 80)'),
            x=0.5,
            xanchor='center',
            y=0.98,
            yanchor='top'
        ),
        geo=dict(
            showframe=True,
            framecolor='rgb(100, 100, 100)',
            framewidth=1.5,
            showcoastlines=True,
            coastlinecolor='rgb(120, 120, 120)',
            coastlinewidth=0.8,
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(242, 242, 242)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            countrywidth=1,
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            bgcolor='rgba(255, 255, 255, 0)'
        ),
        coloraxis_colorbar=dict(
            title=value_label,
            tickvals=[-50, -25, 0, 25, 50],
            ticktext=['-50 (Negative)', '-25', '0 (Neutral)', '+25', '+50 (Positive)'],
            len=0.8,
            thickness=15,
            tickfont=dict(size=10),
            title_font=dict(size=11),
            y=0.5,
            yanchor='middle',
            x=1.0,
            xanchor='left'
        ),
        autosize=True,
        height=500,
        showlegend=False,
        margin=dict(l=0, r=100, t=40, b=10),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)'
    )

    return fig


def create_public_opinion_change_map(df,
                                      start_year=None,
                                      end_year=None,
                                      value_col='net_positive_adj',
                                      country_col='country',
                                      year_col='year',
                                      value_label=None):
    """
    Create a choropleth map showing the change in public opinion over time.
    Uses a diverging color scale: red for negative change, green for positive change.
    Each country shows change from its earliest to latest available year.
    Optional start_year and end_year parameters can constrain the time window.
    """
    # Filter to specified year range if provided
    if start_year is not None:
        df = df[df[year_col] >= start_year]
    if end_year is not None:
        df = df[df[year_col] <= end_year]

    # For each country, find its earliest and latest year and calculate change
    def calculate_country_change(country_df):
        # Get all years for this country
        country_years = country_df[year_col].unique()

        # Find earliest and latest years
        earliest_year = country_years.min()
        latest_year = country_years.max()

        # Get opinion values for those years
        earliest_opinion = country_df[country_df[year_col] == earliest_year][value_col].mean()
        latest_opinion = country_df[country_df[year_col] == latest_year][value_col].mean()

        return pd.Series({
            'Earliest_Year': earliest_year,
            'Latest_Year': latest_year,
            'Start_Opinion': earliest_opinion,
            'End_Opinion': latest_opinion,
            'Change': latest_opinion - earliest_opinion
        })

    # Apply to each country
    change_data = df.groupby(country_col).apply(calculate_country_change).reset_index()

    # Print summary of years used
    year_range = f"{int(change_data['Earliest_Year'].min())}-{int(change_data['Latest_Year'].max())}"
    print(f"Showing change in public opinion (earliest to latest year per country)")
    print(f"Overall year range: {year_range}")

    # Set value_label and title
    if value_label is None:
        value_label = 'Change in Opinion'
    map_title = f'{value_label} (Country-Specific Years)'

    # Define custom diverging colorscale: red (negative change) -> white (no change) -> green (positive change)
    diverging_colorscale = [
        [0.0, 'rgb(178, 34, 34)'],       # Dark red (most negative)
        [0.25, 'rgb(220, 130, 130)'],    # Light red
        [0.5, 'rgb(247, 247, 247)'],     # White/neutral (zero)
        [0.75, 'rgb(120, 198, 121)'],    # Light green
        [1.0, 'rgb(35, 139, 69)']        # Dark green (most positive)
    ]

    # Create choropleth map with diverging color scale centered at 0
    fig = px.choropleth(
        change_data,
        locations=country_col,
        locationmode='country names',
        color='Change',
        hover_name=country_col,
        hover_data={
            'Change': ':.1f',
            'Start_Opinion': ':.1f',
            'End_Opinion': ':.1f',
            'Earliest_Year': True,
            'Latest_Year': True,
            country_col: False
        },
        color_continuous_scale=diverging_colorscale,
        color_continuous_midpoint=0,
        labels={
            'Change': value_label,
            'Start_Opinion': 'Start Opinion',
            'End_Opinion': 'End Opinion',
            'Earliest_Year': 'Start Year',
            'Latest_Year': 'End Year'
        }
    )

    # Customize hover template to show country-specific years and values
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' +
                      'Start Year: %{customdata[3]:.0f}<br>' +
                      'Start Opinion: %{customdata[1]:.1f}<br>' +
                      'End Year: %{customdata[4]:.0f}<br>' +
                      'End Opinion: %{customdata[2]:.1f}<br>' +
                      'Change: %{customdata[0]:.1f}<extra></extra>'
    )

    # Update layout with enhanced visual styling and title
    fig.update_layout(
        title=dict(
            text=map_title,
            font=dict(size=14, color='rgb(80, 80, 80)'),
            x=0.5,
            xanchor='center',
            y=0.98,
            yanchor='top'
        ),
        geo=dict(
            showframe=True,
            framecolor='rgb(100, 100, 100)',
            framewidth=1.5,
            showcoastlines=True,
            coastlinecolor='rgb(120, 120, 120)',
            coastlinewidth=0.8,
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(242, 242, 242)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            countrywidth=1,
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            bgcolor='rgba(255, 255, 255, 0)'
        ),
        coloraxis_colorbar=dict(
            title=value_label,
            len=0.8,
            thickness=15,
            tickfont=dict(size=10),
            title_font=dict(size=11),
            y=0.5,
            yanchor='middle',
            x=1.0,
            xanchor='left'
        ),
        autosize=True,
        height=500,
        showlegend=False,
        margin=dict(l=0, r=100, t=40, b=10),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)'
    )

    return fig
