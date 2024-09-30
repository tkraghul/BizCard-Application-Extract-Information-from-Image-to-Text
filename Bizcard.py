import easyocr  # Optical Character Recognition
import numpy as np
import PIL
from PIL import Image, ImageDraw
import pandas as pd
import re
import sqlalchemy
import mysql.connector
from sqlalchemy import create_engine

import streamlit as st

# ===================================================   /   /   Dash Board   /   /   ======================================================== # 

# Configuring Streamlit GUI 
st.set_page_config(layout='wide')

# Title
st.title(':blue[Business Card Data Extraction]')

# Tabs 
tab1, tab2 = st.tabs(["Data Extraction zone", "Data modification zone"])

# ==========================================   /   /   Data Extraction and upload zone   /   /   ============================================== #

with tab1:
    st.subheader(':red[Data Extraction]')

    # Image file uploaded
    import_image = st.file_uploader('**Select a business card (Image file)**', type =['png','jpg', "jpeg"], accept_multiple_files=False)

    # Note
    st.markdown('''File extension support: **PNG, JPG, TIFF**, File size limit: **2 Mb**, Image dimension limit: **1500 pixel**, Language : **English**.''')

    # --------------------------------      /   Extraction process   /     ---------------------------------- #

    if import_image is not None:
        try:
            # Create the reader object with desired languages
            reader = easyocr.Reader(['en'], gpu=False)

        except:
            st.info("Error: easyocr module is not installed. Please install it.")

        try:
            # Read the image file as a PIL Image object
            if isinstance(import_image, str):
                image = Image.open(import_image)
            elif isinstance(import_image, Image.Image):
                image = import_image
            else:
                image = Image.open(import_image)
            
            image_array = np.array(image)
            text_read = reader.readtext(image_array)

            result = []
            for text in text_read:
                result.append(text[1])

        except:
            st.info("Error: Failed to process the image. Please try again with a different image.")

        # -------------------------      /   Display the processed card with yellow box   /     ---------------------- #

        col1, col2= st.columns(2)

        with col1:
            # Define a function to draw the box on image
            def draw_boxes(image, text_read, color='yellow', width=2):
                image_with_boxes = image.copy()
                draw = ImageDraw.Draw(image_with_boxes)
                for bound in text_read:
                    p0, p1, p2, p3 = bound[0]
                    draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
                return image_with_boxes

            result_image = draw_boxes(image, text_read)
            st.image(result_image, caption='Captured text')

        # ----------------------------    /     Data processing and converted into data frame   /   ------------------ #

        with col2:
            data = {
                "Company_name": [],
                "Card_holder": [],
                "Designation": [],
                "Mobile_number": [],
                "Email": [],
                "Website": [],
                "Area": [],
                "City": [],
                "State": [],
                "Pin_code": [],
            }

            def get_data(res):
                city = ""
                state = ""
                area = ""
                pin_code = ""
                for ind, i in enumerate(res):
                    if "www " in i.lower() or "www." in i.lower():
                        data["Website"].append(i)
                    elif "WWW" in i:
                        data["Website"].append(res[ind-1] + "." + res[ind])
                    elif "@" in i:
                        data["Email"].append(i)
                    elif re.match(r'^\+\d{1,4}-\d{1,4}-\d{4,10}$', i):
                        digits = re.findall(r'\d', i)
                        if len(digits) > 9:
                            data["Mobile_number"].append(i)
                    elif ind == len(res) - 1:
                        data["Company_name"].append(i)
                    elif ind == 0:
                        data["Card_holder"].append(i)
                    elif ind == 1:
                        data["Designation"].append(i)
                    elif re.search(r'^\d+\s.*[,.]', i):
                        area = i.split(',')[0]
                        data["Area"].append(area)
                    elif re.search(r',\s*([A-Z][a-zA-Z\s]*?)\s*,', i):
                        city_match = re.search(r',\s*([A-Z][a-zA-Z\s]*?)\s*,', i)
                        if city_match:
                            city = city_match.group(1).strip()
                            data["City"].append(city)
                    elif re.search(r'[,.]\s*(\w+)', i):
                        state_match = re.search(r'[,.]\s*(\w+)\s*\d{5,}', i)
                        if state_match:
                            state = state_match.group(1).strip()
                        data["State"].append(state)
                    elif re.search(r'\d{5,}', i):
                        pin_code = re.search(r'\d{5,}', i).group(0)
                        data["Pin_code"].append(pin_code)

            get_data(result)

            # Create dataframe
            data_df = pd.DataFrame([data])

            # Show dataframe
            st.dataframe(data_df.T)

        # --------------------------------------   /   Data Upload to MySQL   /   --------------------------------------- #

        # Create a session state object
        class SessionState:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
        session_state = SessionState(data_uploaded=False)

        # Upload button
        st.write('Click the :red[**Upload to MySQL DB**] button to upload the data')
        Upload = st.button('**Upload to MySQL DB**', key='upload_button')

        # Check if the button is clicked
        if Upload:
            session_state.data_uploaded = True

        # Execute the program if the button is clicked
        if session_state.data_uploaded:
            try:
                # Connect to the MySQL server
                connect = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="root",
                    auth_plugin='mysql_native_password')

                # Create a new database and use it
                mycursor = connect.cursor()
                mycursor.execute("CREATE DATABASE IF NOT EXISTS bizcard_db")
                mycursor.close()
                connect.database = "bizcard_db"

                # Connect to the newly created database
                engine = create_engine('mysql+mysqlconnector://root:root@localhost/bizcard_db', echo=False)

                try:
                    # Use pandas to insert the DataFrame data into the SQL Database table
                    data_df.to_sql('bizcardx_data', engine, if_exists='append', index=False, dtype={
                        "Company_name": sqlalchemy.types.VARCHAR(length=225),
                        "Card_holder": sqlalchemy.types.VARCHAR(length=225),
                        "Designation": sqlalchemy.types.VARCHAR(length=225),
                        "Mobile_number": sqlalchemy.types.String(length=50),
                        "Email": sqlalchemy.types.TEXT,
                        "Website": sqlalchemy.types.TEXT,
                        "Area": sqlalchemy.types.VARCHAR(length=225),
                        "City": sqlalchemy.types.VARCHAR(length=225),
                        "State": sqlalchemy.types.VARCHAR(length=225),
                        "Pin_code": sqlalchemy.types.String(length=10)})
                    
                    st.info('Data Successfully Uploaded')

                except:
                    st.info("Card data already exists")

                connect.close()

            except Exception as e:
                st.error(f"Error uploading data: {e}")

            # Reset the session state after executing the program
            session_state.data_uploaded = False

    else:
        st.info('Click the Browse file button and upload an image')

