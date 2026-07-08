import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Ebola Surveillance Dashboard",
    page_icon="🦠",
    layout="wide"
)

connection = sqlite3.connect("ebola_surveillance.db")

st.sidebar.title("🦠 Ebola Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Analysis",
        "Learn About Ebola",
        "Public Health Measures",
        "Contact Public Health",
        "Report Exposure",
    ]
)

if page == "Dashboard":

    st.title("🦠 Ebola Surveillance Dashboard")
    st.write("Monitor the latest Ebola statistics from the CDC.")

    latest_date = pd.read_sql_query("""
        SELECT MAX(update_date) AS latest_update
        FROM ebola_reports
    """, connection)

    latest_update = latest_date["latest_update"][0]

    totals = pd.read_sql_query("""
        SELECT
            SUM(CASE WHEN r.report_name='Confirmed cases' THEN e.count ELSE 0 END) AS confirmed_cases,
            SUM(CASE WHEN r.report_name='Confirmed deaths' THEN e.count ELSE 0 END) AS confirmed_deaths,
            SUM(CASE WHEN r.report_name='Probable cases' THEN e.count ELSE 0 END) AS probable_cases,
            SUM(CASE WHEN r.report_name='Probable deaths' THEN e.count ELSE 0 END) AS probable_deaths

        FROM ebola_reports e

        JOIN report_types r
        ON e.report_type_id = r.report_type_id
    """, connection)

    countries = pd.read_sql_query("""
        SELECT COUNT(*) AS total_countries
        FROM countries
    """, connection)

    st.caption(f"📅 Latest Update: {latest_update}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Countries Reporting", countries["total_countries"][0])

    with col2:
        st.metric("Confirmed Cases", totals["confirmed_cases"][0])

    with col3:
        st.metric("Confirmed Deaths", totals["confirmed_deaths"][0])

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Probable Cases", totals["probable_cases"][0])

    with col5:
        st.metric("Probable Deaths", totals["probable_deaths"][0])

    st.divider()

    country = st.text_input(
        "Enter a country",
        placeholder="e.g. DRC, Uganda, France"
    )

    if country:

        query = """
        SELECT
            r.report_name,
            e.count,
            e.update_date

        FROM ebola_reports e

        JOIN countries c
        ON e.country_id = c.country_id

        JOIN report_types r
        ON e.report_type_id = r.report_type_id

        WHERE LOWER(c.country_name) = LOWER(?)
        """

        country_data = pd.read_sql_query(
            query,
            connection,
            params=(country,)
        )

        if country_data.empty:
            st.warning(f"No Ebola report found for '{country}'.")

        else:

            confirmed_cases = country_data.loc[
                country_data["report_name"] == "Confirmed cases",
                "count"
            ].iloc[0]

            confirmed_deaths = country_data.loc[
                country_data["report_name"] == "Confirmed deaths",
                "count"
            ].iloc[0]

            probable_cases = country_data.loc[
                country_data["report_name"] == "Probable cases",
                "count"
            ].iloc[0]

            probable_deaths = country_data.loc[
                country_data["report_name"] == "Probable deaths",
                "count"
            ].iloc[0]

            update_date = country_data["update_date"].iloc[0]

            st.subheader(f"Results for {country.title()}")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Confirmed Cases", confirmed_cases)
                st.metric("Probable Cases", probable_cases)

            with col2:
                st.metric("Confirmed Deaths", confirmed_deaths)
                st.metric("Probable Deaths", probable_deaths)

            st.caption(f"Report Date: {update_date}")

