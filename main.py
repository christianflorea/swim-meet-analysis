import requests
import random
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import string
import config
import database


class SwimRankingComms:
    """
    Get data from swinrankings.net using Beautifulsoup library
    """

    def __init__(self, meet_id: str) -> None:
        self.meet_id = meet_id
        url = f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={meet_id}&gender=1&styleId=0"

    @staticmethod
    def reformat_soup(soup) -> list:
        """"""
        result = []
        translator = str.maketrans("", "", string.punctuation)

        for item in soup.next_elements:
            # print(item)
            # print("\n")
            # Remove leading spaces
            if str(item)[0] == " ":
                item = item[1:]
            # Remove html tags
            if str(item)[-8:] == "</table>":
                break
            if str(item)[0] == "<":
                continue
            if str(item)[:9] == "GENERATED":
                break
            # Remove punctuation
            item = item.translate(translator)
            # Add team name to list
            result.append(item)
        return result

    def get_team_names(self) -> list:
        result = []
        # Meet home page
        page = requests.get(
            f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={self.meet_id}&gender=1&styleId=0")
        # Scale website
        soup = BeautifulSoup(page.content, 'html.parser')
        teams = soup.find("table").find(
            class_="meetResult0").find(class_="club")
        teams = self.reformat_soup(teams)
        # Return team names
        result = teams[::7]
        return result

    def get_team_points_by_event(self) -> dict:
        rdm = round(random.uniform(1.50, 4.00), 2)
        teams_in_meet = self.get_team_names()
        result = {team: [0, 0, 0] for team in teams_in_meet}
        for gender_id in range(1, 3):
            print(f"gender: {config.gender[gender_id]}")
            for event, id in config.swimming_event_id.items():
                # if id != 15:
                #     continue
                if id > 20:
                    points_mult = 2
                else:
                    points_mult = 1
                print(f"id: {id} - {event}")
                sleep(rdm)
                page = requests.get(
                    f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={self.meet_id}&gender={gender_id}&styleId={id}")
                soup = BeautifulSoup(page.content, 'html.parser')
                event_results = soup.find("table").find(class_="meetResult0")
                if event_results != None:
                    event_results = self.reformat_soup(event_results)
                else:
                    continue
                result_lines = zip(*(iter(event_results),) * 7)
                if "Split" in event_results[::7]:
                    # print("SPLIT")
                    continue
                if points_mult == 2:
                    # print(event_results)
                    result_lines = zip(*(iter(event_results),) * 12)
                    team_index = 1
                else:
                    result_lines = zip(*(iter(event_results),) * 7)
                    team_index = 4
                # print(teams_in_event)
                for line in result_lines:
                    # print(line)
                    # print(line[team_index])
                    if line[team_index] in teams_in_meet:
                        try:
                            int(line[0])
                        except:
                            pass
                            # print(f"Cannot turn {line[0]} into int")
                        else:
                            if int(line[0]) in config.oua_points.keys():
                                points = config.oua_points[int(line[0])]
                                print(
                                    f"Adding {points} points to {line[team_index]} for place {line[0]} and time {line[-2]}")
                                result[line[team_index]][0] += (points_mult *
                                                                points)
                                result[line[team_index]][gender_id] += (points_mult *
                                                                        points)
                    else:
                        pass
                        # print("placing not in dict")
        return result


# page = requests.get(
#     "https://www.swimrankings.net/index.php?page=meetDetail&meetId=634465&gender=1&styleId=17")
# soup = BeautifulSoup(page.content, 'html.parser')
# result_header = soup.find(class_="meetResultHead")

# event_name = result_header.find(class_="event").get_text()

# results = []
# line = {"place": "", "name": "", "team": ""}
# translator = str.maketrans("", "", string.punctuation)

# event0 = soup.find("table").find(class_="meetResult0")
# iterator = 0
# for element in event0.next_elements:
#     if str(element)[0] == " ":
#         element = element[1:]
#     if str(element)[0] == "<":
#         continue
#     iterator += 1
#     if str(element)[:9] == "GENERATED":
#         break
#     element = element.translate(translator)
#     if iterator % 7 == 1:
#         line["place"] = element
#         # print(f"Rank = {element}")
#     elif iterator % 7 == 2:
#         line["name"] = element
#         # print(f"Name = {element}")
#     elif iterator % 7 == 5:
#         line["team"] = element
#         # print(f"Team = {element}")
#     elif iterator % 7 == 0:
#         results.append(line)
#         # print(line)
#         line = {"place": "", "name": "", "team": ""}
#     else:
#         continue

# for result in results:
#     pass
    # print(result)

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

if __name__ == "__main__":
    oua = SwimRankingComms(meet_id="629800")
    divs = SwimRankingComms(meet_id="634465")
    print(divs.get_team_names())
    print(divs.get_team_points_by_event())
