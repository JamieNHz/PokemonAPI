import requests

base_url = "https://pokeapi.co/api/v2/"

def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")

def get_pokemon_evo(url):
    species_request = requests.get(url)

    if species_request.status_code == 200:
        evo_id = species_request.json()
        evo_response = requests.get(evo_id["evolution_chain"]["url"])
        pokemon_evo = evo_response.json()
        return pokemon_evo
    else:
        print(f"Failed to retrieve data {species_request.status_code}")

def get_all_pokemon_info():
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        all_pokemon_data = response.json()
        return all_pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")

def get_pokemon_gen():
    url = f"{base_url}//version-group/?limit=20"
    all_groups = [] # This is where we will store every result

    while url:
        response = requests.get(url)
        data = response.json()
        
        # 1. Add the results from THIS page to our master list
        all_groups.extend(data["results"])
        
        # 2. Update the URL to the 'next' page link provided by the API
        url = data["next"] 
        
        print(f"Fetched {len(all_groups)} groups so far...")

    version_dict = {group["name"]: group["url"] for group in all_groups}

    return version_dict