elif page == "Analysis":

    st.title("📈 Ebola Data Analysis")

    analysis_df = pd.read_sql_query("""

    SELECT

        c.country_name,
        r.report_name,
        e.count

    FROM ebola_reports e

    JOIN countries c
    ON e.country_id = c.country_id

    JOIN report_types r
    ON e.report_type_id = r.report_type_id

    """, connection)
    st.subheader("Confirmed Cases by Country")

    confirmed = analysis_df[
        analysis_df["report_name"] == "Confirmed cases"
    ]

    fig = px.bar(
        confirmed,
        x="country_name",
        y="count",
        color="country_name",
        text="count"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Overall Report Distribution")

    totals = analysis_df.groupby(
        "report_name"
    )["count"].sum().reset_index()

    pie = px.pie(
        totals,
        names="report_name",
        values="count"
    )

    st.plotly_chart(pie, use_container_width=True)
    
    st.subheader("🌍 Ebola Cases by Country")

    map_data = pd.DataFrame({
        "country_name": ["DRC", "Uganda", "France"],
        "latitude": [-2.8797, 1.3733, 46.2276],
        "longitude": [23.6560, 32.2903, 2.2137]
    })
    confirmed_map = analysis_df[
        analysis_df["report_name"] == "Confirmed cases"
    ][["country_name", "count"]]
    map_df = map_data.merge(
    confirmed_map,
    on="country_name"
    )
    fig = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    size="count",
    color="country_name",
    hover_name="country_name",
    hover_data={"count": True},
    projection="natural earth",
    title="Confirmed Ebola Cases by Country"
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "Learn About Ebola":

    st.title("📖 Learn About Ebola")

    st.image(
        "https://www.cdc.gov/vhf/ebola/images/ebola-virus.jpg",
        caption="Ebola virus (CDC)"
    )

    st.header("What is Ebola?")

    st.write("""
Ebola Virus Disease (EVD) is a severe and often fatal illness affecting humans
and other primates. It is caused by viruses of the genus Ebolavirus and is
characterized by sudden onset of fever, weakness, vomiting, diarrhea and, in
some cases, internal and external bleeding.
""")

    st.header("Signs and Symptoms")

    st.markdown("""
-  Fever
-  Severe headache
-  Muscle pain
-  Weakness and fatigue
-  Vomiting
-  Diarrhea
-  Abdominal pain
-  Unexplained bleeding or bruising
""")

    st.header("Transmission")

    st.markdown("""
Ebola spreads through direct contact with:

- Blood
- Body fluids
- Contaminated objects
- Infected animals
- An infected person's clothing or bedding
""")

    st.header("Incubation Period")

    st.info("Symptoms usually appear between **2 and 21 days** after exposure.")

    st.header("Treatment")

    st.markdown("""
Treatment includes:

- Intravenous fluids
- Electrolyte replacement
- Oxygen therapy
- Blood pressure support
- Treatment of secondary infections
- FDA-approved monoclonal antibody treatments for some Ebola virus species
""")

    st.header("Prevention")

    st.markdown("""
- Wash hands regularly
- Avoid contact with infected body fluids
- Wear personal protective equipment (PPE)
- Practice safe burial procedures
- Isolate infected patients
- Vaccinate at-risk populations where recommended
""")

    st.header("Vaccination")

    st.success("""
The Ervebo vaccine has been shown to protect against Ebola virus disease caused
by the Zaire ebolavirus and is used in outbreak response strategies.
""")

    st.header("Quick Facts")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Incubation", "2–21 Days")

    with col2:
        st.metric("Transmission", "Body Fluids")

    with col3:
        st.metric("Vaccine", "Available")
    st.divider()

    st.header("🩺 Ebola Symptom Checker")

    st.warning(
        "This tool is for educational purposes only. It cannot diagnose Ebola. "
        "If you are feeling unwell or think you have been exposed, seek medical attention immediately."
    )

    st.write("Select any symptoms you are experiencing:")

    fever = st.checkbox("Fever")
    headache = st.checkbox("Severe headache")
    muscle = st.checkbox("Muscle pain")
    weakness = st.checkbox("Weakness or fatigue")
    vomiting = st.checkbox("Vomiting")
    diarrhea = st.checkbox("Diarrhea")
    abdominal = st.checkbox("Abdominal pain")
    bleeding = st.checkbox("Unexplained bleeding or bruising")

    st.subheader("Exposure History")

    travel = st.radio(
        "Have you recently travelled to an area with an Ebola outbreak?",
        ["No", "Yes"]
    )

    contact = st.radio(
        "Have you had contact with someone suspected or confirmed to have Ebola?",
        ["No", "Yes"]
    )

    if st.button("Check Symptoms"):

        symptom_count = sum([
            fever,
            headache,
            muscle,
            weakness,
            vomiting,
            diarrhea,
            abdominal,
            bleeding
        ])

        if symptom_count <= 2:
            st.success(
                "You selected only a few symptoms commonly associated with Ebola."
            )

        elif symptom_count <= 5:
            st.warning(
                "You selected several symptoms that can occur with Ebola. "
                "These symptoms are also common in many other illnesses."
            )

        else:
            st.error(
                "You selected many symptoms commonly associated with Ebola."
            )

        if travel == "Yes" or contact == "Yes":
            st.warning(
                "You also reported a possible exposure. If you develop symptoms or are concerned about exposure, contact your local healthcare provider or public health authority as soon as possible."
            )

        st.info(
            "⚠️ This checker is educational only and cannot diagnose Ebola. "
            "Only qualified healthcare professionals and laboratory testing can confirm an Ebola infection."
        )

elif page == "Public Health Measures":

    st.title("🛡️ Public Health Measures")

    st.write(
        "These public health measures help reduce the spread of Ebola Virus Disease."
    )

    st.divider()

    with st.expander("🧼 Personal Prevention", expanded=True):

        st.markdown("""
- Wash hands regularly with soap and clean water.
- Avoid contact with blood and body fluids.
- Do not touch someone who is sick without proper protection.
- Avoid handling bats, monkeys and other wild animals.
- Cook meat thoroughly before eating.
""")

    with st.expander("🏥 Healthcare Measures"):

        st.markdown("""
- Early detection of suspected cases.
- Isolation of infected patients.
- Contact tracing.
- Safe laboratory testing.
- Proper use of Personal Protective Equipment (PPE).
- Safe burial procedures.
""")

    with st.expander("✈️ Travel Measures"):

        st.markdown("""
- Check outbreak updates before travelling.
- Follow screening requirements at borders.
- Avoid unnecessary travel to outbreak areas.
- Report symptoms immediately after travelling.
""")

    with st.expander("👨‍👩‍👧 Community Measures"):

        st.markdown("""
- Report suspected cases immediately.
- Cooperate with health workers.
- Follow quarantine instructions.
- Avoid misinformation.
- Attend community health education sessions.
""")

    with st.expander("🚨 What to Do During an Outbreak"):

        st.markdown("""
1. Seek medical attention immediately if symptoms develop.
2. Avoid close contact with others.
3. Call your local health authority.
4. Do not self-medicate.
5. Monitor symptoms for 21 days after exposure.
""")

    st.divider()

    st.success(
        "Public health measures are most effective when communities, healthcare workers, and governments work together."
    )
elif page == "Report Exposure":

    st.title("⚠️ Report Possible Ebola Exposure")

    st.write(
        """
        If you believe you may have been exposed to Ebola, complete the form below.
        This report is stored in the application's local database for demonstration purposes.
        """
    )

    with st.form("exposure_form"):

        person_name = st.text_input("Full Name (Optional)")

        country = st.text_input("Country")

        exposure_date = st.date_input("Date of Possible Exposure")

        exposure_type = st.selectbox(
            "Type of Exposure",
            [
                "Direct contact with an infected person",
                "Contact with blood or body fluids",
                "Healthcare worker exposure",
                "Contact with infected animals",
                "Travel to an affected area",
                "Other"
            ]
        )

        comments = st.text_area(
            "Describe what happened (Optional)"
        )

        submitted = st.form_submit_button("Submit Exposure Report")

    if submitted:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO exposure_reports
            (
                person_name,
                country,
                exposure_type,
                exposure_date,
                comments
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            person_name,
            country,
            exposure_type,
            str(exposure_date),
            comments
        ))

        connection.commit()

        st.success("✅ Your exposure report has been submitted successfully.")

        st.divider()

        st.header("🩺 Exposure Risk Assessment")

        if exposure_type == "Direct contact with an infected person":

            st.error("""
    ### 🔴 High Risk

    You reported direct contact with an infected person.

    **Recommendations**

    - Seek immediate medical attention.
    - Inform your local public health authority.
    - Avoid contact with others.
    - Monitor your health for 21 days.
    """)

        elif exposure_type in [
            "Contact with blood or body fluids",
            "Healthcare worker exposure"
        ]:

            st.warning("""
    ### 🟠 Moderate Risk

    Your reported exposure may place you at increased risk.

    **Recommendations**

    - Contact a healthcare provider.
    - Monitor yourself for symptoms.
    - Follow advice from your local health authority.
    """)

        elif exposure_type == "Travel to an affected area":

            st.info("""
    ### 🟡 Low–Moderate Risk

    Travel alone does not necessarily mean exposure.

    **Recommendations**

    - Monitor yourself for symptoms.
    - Practice good hand hygiene.
    - Seek medical advice if symptoms develop.
    """)

        else:

            st.success("""
    ### 🟢 Lower Risk

    Based on the information provided, your reported exposure appears to be lower risk.

    Continue monitoring your health and seek medical advice if symptoms develop.
    """)
    st.divider()

    st.header("📚 Learn More")

    st.markdown("""
    For official information about Ebola, visit:

    - World Health Organization (WHO)
    - Centers for Disease Control and Prevention (CDC)
    - Your country's Ministry of Health

    Always rely on official public health guidance during an outbreak.
    """)
