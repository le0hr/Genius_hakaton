import requests

def get_buildings_from_osm(city_name="Kyiv", district="Podil"):
    # Запит: знайти всі житлові будинки в межах вказаної зони
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    area[name="{city_name}"]->.searchArea;
    (
      way["building"="apartments"](area.searchArea);
      way["building"="house"](area.searchArea);
      way["building"="civic"](area.searchArea);
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    
    buildings = []
    for element in data['elements'][:15]: # Беремо перші 15 для тесту
        addr = element.get('tags', {}).get('addr:street', 'Невідома вулиця')
        num = element.get('tags', {}).get('addr:housenumber', '?')
        b_type = element['tags'].get('building')
        buildings.append(f"{addr}, {num} ({b_type})")
    return buildings