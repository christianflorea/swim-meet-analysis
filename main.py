import requests
import random
import re
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
import config
import matplotlib.pyplot as plt
import json
import os
import numpy as np

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
        self.team_points = {}

    def get_points(self, teams_in_meet, points_system, relay_mult):
        self.team_points = {team: 0 for team in teams_in_meet}
        points_mult = 1
        if self.type == "relay":
            points_mult = relay_mult
        for ath in self.athletes:
            if ath.place in points_system:
                # Athlete's team is found in the teams in meet
                if ath.team in self.team_points:
                    ath.points = points_system[ath.place] * points_mult
                    self.team_points[ath.team] += points_system[ath.place] * points_mult
                # Athleate's team is not found
                else:
                    find_alias = ""
                    for team in self.team_points.keys():
                        if team in ath.team or ath.team in team:
                            find_alias = team
                    # Alias for team found
                    if find_alias:
                        ath.points = points_system[ath.place] * points_mult
                        self.team_points[find_alias] += points_system[ath.place] * points_mult
                        print(f"\033[33mWARNING: {find_alias} alias used from {ath.team}\033[00m")
                    # Team not found
                    else:
                        print(f"\033[31mWCAUTION: {ath.team} not found in teams in meet\033[00m")

    def add_athlete(self, athlete: AthleteRanking):
        self.athletes.append(athlete)


