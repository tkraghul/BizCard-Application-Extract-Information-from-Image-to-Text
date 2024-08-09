import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import datetime
import pickle

# Set up page configuration for Streamlit
st.set_page_config(page_title='HDB Flat Resale Price Predictor', page_icon='🏠', initial_sidebar_state='expanded',
                   layout='wide')

# CSS for page setup
st.markdown("""
    <style>
    .main-menu {font-size:18px; margin-top:-40px;}
    .content {padding: 20px; background-color: #f5f5f5;}
    .header {margin-top: 20px; padding-top: 30px; text-align: center; background-color: #4CAF50; color: white; padding-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

c1, _, c2 = st.columns([2, 1, 2])
with _:
    st.empty()
    st.image(r"E:\image for st\singapore-flag-name-country-moving-wind-text-181190652.webp")
    st.empty()

# Set up the sidebar with optionmenu
st.markdown("""
    <style>
    .sidebar-title {
        color: #4CAF50;  /* Change this color to your preference */
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Add the sidebar title using Markdown
st.sidebar.markdown('<div class="sidebar-title">Main Menu</div>', unsafe_allow_html=True)

# Create the sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title=None,  # Remove default menu title
        options=["Home", "Get Prediction", "About"],
        icons=['house', "lightbulb", "info-circle"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {
                "padding": "10px",
                "border": "2px solid #4CAF50",
                "background-color": "#f0f0f0"
            },
            "icon": {
                "color": 'green',
                "font-size": "20px",
                "margin-right": "10px"
            },
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "margin": "5px 0px",
                "padding": "10px",
                "background-color": "#e0e0e0",
                "color": "#000000",
                "--hover-color": "#b2dfdb"
            },
            "nav-link-selected": {
                "background-color": "#80cbc4",
                "font-weight": "bold"
            },
        })
