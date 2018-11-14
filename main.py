#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from collections import defaultdict
from os.path import join, dirname

import networkx as nx
import tweepy
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CK = os.environ.get('TWITTER_CONSUMER_KEY')
CS = os.environ.get('TWITTER_CONSUMER_SECRET')
AT = os.environ.get('TWITTER_ACCESS_TOKEN')
AS = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)

api = tweepy.API(auth, wait_on_rate_limit=True)


def getFollowers_ids(api, id):
    # Get Id list of followers
    followers_ids = tweepy.Cursor(api.followers_ids, id=id, cursor=-1).items()

    followers_ids_list = []
    try:
        followers_ids_list = [followers_id for followers_id in followers_ids]
    except tweepy.error.TweepError as e:
        print(e.reason)

    return followers_ids_list


center_to_followers = {}
node_attrs = defaultdict(dict)

# center account
CENTER_ACCOUNTS = ['yabaiwebyasan', 'statue_of_weben']

for center_screen_name in CENTER_ACCOUNTS:

    # get center account information (node attributes)
    center_info = api.get_user(screen_name=center_screen_name)

    # get id of center account
    center_id = center_info.id

    node_attrs[center_id]['screenName'] = center_screen_name
    node_attrs[center_id]['followersNum'] = center_info.followers_count
    node_attrs[center_id]['followNum'] = center_info.friends_count

    center_to_followers[center_id] = getFollowers_ids(api=api, id=center_screen_name)

    # set empty value to account attribute that is not center
    for follower_id in center_to_followers[center_id]:
        node_attrs.setdefault(follower_id, {'screenName': '', 'followersNum': '', 'followNum': ''})

graph = nx.from_dict_of_lists(center_to_followers)
nx.set_node_attributes(graph, node_attrs)
nx.write_gml(graph, 'twitter.gml')
