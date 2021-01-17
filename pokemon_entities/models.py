from django.db import models


class Pokemon(models.Model):
    title = models.CharField('название на русском', max_length=200)
    title_en = models.CharField('название на английском', max_length=200,
                                null=True, blank=True)
    title_jp = models.CharField('название на японском', max_length=200,
                                null=True, blank=True)
    image = models.ImageField('изображение', upload_to='pokemon_images',
                              null=True, blank=True)

    description = models.TextField('описание', null=True, blank=True)
    previous_evolution = models.ForeignKey(
        'self',
        verbose_name='из кого эволюционировал',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_evolution',
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'вид покемона'
        verbose_name_plural = 'виды покемонов'


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        verbose_name='вид покемона',
        on_delete=models.CASCADE,
    )
    latitude = models.FloatField('широта')
    longitude = models.FloatField('долгота')
    appeared_at = models.DateTimeField('дата и время появления',
                                       null=True, blank=True)
    disappeared_at = models.DateTimeField('дата и время исчезнования',
                                          null=True, blank=True)
    level = models.IntegerField('уровень', null=True, blank=True)
    health = models.IntegerField('здоровье', null=True, blank=True)
    strength = models.IntegerField('сила', null=True, blank=True)
    defence = models.IntegerField('защита', null=True, blank=True)
    stamina = models.IntegerField('выносливость', null=True, blank=True)

    class Meta:
        verbose_name = 'покемон на карте'
        verbose_name_plural = 'покемоны на карте'



