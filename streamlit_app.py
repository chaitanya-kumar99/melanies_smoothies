import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# Input for the name on the smoothie order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

connection_parameters = {
    "account": "PNBFAXK-GQB48216",
    "user": "chaitanya.yelisetti@teamhgs.com",
    "password": "Chinnu@123456789",
    "role": "SYSADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "PUBLIC"
}
session = Session.builder.configs(connection_parameters).create()

# Fetch available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Create a multiselect to choose ingredients (up to 5 ingredients)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=[row['FRUIT_NAME'] for row in my_dataframe.collect()],
    max_selections=5
)

# Check if the user has selected any ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Create a comma-separated list of chosen ingredients
    
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

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=true)
