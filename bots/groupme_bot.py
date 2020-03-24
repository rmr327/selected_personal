from groupy.client import Client
import re


def contains_any(string_val, list_v):
    """"" Check whether sequence str contains ANY of the items in list. """
    return 1 in [c in string_val for c in list_v]


def regular_expression_matching(regex):
    return re.search(regex, message.text)


token = ''  # group me token goes here
client = Client.from_token(token)

key_list = [['drop', 'pickup', 'pick up', 'take', 'cover'], ['shift'], ['1', '2', '3', '4', '5', '6', '7', '8', '9',
                                                                        'opening', 'Opening', 'closing', 'Closing']]

response_list = ['I can', 'i can', 'I can take it', 'I can pick it up']

for group in client.groups.list_all():
    # if group.name == 'Game Of Phones':
    if group.name == 'DSC Building Mangers':
        # for message in itertools.islice(group.messages.list_all(), 1000):
        for message in group.messages.list_all():
            if message.text is None:
                continue
            target_acquired = True
            for keys in key_list:
                if contains_any(message.text, keys):
                    continue
                else:
                    target_acquired = False
                    break

            if target_acquired:
                matched = False
                regex_list = [r'\d+-\d+', r'Opening|opening', r'Closing|closing', r'\d+ to \d+',
                              r'\d+ am (\D)* \d+ am*', r'\d+ am (\D)* \d+ pm*', r'\d+ pm (\D)* \d+ pm*',
                              r'\d+ pm (\D)* \d+ am*']

                for rege in regex_list:
                    match = re.search(rege, message.text)
                    if match is not None:
                        matched = True
                        break

                if not matched:
                    print(message.text)

                # print('**', match.group(), '***')
