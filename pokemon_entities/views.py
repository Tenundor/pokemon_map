import folium

from django.http import HttpResponseNotFound
from django.shortcuts import render

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = 'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832&fill=transparent'


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


def get_image_url(request, image, default_image_url):
    if image:
        return request.build_absolute_uri(image.url)
    return default_image_url


def request_pokemon_entities(pokemon):
    requested_pokemon_entities = []
    for entity in pokemon.entities.all():
        requested_pokemon_entities.append(
            {
                'level': entity.level,
                'lat': entity.latitude,
                'lon': entity.longitude,
            }
        )
    return requested_pokemon_entities


def request_evolution(request, evolution, default_image_url):
    image_url = get_image_url(request, evolution.image, default_image_url)
    return {
            'title_ru': evolution.title,
            'pokemon_id': evolution.id,
            'img_url': image_url,
        }


def request_previous_evolution(request, pokemon, default_image_url):
    previous_evolution = pokemon.previous_evolution
    if previous_evolution:
        return request_evolution(request, previous_evolution,
                                 default_image_url)


def request_next_evolution(request, pokemon, default_image_url):
    next_evolutions = pokemon.next_evolution.all()
    if next_evolutions:
        next_evolution = next_evolutions[0]
        return request_evolution(request, next_evolution, default_image_url)


def request_pokemon(request, pokemon_id, default_image_url):
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')
    image_url = get_image_url(request, pokemon.image, default_image_url)
    pokemon_entities = request_pokemon_entities(pokemon)
    previous_evolution = request_previous_evolution(request, pokemon,
                                                    default_image_url)
    next_evolution = request_next_evolution(request, pokemon,
                                            default_image_url)
    return {
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': image_url,
        'entities': pokemon_entities,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution,
    }


def show_all_pokemons(request):
    pokemons = Pokemon.objects.all()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemons_on_page = []
    for pokemon in pokemons:
        pokemon_entities = PokemonEntity.objects.filter(pokemon=pokemon)
        image_url = get_image_url(request, pokemon.image, DEFAULT_IMAGE_URL)
        for pokemon_entity in pokemon_entities:
            add_pokemon(
                folium_map,
                pokemon_entity.latitude,
                pokemon_entity.longitude,
                image_url,
            )
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': image_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = request_pokemon(request, pokemon_id, DEFAULT_IMAGE_URL)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon['entities']:
        add_pokemon(
            folium_map, pokemon_entity['lat'], pokemon_entity['lon'],
            pokemon['img_url'])

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon,
    })
