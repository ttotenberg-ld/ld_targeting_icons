import blessed
from dotenv import load_dotenv
import json
import ldclient
from ldclient.config import Config
import os
from prettytable import PrettyTable as pt
import time
import unicodedata
from utils.create_context import *

'''
Get environment variables
'''
load_dotenv()

'''
Create a terminal and clear it
'''
term = blessed.Terminal()
print(term.clear)


'''
Set sdk_key and feature_flag_key to your LaunchDarkly keys, then initialize the LD client. These keys are pulled from your Replit environment variables, AKA secrets.
'''
sdk_key = os.environ.get('SDK_KEY')
feature_flag_key = os.environ.get('FLAG_KEY')
# sdk_key = "sdk-f736700e-5e55-4221-a045-3dfc960e01ef"
# feature_flag_key = "release-new-ui"
ldclient.set_config(Config(sdk_key,send_events=False))


'''
Define symbols for the table
'''
true_icon = unicodedata.lookup('WHITE HEAVY CHECK MARK')
false_icon = unicodedata.lookup('CROSS MARK')


'''
Create fake targets for this exercise
'''
def create_contexts():
    num_contexts = 2000
    contexts_array = []
    for i in range(num_contexts):
        context = create_multi_context()
        json.dumps(contexts_array.append(context))
        with open('data/contexts.json', 'w') as f:
            f.write(str(contexts_array))

'''
Add targets to the table
'''
def add_targets_to_table(data):
    context_table = []

    for i in data:
        feature = ldclient.get().variation(feature_flag_key, i, False)
        if feature:
            feature = true_icon
        else:
            feature = false_icon

        context_table.append(feature)
        
    return context_table


'''
Clears the terminal, then renders the table
'''
def render_table(table):
    with term.hidden_cursor():
        print(term.home + term.clear, end='')
        # print(table)
        for i in table:
            print(i,end = '')


'''
OK, word of warning: Everything below is pretty hacky. :)
Ideally, I wanted to subscribe to flag changes and render the table only when there was an update. However, once I was mostly done creating this, I realized the Python SDK doesn't have that functionality yet! (as of fall 2022)

https://docs.launchdarkly.com/sdk/features/flag-changes

So instead, I'm saving an array of trues/falses for each target user, updating that array multiple times per second based on the latest targeting data from LaunchDarkly, and re-rendering the table if that has been updated.

Don't judge me! :) It's hacky but it works!
'''
if __name__ == '__main__':
    # Uncomment the line below and rerun the script if you want to generate new targets
    # create_contexts()
    data = json.load(open("data/contexts.json"))
    target_array = [False]
    while True:
        new_target_array = []
        for i in data:
            feature = ldclient.get().variation(feature_flag_key, i, False)
            new_target_array.append(feature)
        if target_array != new_target_array:
            table = add_targets_to_table(data)
            render_table(table)
            target_array = new_target_array
            new_target_array = []
        time.sleep(.1)