class Meet:
    """
    Get data from swinrankings.net using Beautifulsoup library
    """

    def __init__(self, name:str , year:str , meet_id: str, points_system: dict, relay_mult: int, gender: int) -> None:
        self.name = name
        self.year = year
        self.meet_id = meet_id
        self.points_system = points_system
        self.relay_mult = relay_mult
        self.gender = gender
        self.results = dict()
        self.points = dict()

    def get_team_names(self) -> list:
        # Meet home page
        page = requests.get(
            f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={self.meet_id}&gender=1&styleId=0")
        # Scrape website
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
        if not os.path.exists(f"cache/{config.gender[self.gender]}-{self.year}-{self.name}.json"):
            print(f"CACHING MEET RESULTS -> {config.gender[self.gender]} {self.year} {self.name}")
            meet_results = []
            rdm = round(random.uniform(1.50, 3.50), 2)
            gender = config.gender[self.gender]
            
            # EVENT LOOP
            for event, id in config.swimming_event_id.items():

                if event in config.relay_events:
                    event_type = "relay"
                else:
                    event_type = "individual"

                # if id != 15 and id != 16:
                #     continue

                event_results = EventRanking(event, gender, event_type)
                print(f"\033[95m ***** Scraping Event: {gender}'s {event} ***** \033[00m")
                sleep(rdm)
                page = requests.get(f"https://www.swimrankings.net/index.php?page=meetDetail&meetId={self.meet_id}&gender={self.gender}&styleId={id}")
                soup = BeautifulSoup(page.content, 'html.parser')
                event_rows = soup.find("table", class_="meetResult")
                if not event_rows:
                    print(f"\033[33mWarning: Results for {gender}'s {event} not found\033[00m")
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
                    time = self.__try_parsing_time(time)

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
                for team in event_results.team_points.keys():
                    if team in self.points:
                        self.points[team] += event_results.team_points[team]
                    else:
                        self.points[team] = event_results.team_points[team]
                meet_results.append(event_results)
            
            
            for event in meet_results:
                self.results[event.name] = {"points": event.team_points, "results": []}
                for athlete in event.athletes:
                    self.results[event.name]["results"].append(athlete.__dict__)

            # Serializing json
            json_object = json.dumps({'points':self.points, 'results': self.results}, indent=4)
            # Writing to json
            with open(f"cache/{config.gender[self.gender]}-{self.year}-{self.name}.json", "w") as outfile:
                print(f"Writing to cache/{config.gender[self.gender]}-{self.year}-{self.name}.json")
                outfile.write(json_object)
        else:
            print(f"{self.year} {self.name} results found in cache")
        
        # Opening JSON file
        with open(f'cache/{config.gender[self.gender]}-{self.year}-{self.name}.json', 'r') as f:
            # Reading from json file
            json_object = json.load(f)
            self.results = json_object["results"]
            self.points = json_object["points"]
        return json_object

    def __try_parsing_time(self, text):
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


class Plotter:
    """
    """
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def get_tuple(points: list[int], index: int):
        tup = []
        for p in points:
            tup.append(p[index])
        return tuple(tup)

    def plot_points_by_stroke(self, name, results, points, teams=None):
        try:
            teams_to_plot = points.keys()
            if teams:
                teams_to_plot = list(set(teams) & set(points.keys()))
            team_pts = {team: [0] * 6 for team in teams_to_plot}
            for event in results.keys():
                i = -1
                if "Relay" not in event:
                    if "Fly" in event: i = 0
                    elif "Back" in event: i = 1
                    elif "Breast" in event: i = 2
                    elif "Free" in event: i = 3
                    elif "IM" in event: i = 4
                else:
                    i = 5
                for team, pts in results[event]["points"].items():
                    if team in teams_to_plot:
                        team_pts[team][i] += pts
            
            teams = tuple(team_pts.keys())
            points = {
                "Fly": self.get_tuple(team_pts.values(), 0),
                "Back": self.get_tuple(team_pts.values(), 1),
                "Breast": self.get_tuple(team_pts.values(), 2),
                "Free": self.get_tuple(team_pts.values(), 3),
                "IM": self.get_tuple(team_pts.values(), 4),
                "Relay": self.get_tuple(team_pts.values(), 5),
            }
            
            x = np.arange(len(teams))  # the label locations
            width = 0.1  # the width of the bars
            multiplier = 0

            fig, ax = plt.subplots(layout='constrained')

            for attribute, measurement in points.items():
                offset = width * multiplier
                rects = ax.bar(x + offset, measurement, width, label=attribute)
                ax.bar_label(rects, padding=4)
                ax.legend(loc='best', fontsize=10)
                multiplier += 1

            ax.set_ylabel('Points')
            ax.set_xlabel('Teams')
            ax.set_title(f'{name} Points by Stroke')
            ax.set_xticks(x + width, teams)
            plt.xticks(rotation=15)

            ax.legend(loc='upper left', ncols=3)
            ax.set_ylim(0, 600)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(e)

    def plot_meet_points(self, name, points, teams=None):
        try:
            teams_to_plot = points.keys()
            if teams:
                teams_to_plot = list(set(teams) & set(points.keys()))
            
            for team in points.keys():
                if team not in teams_to_plot:
                    del points[team]
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(list(points.keys()), list(points.values()))
            labels = ax.get_xticklabels()
            plt.setp(labels, rotation=45, horizontalalignment='right')
            ax.set(xlim=[0, 1400], xlabel='Total Points', ylabel='Team',
                title=f'{name} Overall Team Points')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(e)

    def plot_event_points(self, name, event, results, teams=None):
        try:
            teams_to_plot = results.keys()
            if teams:
                teams_to_plot = list(set(teams) & set(results.keys()))
            
            for team in results.keys():
                if team not in teams_to_plot:
                    del results[team]
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(list(results.keys()), list(results.values()))
            labels = ax.get_xticklabels()
            plt.setp(labels, rotation=45, horizontalalignment='right')
            ax.set(xlim=[0, 90], xlabel='Total Points', ylabel='Team',
                title=f'{name} Team Points for {event}')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(e)


if __name__ == "__main__":
    header = ["Place", "Name", "YOB", "Country",
              "Team", "Time", "FINA", "Meet Points"]
    oua = Meet(name="OUA", year="2022", meet_id="629800", 
        points_system=config.oua_points,relay_mult=2, gender=1)
    oua2023 = Meet(name="OUA", year="2023", meet_id="636201", 
        points_system=config.oua_points,relay_mult=2, gender=1)    
    divs = Meet(name="Divisionals", year="2022", meet_id="634465", 
        points_system=config.oua_points,relay_mult=2, gender=2)
    usports = Meet(name="USports", year="2023", meet_id="636410",
        points_system=config.usports_points, relay_mult=1, gender=1)

    meet = divs
    
    meet_results = meet.get_meet_results()
    meet_name = meet.name
    meet_gender = config.gender[meet.gender]
    meet_year = meet.year
    meet_title = f'{meet_year} {meet_gender} {meet_name}'
    
    plot = Plotter()
    plot.plot_points_by_stroke(
        name=meet_title,
        results=meet_results["results"], 
        points=meet_results["points"], 
        teams=[
            'University Of Toronto', 
            'Western University Swimming', 
            'University Of Waterloo', 
            'McMaster University'
        ])
    plot.plot_meet_points(name=meet_title, points=meet_results["points"])
    plot.plot_event_points(
        name=meet_title, 
        event="50 Free", 
        results=meet_results["results"]["50 Free"]["points"])