# =================================================   /   /   Modification zone   /   /   ==================================================== #

with tab2:

    col1,col2 = st.columns(2)

    # ------------------------------   /   /   Edit option   /   /   -------------------------------------------- #

    with col1:
        st.subheader(':red[Edit option]')

        try:
            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                auth_plugin='mysql_native_password',
                database="bizcard_db")

            cursor = conn.cursor()

            # Execute the query to retrieve the cardholder data
            cursor.execute("SELECT card_holder FROM bizcardx_data")

            # Fetch all the rows from the result
            rows = cursor.fetchall()

            # Take the cardholder name
            names = [row[0] for row in rows]

            # Create a selection box to select cardholder name
            cardholder_name = st.selectbox("**Select a Cardholder name to Edit the details**", names, key='cardholder_name')

            # Collect all data depending on the cardholder's name
            cursor.execute( "SELECT Company_name, Card_holder, Designation, Mobile_number, Email, Website, Area, City, State, Pin_code FROM bizcardx_data WHERE card_holder=%s", (cardholder_name,))
            col_data = cursor.fetchone()

            # DISPLAYING ALL THE INFORMATION
            Company_name = st.text_input("Company name", col_data[0])
            Card_holder = st.text_input("Cardholder", col_data[1])
            Designation = st.text_input("Designation", col_data[2])
            Mobile_number = st.text_input("Mobile number", col_data[3])
            Email = st.text_input("Email", col_data[4])
            Website = st.text_input("Website", col_data[5])
            Area = st.text_input("Area", col_data[6])
            City = st.text_input("City", col_data[7])
            State = st.text_input("State", col_data[8])
            Pin_code = st.text_input("Pin code", col_data[9])

            # UPDATE BUTTON
            if st.button("Update"):
                cursor.execute("""UPDATE bizcardx_data 
                                SET Company_name=%s, Designation=%s, Mobile_number=%s, Email=%s, Website=%s, Area=%s, City=%s, State=%s, Pin_code=%s
                                WHERE Card_holder=%s""",
                                (Company_name, Designation, Mobile_number, Email, Website, Area, City, State, Pin_code, Card_holder))
                conn.commit()

                st.info("Details successfully updated")

            conn.close()

        except Exception as e:
            st.error(f"Error: {e}")

    # ---------------------------------   /   /   Delete option   /   /   -------------------------------------------- #

    with col2:
        st.subheader(':red[Delete option]')

        try:
            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                auth_plugin='mysql_native_password',
                database="bizcard_db")

            cursor = conn.cursor()

            # Execute the query to retrieve the cardholder data
            cursor.execute("SELECT card_holder FROM bizcardx_data")

            # Fetch all the rows from the result
            rows = cursor.fetchall()

            # Take the cardholder name
            names = [row[0] for row in rows]

            # Create a selection box to select cardholder name
            cardholder_name = st.selectbox("**Select a Cardholder name to Delete the details**", names, key='delete_cardholder_name')

            # Delete button
            if st.button("Delete"):
                cursor.execute("DELETE FROM bizcardx_data WHERE Card_holder=%s", (cardholder_name,))
                conn.commit()

                st.info("Details successfully deleted")

            conn.close()

        except Exception as e:
            st.error(f"Error: {e}")

