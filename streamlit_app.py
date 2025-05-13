import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session
import requests


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# Input for the name on the smoothie order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

connection_parameters = {
    "account": "PNBFAXK-GQB48216",
    "user": "chaitanya99",
    "password": "u4eSS5F63:d8QL_",
    "role": "SYSADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "PUBLIC"
}
session = Session.builder.configs(connection_parameters).create()

# Fetch available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

# Create a multiselect to choose ingredients (up to 5 ingredients)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=[row['FRUIT_NAME'] for row in my_dataframe.collect()],
    max_selections=5
)

# Check if the user has selected any ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Create a comma-separated list of chosen ingredients
    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+''
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    # Display the chosen ingredients
    st.write("Your chosen ingredients:", ingredients_string)

    # Insert the order into Snowflake (add the chosen ingredients and name on the order)
    try:
        session.sql(f"""
            INSERT INTO smoothies.public.orders (Ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """).collect()
        st.success("Your smoothie order has been placed successfully!")
    except Exception as e:
        st.error(f"Error placing order: {e}")
else:
    st.warning("Please choose at least one ingredient for your smoothie.")
