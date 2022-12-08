import requests
import random
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import string
import config


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
        rdm = random.randint(3, 8)
        teams_in_meet = self.get_team_names()
        result = {team: [0, 0, 0] for team in teams_in_meet}
        for gender_id in range(1, 3):
            print(f"gender: {config.gender[gender_id]}")
            for event, id in config.swimming_event_id.items():
                # if id != 24:
                #     continue
                if id > 20:
                    points_mult = 2
                else:
                    continue
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
                if "Split" in event_results[::7]:
                    # print("SPLIT")
                    continue
                if points_mult == 2:
                    # print(event_results)
                    teams_in_event = event_results[1::12]
                else:
                    teams_in_event = event_results[4::7]
                # print(teams_in_event)
                place = 0
                for team in teams_in_event:
                    place += 1
                    if team in teams_in_meet:
                        if place in config.oua_points.keys():
                            # print(
                            #     f"Adding {config.oua_points[place]} points to {team}")
                            result[team][0] += (points_mult *
                                                config.oua_points[place])
                            result[team][gender_id] += (points_mult *
                                                        config.oua_points[place])
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
    print(oua.get_team_points_by_event())
