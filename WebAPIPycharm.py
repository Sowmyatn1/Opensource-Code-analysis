import streamlit as st
import pandas as pd
import requests
import numpy as np
import json


# Function to display data in Streamlit
def display_data(df):


    #st.write(f"## total commits :{df.groupby('Owner')[["Owner"]].count()}")
    owner_commits = df.groupby('Owner').size().reset_index(name='Total Commits')
    st.write("## Total Commits by Owner:")
    for index, row in owner_commits.iterrows():
        st.write(f"{row['Owner']}: {row['Total Commits']}")
    st.dataframe(df)

def calculateSize(df):
    conditions = [
        df['insertions'] < 10,
        df['insertions'].between(10, 40),
        df['insertions'].between(40, 70)
    ]
    choices = ['XS', 'S', 'M']
    df.loc[:, "Size"] = np.select(conditions, choices, default='L')
    return df


# json_prefix here is the extra characters the response has as we know chromium and android has extra char and GIT lab dosen't so
# pass json_prefix as false to gitlab

def fetch_data_from_api(url, Opensource):
    try:
        response = requests.get(url)
        print("Response:", response)
        output = response.text
        # print(output)
        if Opensource == 'chromium' or Opensource == 'android':
            # Remove potential security prefixes
            output = output[4:]

        if output:
            return pd.DataFrame(json.loads(output))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")

    return pd.DataFrame()


def query_api_with_fallback(url, Replace_url, Opensource):
    responsedf = fetch_data_from_api(url, Opensource)
    # Check if the DataFrame is empty (no data was found)
    # print(responsedf.head())
    if responsedf.empty:
        print(f"No data found for owner under {url}, checking for author...")
        responsedf = fetch_data_from_api(Replace_url, Opensource)
        if responsedf.empty:
            print(f"No data found for author as well.{Replace_url}")

    return responsedf


def save_data(all_data):
    responsedf = pd.concat(all_data, ignore_index=True)
    return responsedf

def getfinalResponse(Owner, opensource):
    match opensource.strip().lower():
        case 'chromium':
            url = f"https://chromium-review.googlesource.com/changes/?q=owner:{Owner}"
            Replaceurl = f"https://chromium-review.googlesource.com/changes/?q=author:{Owner}"
            print("invoking web api for chromium using owner...", Owner)
            responsedf = query_api_with_fallback(url, Replaceurl, 'chromium')
            if responsedf.empty:
                print("No data found for chromium for owner:", Owner)
                return
            # print(responsedf)
            responsedf = responsedf.loc[:, ["subject", "project", "branch", "status", "insertions", "updated"]]

            calculateSize(responsedf.head())
            responsedf["Owner"] = Owner
            responsedf["OpenSource"] = "Chromium"
            responsedf = responsedf.drop(columns=['insertions'])
            # responsedf=pd.concat([responsedf,responsechromiumdf]).drop_duplicates().reset_index(drop=True)
            print("chromium done ::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            # print(responsedf)
            yield responsedf

        case 'gitlab':
            url = f"https://gitlab.freedesktop.org/api/v4/projects/176/repository/commits?author={Owner}"
            Replaceurl = f"https://gitlab.freedesktop.org/api/v4/projects/176/repository/commits?author={Owner}"
            print("invoking web api for gitlab...", Owner)
            responsedf = query_api_with_fallback(url, Replaceurl, 'gitlab')
            if responsedf.empty:
                print("No data found for chromium for owner:", Owner)
                return
            responsedf = responsedf.loc[:, ["title", "committed_date"]]
            responsedf = responsedf.rename(columns={"title": "subject", "committed_date": "updated"})
            responsedf["project"] = "chromiumos/third_party/mesa"
            responsedf["branch"] = "Mesa"
            responsedf["status"] = "Merged"
            responsedf["Size"] = "unknown"
            responsedf["Owner"] = Owner
            responsedf["OpenSource"] = "GITLAB"

            # responsegitdf = responsegitdf.drop(columns=['title', 'committed_date'])
            new_order = ["subject", "project", "branch", "status", "Size", "updated", "Owner", "OpenSource"]
            responsedf = responsedf[new_order]
            print(responsedf.head(2))
            # responsedf=pd.concat([responsegitdf, responsedf]).drop_duplicates().reset_index(drop=True)
            #  print(responsedf.head(2))
            print("gitlab done ::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            yield responsedf

        case 'android':

            statuses = ["open", "MERGED", "Abandoned"]
            for status in statuses:
                url = f"https://android-review.googlesource.com/changes/?q=owner:{Owner}%20status:{status}"
                Replaceurl = f"https://android-review.googlesource.com/changes/?q=author:{Owner}%20status:{status}"
                print(f"invoking web api for android : {Owner} for status :{status}")
                responsedf = query_api_with_fallback(url, Replaceurl, 'android')
                if responsedf.empty:
                    print("No data found for chromium for owner:", Owner)
                    return
                responsedf = responsedf.loc[:, ["subject", "project", "insertions", "branch", "updated", "status"]]
                calculateSize(responsedf)
                responsedf["Owner"] = Owner
                responsedf["OpenSource"] = "Android"
                responsedf = responsedf.drop(columns=['insertions'])
                print(f"android done for {status}::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                yield responsedf
            #  responsedf=pd.concat([responseAndroidOpendf, responsedf]).drop_duplicates().reset_index(drop=True)



def main():

   # df=read_data()
    df_input=pd.DataFrame()
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

    all_data = []
    for index, row in df_input.iterrows():
        owner = row['Owner']
        projects = row['Opensource'].split(',')
        for project in projects:
            all_data.extend(getfinalResponse(owner, project.strip()))
    #df_input = save_data(all_data)


    if all_data:
        responsedf = pd.concat(all_data, ignore_index=True)
        display_data(responsedf)
    else:
        st.write("Enter the details.")


if __name__ == "__main__":
    main()
