# pokemon_api.py start
import requests

base_url = "https://pokeapi.co/api/v2/"
# API call to get the basic info of a pokemon, including its name, id, types, forms, abilities, and level-up moves for a specific generation.
def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")
# API call to get the evolutionary line of pokemon. We will use the species endpoint to get the URL for the evolution chain, and then make another call to get the full evolution data.
def get_pokemon_evo(url):
    species_request = requests.get(url)

    if species_request.status_code == 200:
        evo_id = species_request.json()
        evo_response = requests.get(evo_id["evolution_chain"]["url"])
        pokemon_evo = evo_response.json()
        return pokemon_evo
    else:
        print(f"Failed to retrieve data {species_request.status_code}")

def get_pokemon_gen():
    url = f"{base_url}/version-group/?limit=20"
    all_groups = [] # This is where we will store every result

    while url:
        response = requests.get(url)
        data = response.json()
        
        #  We extend our all_groups list with the results from this page. This way, we accumulate all the version groups across multiple pages of results.
        all_groups.extend(data["results"])
        
        #  We update the url variable to the next page of results. If there are no more pages, data["next"] will be None, and the loop will terminate.
        url = data["next"] 
        
        print(f"Fetched {len(all_groups)} groups so far...")

    version_dict = {group["name"]: group["url"] for group in all_groups}

    return version_dict

# pokemon_api.py ends here
