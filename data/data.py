# read data and analyze traces.json
import json
import pandas as pd
import random
from tqdm import tqdm
import csv
import concurrent.futures
from collections import defaultdict
import concurrent.futures
import time


"""
data format:
{key: [list of youtube links], key: [list of youtube links], ...}
"""

def read_data(filename='data/traces.json/traces.json'):
    with open(filename) as f:
        data = json.load(f)
    return data

def analyze_data(data):
    # number of users
    num_users = len(data)
    # num of videos per user
    num_videos_per_user = {}
    
    # number of videos
    num_videos = 0
    for user in data:
        num_videos_per_user[user] = len(set(data[user]))
        num_videos += len(data[user])
    # number of unique videos
    unique_videos = set()
    for user in data:
        for video in data[user]:
            unique_videos.add(video)
    num_unique_videos = len(unique_videos)
    return num_users, num_videos, num_unique_videos, num_videos_per_user


# read three csv filess to extract youtube links and then randomly intersperse them with the existing data creating a new json file


# read three csv files and extract youtube links
def extract_yt_links():
    yt_links = {'Links': [], 'Category': []}

    files = [
        # 'data/data_gpt_test_2500_PILOT.xlsx - harmful.csv',
        'data/Harmfully classified videos_gpt-4.xlsx - gpt-4.csv',
        # 'data/sexual harm_all_data.xlsx - Data.csv',
        # 'data/Misinformation Videos_available.csv'
    ]

    for file in files:
        df = pd.read_csv(file)
        if 'video_link' in df.columns:
            # For file 1 structure
            yt_links['Links'] += df['video_link'].dropna().tolist()
            # add category
            yt_links['Category'] += ['Misinformation'] * len(df['video_id'].dropna().tolist())
        if 'links' in df.columns:
            # For file 1 structure
            yt_links['Links'] += df['links'].dropna().tolist()
            # add category
            yt_links['Category'] += df['Category'].dropna().tolist()
        elif 'Link' in df.columns:
            # For file 2 structure
             yt_links['Links'] += df['Link'].dropna().tolist()
             # read the first column of the file
             yt_links['Category'] += ['Hate and Harassment Harm'] * len(df['Link'].dropna().tolist()) #df['subcat'].dropna().tolist()
        elif 'Links' in df.columns:
            # For file 3 structure
             yt_links['Links'] += df['Links'].dropna().tolist()
            # add category
             yt_links['Category'] += ['Sexual Harm'] * len(df['Links'].dropna().tolist())
    pd.DataFrame(yt_links).to_csv('data/yt_links.csv', mode='a', index=False, header=not os.path.exists('data/yt_links.csv'))
    return yt_links



def read_yt_links():
    df = pd.read_csv('data/yt_links.csv')
    return df


# take 100 users and 50 video links each 
def get_data():
    users = read_data()
    new_users = {}
    user_count = 0
    items = list(users.items())
    random.shuffle(items)
    # remove unavailable links
    for user, links in items:
        if user_count == 50:
            break
        available_links = list(set(links))
        
        if len(available_links) > 50:
            new_users[user] = available_links[:50]
            user_count += 1
        else:
            print(f"User {user} has less than 50 available links")
    # new_users = {user: links[:50] for user, links in list(users.items())[:500]}
    return new_users

def make_data():
    yt_links = read_yt_links() 
    # where Category = Harassment or Sexual Harm
    yt_links = yt_links[yt_links['Category'] == 'Hate and Harassment Harm']
    # yt_links_test = yt_links[yt_links['Category'] == 'Sexual Harm'][-500:]
    print("Length of videos collected: ", len(yt_links['Links'].tolist()), "Links")
    # print("Length of videos collected for testing: ", len(yt_links_test['Links'].tolist()), "Links")
    # pd.DataFrame(yt_links_test).to_csv('data/yt_links_test.csv', index=False, header=False)
    users = get_data()
    for user in users:
        # take 50 unique links from the yt_links such that every user has 50 unique links
        users[user] += list(yt_links['Links'].sample(50))
    write_json(users)
    return users
 

# def clean_data():
#     data = read_data()
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         for user, cleaned_links in tqdm(zip(data.keys(), executor.map(remove_unavailable_links, data.values()))):
#             data[user] = list(set(cleaned_links))
#     write_json(data, 'data/cleaned_traces.json')

