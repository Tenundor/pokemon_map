import folium

from django.http import HttpResponseNotFound
from django.shortcuts import render

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = "https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832&fill=transparent"


def add_pokemon(folium_map, lat, lon, image_url):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # tooltip=name,  # disable tooltip because of folium encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):

    pokemons = Pokemon.objects.all()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon in pokemons:
        pokemon_entities = PokemonEntity.objects.filter(pokemon=pokemon)
        image = pokemon.image
        image_url = DEFAULT_IMAGE_URL
        if image:
            image_url = request.build_absolute_uri(image.url)
        for pokemon_entity in pokemon_entities:
            add_pokemon(
                folium_map,
                pokemon_entity.latitude,
                pokemon_entity.longitude,
                image_url,
            )

    pokemons_on_page = []
    for pokemon in pokemons:
        image = pokemon.image
        image_url = DEFAULT_IMAGE_URL
        if image:
            image_url = pokemon.image.url
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': image_url,
            'title_ru': pokemon.title,
        })

    return render(request, "mainpage.html", context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        requested_pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    image = requested_pokemon.image
    image_url = DEFAULT_IMAGE_URL
    if image:
        image_url = request.build_absolute_uri(requested_pokemon.image.url)

    pokemon = {
        "pokemon_id": requested_pokemon.id,
        "title_ru": requested_pokemon.title,
        "title_en": requested_pokemon.title_en,
        "title_jp": requested_pokemon.title_jp,
        "description": requested_pokemon.description,
        "img_url": image_url,
        "entities": [],
    }

    pokemon_entities = PokemonEntity.objects.filter(pokemon=requested_pokemon)

    for entity in pokemon_entities:
        pokemon["entities"].append(
            {
                "level": entity.level,
                "lat": entity.latitude,
                "lon": entity.longitude,
            }
        )

    previous_evolution = requested_pokemon.previous_evolution
    if previous_evolution:
        pokemon["previous_evolution"] = {
            "title_ru": previous_evolution.title,
            "pokemon_id": previous_evolution.id,
            "img_url": previous_evolution.image.url,
        }

    next_evolutions = requested_pokemon.next_evolution.all()
    if next_evolutions:
        next_evolution = next_evolutions[0]
        pokemon["next_evolution"] = {
            "title_ru": next_evolution.title,
            "pokemon_id": next_evolution.id,
            "img_url": next_evolution.image.url,
        }

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon['entities']:
        add_pokemon(
            folium_map, pokemon_entity['lat'], pokemon_entity['lon'], pokemon['img_url'])

    return render(request, "pokemon.html", context={'map': folium_map._repr_html_(),
                                                    'pokemon': pokemon})
