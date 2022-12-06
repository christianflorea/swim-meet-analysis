import requests
from bs4 import BeautifulSoup
import pandas as pd
import string


page = requests.get(
    "https://www.swimrankings.net/index.php?page=meetDetail&meetId=629800&gender=1&styleId=17")
soup = BeautifulSoup(page.content, 'html.parser')
result_header = soup.find(class_="meetResultHead")

event_name = result_header.find(class_="event").get_text()

results = []
line = {"place": "", "name": "", "team": ""}
translator = str.maketrans("", "", string.punctuation)

event0 = soup.find("table").find(class_="meetResult0")
iterator = 0
for element in event0.next_elements:
    if str(element)[0] == " ":
        element = element[1:]
    if str(element)[0] == "<":
        continue
    iterator += 1
    if str(element)[:9] == "GENERATED":
        break
    element = element.translate(translator)
    if iterator % 7 == 1:
        line["place"] = element
        # print(f"Rank = {element}")
    elif iterator % 7 == 2:
        line["name"] = element
        # print(f"Name = {element}")
    elif iterator % 7 == 5:
        line["team"] = element
        # print(f"Team = {element}")
    elif iterator % 7 == 0:
        results.append(line)
        # print(line)
        line = {"place": "", "name": "", "team": ""}
    else:
        continue

for result in results:
    print(result)


# event0 = soup.find_all(class_="meetResult0")
# print(len(event0))

# tags = {tag.name for tag in event0}

# print(len(tags))

# for tag in tags:
#     print(tag)

# for string in event0:
#     if contains("name", str(string)):
#         filtered_menu.append(string)

# print(filtered_menu[0])

# event_name = event0.find(class_="name").get_text()
# print(event_name)

# event0 = soup.find(class_="meetResult0")

# event_name = event0.find(class_="name").get_text()
# print(event_name)
