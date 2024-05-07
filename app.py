import requests
import os
from pathlib import Path

headers = {
    "Accept": "application/json"
}

def pullTeamFromAPI(team_id):
    url=f'https://www.mariokartcentral.com/mkc/api/registry/teams/{team_id}'

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to download team {team_id}. Status code: {response.status_code}")
        return None
    
    return response.json()


def saveTeamLogoFromAPI(team_logo_id, team_name, team_id, tournament_id, progress_string):
    url = f'https://www.mariokartcentral.com/mkc/storage/{team_logo_id}'
    response = requests.get(url, stream=True)

    # Define the directory path and file path
    sanitized_team_name = team_name.strip("'")  # Remove extra quotes
    directory_path = Path(f"tournaments/{tournament_id}/{sanitized_team_name}")
    save_path = directory_path / "logo.png"

    # Ensure that the directory exists
    directory_path.mkdir(parents=True, exist_ok=True)

    # Check if the request was successful
    if response.status_code != 200:
        # Handle the error if the request failed
        print(f"{progress_string} Failed to download image for {team_name}. Status code: {response.status_code}")
        return None

    # Write the logo image to the file
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
    print(f"{progress_string} Logo from {team_name} successfully downloaded and saved to {save_path}")

def get_tournament_id():
    while True:
        try:
            user_input = input("Enter the tournament ID (integer only): ").strip()
            tournament_id = int(user_input)
            return tournament_id
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

tournament_id = get_tournament_id()
TOURNAMENT_API_ENDPOINT=f'https://www.mariokartcentral.com/mkc/api/events/{tournament_id}/registrations?order=RD&checked_in=all&verified=yes'


tourney_response=requests.get(TOURNAMENT_API_ENDPOINT, headers=headers)

if tourney_response.status_code != 200:
    # Handle the error if the request failed
    print(f"Failed to download logos for tournament id {tournament_id}. Status code: {tourney_response.status_code}")
    exit(1)

tourney_data = tourney_response.json()

print(f"Successfully pulled from tournament id {tournament_id}")

total_teams = len(tourney_data["data"])
iteration = 1

for team in tourney_data["data"]:

    progress_string = f'({iteration}/{total_teams})'

    primary_team_id = team["team_id"]
    primary_team_name = team["team_name"]

    primary_team_data = pullTeamFromAPI(primary_team_id)

    primary_team_image_id = primary_team_data["team_logo"].replace("\\", "")

    saveTeamLogoFromAPI(primary_team_image_id, primary_team_name, primary_team_id, tournament_id, progress_string)

    if(team["secondary_team"]):
        secondary_team_id = team["secondary_team_id"]
        secondary_team_name = team["secondary_team_name"]
        secondary_team_data = pullTeamFromAPI(secondary_team_id)
        secondary_team_image_id = secondary_team_data["team_logo"].replace("\\", "")
        saveTeamLogoFromAPI(secondary_team_image_id, secondary_team_name, secondary_team_id, tournament_id, progress_string)
    
    iteration = iteration + 1

print("Successfully pulled all team logos!")