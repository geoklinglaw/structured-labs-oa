from preswald import text, plotly, connect, get_df, table, separator, playground, slider, query, sidebar
import pandas as pd
import plotly.express as px
import preswald as pw
import matplotlib.pyplot as plt


"""
Data cleaning stuff:
Issues with data: 
1/18/2024 - LAPD is facing issues with posting the Crime data
(0°, 0°) = invalid/missing coordinates
possible errors: typo? null? types? 
freq gaps from weekly to biweekly

looking at the data,
- crm cd 3 / 4 is alm entirely empty
- crm cd 2 has vvvvv few data points
- weird data point, not too sure of the metadata like whats X in M and F? and all the random descents
"""


def clean_data(df):
    # print("in clean data")
    df = df[~((df['LAT'] == 0.0) & (df['LON'] == 0.0))]
    threshold = 0.9 # rm columns that have > threshold empty
    df = df.loc[:, df.isnull().mean() < threshold]

    return df


def load_data():
    try:
        connect()
        df = get_df('crime_csv')
        return clean_data(df)
    except Exception as e:
        text(f"Error retrieving data: {e}")
        return pd.DataFrame()


def render_ui(df):
    text("## Explore crimes happening in Los Angeles from 2020 to 2025 ")
    show_victim_distribution(df)
    separator()


def show_victim_distribution(df):
    df_cleaned = df.dropna(subset=["Vict Sex", "Vict Descent"])
    df_filtered = df_cleaned[df_cleaned["Vict Sex"].isin(["M", "F"])]

    def show_victim_histogram(df):
        fig = px.histogram(
            df,
            x="Vict Sex",             
            color="Vict Descent",      
            barmode="group",           
            labels={"Vict Sex": "Victim Sex", "count": "Number of Crimes"}
        )
        plotly(fig)

    def show_victim_sex_distribution(df):
        df = df[df['Vict Sex'].notna() & (df['Vict Sex'].str.strip() != '')]
        fig = px.pie(df, names='Vict Sex', title='Victim Gender Distribution')
        plotly(fig, size=0.4)

    def show_victim_descent_distribution(df):
        df = df[df['Vict Descent'].notna() & (df['Vict Descent'].str.strip() != '')]
        top_descent = df['Vict Descent'].value_counts().nlargest(10).reset_index()
        top_descent.columns = ['Descent', 'Count']
        fig = px.bar(top_descent, x='Descent', y='Count', title='Victim Descent Breakdown')
        plotly(fig, size=0.4)

    text("### Number of Crimes by Victim Sex and Descent")
    show_victim_histogram(df_filtered)

    text("#### For individual distribution...")
    show_victim_sex_distribution(df_filtered)
    show_victim_descent_distribution(df_filtered)

def show_partial_data_table():
    connect()

    text("## Show top rows based on your selection")
    text("Please wait around 5s for number of rows in table to reflect slider change")

    value = slider(
        label="Rows to Display",
        min_val=1,
        max_val=100,
        step=10,
        default=20
    )

    # duckdb spaces must be "" not backtick
    sql = f"""
        SELECT 
            "AREA NAME", 
            "Vict Age", 
            "Vict Sex", 
            "Vict Descent", 
            "Crm Cd Desc", 
            "Status Desc"
        FROM crime_csv
        WHERE 
            "Vict Age" > 0 
            AND "Vict Sex" IN ('M', 'F') 
            AND "Vict Descent" IS NOT NULL 
            AND TRIM("Vict Descent") != ''
        LIMIT 100
    """

    try:
        full_df = query(sql, 'crime_csv')     
        partial_df = full_df.head(value)      
        table(partial_df)
    except Exception as e:
        text(f"Error retrieving data: {e}")

df = load_data()
cleaned_df = clean_data(df)
sidebar(defaultopen=True)
render_ui(cleaned_df)
show_partial_data_table()





