import streamlit as st
import pandas as pd
import WebAPIPycharm as web

# Function to read data from Excel file
def read_data():
    owners = []
    opensources = []

    # Display text input boxes for entering owner and opensource values
    num_rows = st.number_input("Number of rows", min_value=1, value=1)
    for i in range(num_rows):
        owner = st.text_input(f"Owner {i + 1}")
        opensource = st.text_input(f"Opensource {i + 1}")
        owners.append(owner)
        opensources.append(opensource)

    # Button to trigger data processing
    if st.button("Process Data"):
        # Create DataFrame from lists of owners and opensources
        df_input = pd.DataFrame({"Owner": owners, "Opensource": opensources})
        return df_input

# Function to display data in Streamlit
def display_data(df):


    #st.write(f"## total commits :{df.groupby('Owner')[["Owner"]].count()}")
    owner_commits = df.groupby('Owner').size().reset_index(name='Total Commits')
    st.write("## Total Commits by Owner:")
    for index, row in owner_commits.iterrows():
        st.write(f"{row['Owner']}: {row['Total Commits']}")
    st.dataframe(df)


def main():

    df=read_data()
    DISPLAYdf=web.main(df)
    display_data(DISPLAYdf)



if __name__ == "__main__":
    main()