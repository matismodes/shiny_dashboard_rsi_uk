import pandas as pd
from data import df, avg_rsi
from shiny import App, render, ui
import plotly.express as px
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget

# Data Loading and Transformation
df['Time'] = df['Time'].dt.strftime('%Y-%m-%d')
unique_USIC_with_business = df['USIC'].unique().tolist()
unique_USIC_no_business = ['-'.join(item.split('-')[:-2]) for item in unique_USIC_with_business]
unique_business_types = list(set(['-'.join(item.split('-')[-2:]) for item in unique_USIC_with_business]))
unique_business_types.sort()

unique_prices = list(df['Price'].unique())
unique_prices.sort()

barchart_years = df.Year.unique().tolist()[-4:-1]
barchart_years.sort()
barchart_years = [str(item) for item in barchart_years]


app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_panel("Dashboard", (
            ui.card(
                ui.card_header("Monthly Retail Sales Index per Category-Business"),
                ui.layout_sidebar(
                    ui.sidebar(("Options",
                                ui.input_select(
                                    "var1", "Category", choices=unique_USIC_no_business
                                ),
                                ui.input_select(
                                    "var2", "Type of Price", choices=unique_prices
                                )), bg="#f8f8f8"),
                    output_widget("line_graph"),
                ),
            ),
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header(f"Average RSI by Category - {unique_business_types[1]} ({unique_prices[0]}) > {barchart_years[0]}-{barchart_years[-1]}"),
                    output_widget("bar_chart_1")
                ),
                ui.card(
                    ui.card_header(f"Average RSI by Category - {unique_business_types[2]} ({unique_prices[0]}) > {barchart_years[0]}-{barchart_years[-1]}"),
                    output_widget("bar_chart_2")
                ),
            ),
            ui.card(
                ui.card_header(f"Average RSI by Category - {unique_business_types[0]} ({unique_prices[0]}) > {barchart_years[0]}-{barchart_years[-1]}"),
                output_widget("bar_chart_3")
            )
        )),
        title=f"Retail Sales Index (RSI) in the United Kingdom > {min(df.Time)} to {max(df.Time)}",
        id="page",
    )
)


def server(input, output, session):
    @render_widget
    def line_graph():
        df_list = []
        for i in range(len(unique_business_types)):
            USIC_sel = input.var1() + "-" + unique_business_types[i]
            df_list.append(df[(df['USIC'] == USIC_sel) & (df['Price'] == input.var2())])

        fig = go.Figure()

        for sel_df, label in zip(df_list, unique_business_types):
            fig.add_trace(go.Scatter(x = sel_df["Time"], y = sel_df['Observation'], mode = 'lines+markers', name = label))

        fig.add_shape(type="line", x0=min(df['Time']), x1=max(df['Time']), y0=100, y1=100, line=dict(color="black", width=2, dash="dash"))

        fig.update_layout(
            showlegend=True,
            title = f"Retail Sales Index (RSI) (Base Year = 100) - {input.var1()} / {input.var2()}",
            xaxis_title = "Time",
            yaxis_title = "RSI",
            colorway=px.colors.qualitative.Set1
        )

        return fig

    @render_widget
    def bar_chart_1():
        sel_df = avg_rsi[(avg_rsi['Year'].isin(barchart_years) ) & (avg_rsi['Price'] == unique_prices[0]) & (avg_rsi['USIC_business'] == unique_business_types[1])]
        fig = px.bar(sel_df, x="USIC_industry", y = "Observation", color = "Year", barmode = "group", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(
            xaxis_title = "Category",
            yaxis_title = "RSI",
            yaxis = dict(
                range = [max(min(sel_df["Observation"] - 10), 0), max(sel_df["Observation"]) + 10],
            )
        )
        return fig

    @render_widget
    def bar_chart_2():
        sel_df = avg_rsi[(avg_rsi['Year'].isin(barchart_years) ) & (avg_rsi['Price'] == unique_prices[0]) & (avg_rsi['USIC_business'] == unique_business_types[2])]
        fig = px.bar(sel_df, x="USIC_industry", y = "Observation", color = "Year", barmode = "group", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="RSI",
            yaxis=dict(
                range=[max(min(sel_df["Observation"] - 10), 0), max(sel_df["Observation"]) + 10],
            )
        )
        return fig

    @render_widget
    def bar_chart_3():
        sel_df = avg_rsi[(avg_rsi['Year'].isin(barchart_years) ) & (avg_rsi['Price'] == unique_prices[0]) & (avg_rsi['USIC_business'] == unique_business_types[0])]
        fig = px.bar(sel_df, x="USIC_industry", y = "Observation", color = "Year", barmode = "group", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="RSI",
            yaxis=dict(
                range=[max(min(sel_df["Observation"] - 10), 0), max(sel_df["Observation"]) + 10],
            )
        )
        return fig



app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