# User input values for selectbox and encoded for respective features
class option:
    option_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    encoded_month = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    
    option_town = ['ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG', 'CLEMENTI',
                   'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST', 'KALLANG/WHAMPOA', 'MARINE PARADE', 'QUEENSTOWN', 'SENGKANG', 'SERANGOON',
                   'TAMPINES', 'TOA PAYOH', 'WOODLANDS', 'YISHUN', 'LIM CHU KANG', 'SEMBAWANG', 'BUKIT PANJANG', 'PASIR RIS', 'PUNGGOL']
    
    encoded_town = {'ANG MO KIO': 0, 'BEDOK': 1, 'BISHAN': 2, 'BUKIT BATOK': 3, 'BUKIT MERAH': 4, 'BUKIT PANJANG': 5, 'BUKIT TIMAH': 6,
                    'CENTRAL AREA': 7, 'CHOA CHU KANG': 8, 'CLEMENTI': 9, 'GEYLANG': 10, 'HOUGANG': 11, 'JURONG EAST': 12, 'JURONG WEST': 13,
                    'KALLANG/WHAMPOA': 14, 'LIM CHU KANG': 15, 'MARINE PARADE': 16, 'PASIR RIS': 17, 'PUNGGOL': 18, 'QUEENSTOWN': 19,
                    'SEMBAWANG': 20, 'SENGKANG': 21, 'SERANGOON': 22, 'TAMPINES': 23, 'TOA PAYOH': 24, 'WOODLANDS': 25, 'YISHUN': 26}
    
    option_flat_type = ['1 ROOM', '2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 'MULTI-GENERATION']
    encoded_flat_type = {'1 ROOM': 0, '2 ROOM': 1, '3 ROOM': 2, '4 ROOM': 3, '5 ROOM': 4, 'EXECUTIVE': 5, 'MULTI-GENERATION': 6}
    
    option_flat_model = ['2-ROOM', '3GEN', 'ADJOINED FLAT', 'APARTMENT', 'DBSS', 'IMPROVED', 'IMPROVED-MAISONETTE', 'MAISONETTE',
                         'MODEL A', 'MODEL A-MAISONETTE', 'MODEL A2', 'MULTI GENERATION', 'NEW GENERATION', 'PREMIUM APARTMENT',
                         'PREMIUM APARTMENT LOFT', 'PREMIUM MAISONETTE', 'SIMPLIFIED', 'STANDARD', 'TERRACE', 'TYPE S1', 'TYPE S2']
    
    encoded_flat_model = {'2-ROOM': 0, '3GEN': 1, 'ADJOINED FLAT': 2, 'APARTMENT': 3, 'DBSS': 4, 'IMPROVED': 5, 'IMPROVED-MAISONETTE': 6,
                          'MAISONETTE': 7, 'MODEL A': 8, 'MODEL A-MAISONETTE': 9, 'MODEL A2': 10, 'MULTI GENERATION': 11, 'NEW GENERATION': 12,
                          'PREMIUM APARTMENT': 13, 'PREMIUM APARTMENT LOFT': 14, 'PREMIUM MAISONETTE': 15, 'SIMPLIFIED': 16, 'STANDARD': 17,
                          'TERRACE': 18, 'TYPE S1': 19, 'TYPE S2': 20}

# Set up information for the 'Get Prediction' menu
if selected == "Get Prediction":
    st.write('')
    st.markdown("<h5 style=color:#4CAF50>To Predict the Resale Price of a Flat, Please Provide the Following Information:</h5>", unsafe_allow_html=True)
    st.write('')

    # Created form to get the user input 
    with st.form('prediction'):
        col1, col2 = st.columns(2)
        with col1:
            user_month = st.selectbox(label='Month', options=option.option_months, index=None)
            user_town = st.selectbox(label='Town', options=option.option_town, index=None)
            user_flat_type = st.selectbox(label='Flat Type', options=option.option_flat_type, index=None)
            user_flat_model = st.selectbox(label='Flat Model', options=option.option_flat_model, index=None)
            floor_area_sqm = st.number_input(label='Floor area sqm', min_value=10.0)
            price_per_sqm = st.number_input(label='Price Per sqm', min_value=100.00)
        
        with col2:
            year = st.text_input(label='Year', max_chars=4)
            block = st.text_input(label='Block', max_chars=3)
            lease_commence_date = st.text_input(label='Year of lease commence', max_chars=4)
            remaining_lease = st.number_input(label='Remaining lease year', min_value=0, max_value=99)
            years_holding = st.number_input(label='Years Holding', min_value=0, max_value=99)
            c1, c2 = st.columns(2)
            with c1:
                storey_start = st.number_input(label='Storey start', min_value=1, max_value=50)
            with c2:
                storey_end = st.number_input(label='Storey end', min_value=1, max_value=51)
            
            st.markdown('<br>', unsafe_allow_html=True)
            button = st.form_submit_button('PREDICT', use_container_width=True)

    if button:
        with st.spinner("Predicting..."):
            # Check whether user filled all required fields
            if not all([user_month, user_town, user_flat_type, user_flat_model, floor_area_sqm, price_per_sqm, year, block,
                        lease_commence_date, remaining_lease, years_holding, storey_start, storey_end]):
                st.error("Please fill in all required fields.")
            else:
                # Create features from user input 
                current_year = datetime.datetime.now().year
                current_remaining_lease = remaining_lease - (current_year - int(year))
                age_of_property = current_year - int(lease_commence_date)
                month = option.encoded_month[user_month]
                town = option.encoded_town[user_town]
                flat_type = option.encoded_flat_type[user_flat_type]
                flat_model = option.encoded_flat_model[user_flat_model]
                floor_area_sqm_log=np.log(floor_area_sqm)
                remaining_lease_log=np.log1p(remaining_lease)
                price_per_sqm_log=np.log(price_per_sqm)

                # Prepare the input features for prediction
                features = np.array([[month, town, flat_type, block, flat_model, lease_commence_date, year, storey_start,
                                    storey_end, years_holding, current_remaining_lease, age_of_property, floor_area_sqm_log, 
                                    remaining_lease_log,price_per_sqm_log]])

                # Load the pre-trained model and make predictions
                with open(r"C:\Users\Raghul\Decisiontree.pkl", 'rb') as file:
                    model = pickle.load(file)
                prediction = model.predict(features)

                st.success(f"The predicted resale price for the flat is: SGD {prediction[0]:,.2f}")

# Home section content
if selected == "Home":
    st.write('')
    st.markdown("<h1 style=color:#4CAF50>Welcome to the Singapore HDB Flat Resale Price Predictor</h1>", unsafe_allow_html=True)
    st.write('<br>', unsafe_allow_html=True)
    st.write("This application uses machine learning models to predict the resale price of HDB flats based on various features. Please navigate to the 'Get Prediction' tab to use the prediction feature.")

# About section content
if selected == "About":
    st.write('')
    st.markdown("<h1 style=color:#4CAF50>About This Application</h1>", unsafe_allow_html=True)
    st.write('<br>', unsafe_allow_html=True)
    st.write("This application was developed to assist in predicting the resale price of HDB flats in Singapore. It utilizes various features such as flat type, location, and other parameters to provide an estimated price based on historical data and machine learning models.")