elif page == "Contact Public Health":

    st.title("📩 Contact Public Health")

    st.write(
        "Submit a concern or question to your local public health authority."
    )

    with st.form("contact_form"):

        name = st.text_input("Full Name")

        email = st.text_input("Email Address")

        country = st.text_input("Country")

        subject = st.selectbox(
            "Subject",
            [
                "General Question",
                "Report a Concern",
                "Travel Advice",
                "Vaccination Information",
                "Symptoms",
                "Other"
            ]
        )

        message = st.text_area("Message")

        submitted = st.form_submit_button("Submit")

    if submitted:

        if name.strip() == "" or email.strip() == "" or message.strip() == "":

            st.error("Please complete all required fields.")

        else:

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO public_health_messages
                (
                    name,
                    email,
                    country,
                    subject,
                    message
                )

                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                email,
                country,
                subject,
                message
            ))

            connection.commit()

            st.success("✅ Your concern has been submitted.")

    st.divider()

    st.header("📢 Public Health Advice")

    advice = pd.read_sql_query("""

        SELECT
            topic,
            advice,
            last_updated

        FROM public_health_advice

        ORDER BY last_updated DESC

    """, connection)

    for _, row in advice.iterrows():

        with st.expander(row["topic"]):

            st.write(row["advice"])

            st.caption(f"Last Updated: {row['last_updated']}")

    st.divider()

    st.header("📝 Community Concerns")

    concerns = pd.read_sql_query("""

        SELECT

            message_id,
            name,
            subject,
            status,
            response,
            date_submitted

        FROM public_health_messages

        ORDER BY date_submitted DESC

    """, connection)

    st.dataframe(
        concerns,
        use_container_width=True
    )

connection.close()
    




    