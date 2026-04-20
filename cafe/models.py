from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.TextField(unique=True)
    descrizione = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'categoria'
        managed = False

    def __str__(self):
        return self.nome


class Prodotto(models.Model):
    nome = models.TextField()
    descrizione = models.TextField(null=True, blank=True)
    prezzo = models.FloatField()
    disponibile = models.IntegerField(default=1)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        db_column='categoria_id'
    )
    immagine_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'prodotto'
        managed = False

    def __str__(self):
        return self.nome


class Ordine(models.Model):
    STATO_CHOICES = [
        ('in_attesa', 'In Attesa'),
        ('in_preparazione', 'In Preparazione'),
        ('completato', 'Completato'),
        ('annullato', 'Annullato'),
    ]

    utente = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='utente_id'
    )
    data_ordine = models.TextField(default='CURRENT_TIMESTAMP')
    stato = models.TextField(default='in_attesa', choices=STATO_CHOICES)
    totale = models.FloatField(default=0.0)
    note = models.TextField(null=True, blank=True)
    prodotti = models.ManyToManyField(
        Prodotto, through='OrdineProdotto', related_name='ordini'
    )

    class Meta:
        db_table = 'ordine'
        managed = False

    def __str__(self):
        return f'Ordine #{self.id} - {self.utente.username}'


class OrdineProdotto(models.Model):
    ordine = models.ForeignKey(
        Ordine, on_delete=models.CASCADE, db_column='ordine_id'
    )
    prodotto = models.ForeignKey(
        Prodotto, on_delete=models.CASCADE, db_column='prodotto_id'
    )
    quantita = models.IntegerField(default=1)

    class Meta:
        db_table = 'ordine_prodotto'
        managed = False

    def __str__(self):
        return f'{self.quantita}x {self.prodotto.nome} in Ordine #{self.ordine.id}'
