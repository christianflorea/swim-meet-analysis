import requests
import random
import re
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas as pd
import config


class AthleteRanking:
    """
    """

    def __init__(
            self,
            place: int,
            name: str,
            yob: int,
            country: str,
            team: str,
            time: float,
            fina: int,
            points: float = 0) -> None:
        self.place = place
        self.name = name
        self.yob = yob
        self.country = country
        self.team = team
        self.time = time
        self.fina = fina
        self.points = points


class EventRanking:
    """
    """

    def __init__(self, name: str, gender: str, type: str) -> None:
        self.name = name
        self.gender = gender
        self.type = type
        self.athletes = []
        self.points = {}

    def get_points(self, teams_in_meet, points_system, relay_mult):
        self.points = {team: 0 for team in teams_in_meet}
        points_mult = 1
        if self.type == "relay":
            points_mult = relay_mult
        for ath in self.athletes:
            if ath.place in points_system:
                if ath.team in self.points:
                    ath.points = points_system[ath.place] * points_mult
                    self.points[ath.team] += points_system[ath.place] * \
                        points_mult
                else:
                    find_alias = ""
                    for team in self.points.keys():
                        if team in ath.team or ath.team in team:
                            find_alias = team
                    if find_alias:
                        ath.points = points_system[ath.place] * points_mult
                        self.points[find_alias] += points_system[ath.place] * \
                            points_mult
                        print(
                            f"\033[33mWARNING: {find_alias} alias used from {ath.team}\033[00m")
                    else:
                        print(
                            f"\033[31mWCAUTION: {ath.team} not found in teams in meet\033[00m")

    def add_athlete(self, athlete: AthleteRanking):
        self.athletes.append(athlete)


def try_parsing_time(text):
    for fmt in ('%M:%S.%f', '%S.%f'):
        try:
            t = datetime.strptime(text, fmt)
            return t.second + \
                t.minute*60 + t.microsecond/1000000
        except ValueError:
            pass
    if text == "DSQ" or text == "NT" or text == "DNS":
        return None
    raise ValueError('no valid time format found')


class Meet:
    """
    Get data from swinrankings.net using Beautifulsoup library
    """

    def __init__(self, meet_id: str, points_system: dict, relay_mult: int, gender: int) -> None:
        self.meet_id = meet_id
        self.points_system = points_system
        self.relay_mult = relay_mult
        self.gender = gender
        self.events = {}
        self.points = {}

    def get_team_names(self) -> list:
        # Meet home page
        page = requests.get(
            f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={self.meet_id}&gender=1&styleId=0")
        # Scale website
        soup = BeautifulSoup(page.content, 'html.parser')
        parse = soup.find("table", class_="meetSearch").find_all(
            "td", class_="club")
        teams = []
        for line in parse:
            team = line.find('a')
            if team:
                teams.append(team.text)
        return teams

    def get_meet_results(self) -> dict:
        meet_results = []
        rdm = round(random.uniform(1.50, 3.50), 2)
        gender = config.gender[self.gender]
        print(f"Gender: {gender} \n")
        # EVENT LOOP
        for event, id in config.swimming_event_id.items():

            if event in config.relay_events:
                event_type = "relay"
            else:
                event_type = "individual"

            # if id != 15 and id != 16:
            #     continue

            event_results = EventRanking(event, gender, event_type)
            print(
                f"\033[95m ***** Scraping Event: {gender}'s {event} ***** \033[00m")
            sleep(rdm)
            page = requests.get(
                f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={self.meet_id}&gender={self.gender}&styleId={id}")
            soup = BeautifulSoup(page.content, 'html.parser')
            event_rows = soup.find(
                "table", class_="meetResult")
            if not event_rows:
                print(
                    f"\033[33mWarning: Results for {gender}'s {event} not found\033[00m")
                continue
            event_rows = event_rows.find_all("tr")
            # EVENT PLACES LOOP
            for i in range(1, len(event_rows)):
                data = event_rows[i].find_all("td")

                if event_type == "individual":
                    place = data[0].text
                    name = data[1].text
                    yob = int(data[2].text)
                    country = data[3].text
                    team = data[4].text
                    time = data[5].text
                    fina = data[6].text
                else:
                    place = data[0].text
                    team = data[1].text
                    country = data[3].text
                    name = data[4].text
                    time = data[5].text
                    fina = data[6].text
                    yob = None

                if (re.findall(r'\d+', place)):
                    place = int((re.findall(r'\d+', place))[0])
                else:
                    place = None
                time = try_parsing_time(time)

                athlete = AthleteRanking(
                    place,
                    name,
                    yob,
                    country,
                    team,
                    time,
                    fina,
                )
                event_results.add_athlete(athlete)
            event_results.get_points(
                teams_in_meet=self.get_team_names(),
                points_system=self.points_system,
                relay_mult=self.relay_mult)
            for team in event_results.points.keys():
                if team in self.points:
                    self.points[team] += event_results.points[team]
                else:
                    self.points[team] = event_results.points[team]
            self.events[event_results.name] = event_results
            meet_results.append(event_results)
        return meet_results

    # def get_team_points(self, meet_results, points_system):
    #     teams_in_meet = self.get_team_names()
    #     results = {team: 0 for team in teams_in_meet}
    #     for event, event_result in meet_results.items():
    #         points_mult = 1
    #         if event in config.relay_events:
    #             points_mult = 2
    #         for athlete in event_result:
    #             place = int(re.findall(r'\d+', athlete[0]))
    #             if place in points_system:
    #                 points = points_system[place] * points_mult


if __name__ == "__main__":
    header = ["Place", "Name", "YOB", "Country",
              "Team", "Time", "FINA", "Meet Points"]
    oua = Meet(meet_id="629800", points_system=config.oua_points,
               relay_mult=2, gender=1)
    divs = Meet(meet_id="634465", points_system=config.oua_points,
                relay_mult=2, gender=1)
    usports = Meet(meet_id="636410",
                   points_system=config.usports_points, relay_mult=1, gender=1)

    with open("results.txt", 'w') as f:
        results = usports.get_meet_results()
        print(usports.points)
        for event in results:
            f.write(f"EVENT: {event.name}\n")
            table = []
            for athlete in event.athletes:
                table.append(athlete.__dict__.values())
            f.write(
                f"{tabulate(table, header, 'simple_grid')}\n")