# def remove_unavailable_links(links):
#     new_links = []
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         results = list(tqdm(executor.map(site_check_with_delay, links), total=len(links), desc='Checking links'))
        
#     for link, result in zip(links, results):
#         if result:
#             new_links.append(link)
#     return new_links

# def site_check_with_delay(url):
#     try:
#         request = requests.get(url)
#         if "unavailable" in request.text or "community_guideline_violation" in request.text or "private" in request.text:
#             return False
#         else:
#             return True
#     except Exception as e:
#         print(f"An error occurred while processing the URL: {url}; {e}")
#         return True  
#     finally:
#         time.sleep(1)  # Add a delay of 1 second between requests


# let's say we have existing X users and total Y videos and now we want to randomly distribute Z youtube links to the existing users
#yt_links = [list of youtube links]
# import random

# def intersperse_yt_links(data, yt_links, categories):
#     users = list(data.keys())
#     num_users = len(users)
#     num_yt_links = len(yt_links)

#     # Organize YouTube links into categories
#     yt_links_per_category = {}
#     for i in range(num_yt_links):
#         category = categories[i]
#         if category not in yt_links_per_category:
#             yt_links_per_category[category] = []
#         yt_links_per_category[category].append(yt_links[i])

#     # Calculate the proportion of videos for each category
#     total_videos_per_category = {category: len(links) for category, links in yt_links_per_category.items()}

#     # Distribute YouTube links to users
#     for user in users:
#         yt_links_per_user = {}

#         # Calculate the proportion of videos for each user
#         total_videos_per_user = {category: 0 for category in yt_links_per_category.keys()}

#         for category in yt_links_per_category:
#             num_links = min(len(yt_links_per_category[category]), int(num_yt_links / num_users))
#             yt_links_per_user[category] = random.sample(yt_links_per_category[category], num_links)
#             total_videos_per_user[category] += len(yt_links_per_user[category])
            
#             yt_links_per_category[category] = [link for link in yt_links_per_category[category] if link not in yt_links_per_user[category]]

#         # Adjust for any remaining videos
#         remaining_videos = num_yt_links - sum(total_videos_per_user.values())
#         for category in yt_links_per_category:
#             num_links = min(len(yt_links_per_category[category]), remaining_videos)
#             yt_links_per_user[category].extend(random.sample(yt_links_per_category[category], num_links))
#             remaining_videos -= num_links

#         # Flatten the dictionary into a list of links for the user
#         user_links = [link for links in yt_links_per_user.values() for link in links]

#         # Add the links to the existing data for the user
#         data[user] += user_links
#     return data



    

def write_json(data, filename='data/new_traces_hnh.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)
    

def extract_yt_id(link):
    # get after v= and before & or end of string
    return link.split('v=')[1].split('&')[0]


def create_intervention_data():
    data = read_data('data/new_traces_hnh.json')
    new_data = defaultdict(list)
    videos = []
    n_users = 0
    batch = 0
    # new_data = {'user_0' [video1. video2..], 'user_1' [video1, video2..]... }
    for user, links in data.items():
        n_users += 1
        for link in links:
            yt_id = extract_yt_id(link)
            new_data['user_' + str(n_users)].append(yt_id)
    pd.DataFrame(new_data).to_csv(f'data/videos_hnh.csv', index=False)
        

    



def main():
    # clean_data()
    # data = read_data('data/cleaned_traces.json')
    # num_users, num_videos, num_unique_videos, num_videos_per_user = analyze_data(data)
    # print("Number of users: ", num_users)
    # print("Number of videos: ", num_videos)
    # print("Number of unique videos: ", num_unique_videos)
    # print("Number of unique videos per user: ", num_videos_per_user)
    # extract_yt_links()

    make_data()
    data = read_data("data/new_traces_hnh.json")
    num_users, num_videos, num_unique_videos, num_videos_per_user = analyze_data(data)
    print("Number of users: ", num_users)
    print("Number of videos: ", num_videos)
    print("Number of unique videos: ", num_unique_videos)
    print("Number of unique videos per user: ", num_videos_per_user)
    create_intervention_data()
    

    
    # yt_links = pd.read_csv('data/yt_links.csv')['Links'].tolist()
    # categories = pd.read_csv('data/yt_links.csv')['Category'].tolist()
    # data = intersperse_yt_links(data, yt_links, categories)
    # write_json(data)
    

if __name__ == "__main__":
    main()
