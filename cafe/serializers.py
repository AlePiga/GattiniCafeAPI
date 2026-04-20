from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Categoria, Prodotto, Ordine, OrdineProdotto


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Le password non coincidono.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descrizione']


class ProdottoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Prodotto
        fields = ['id', 'nome', 'descrizione', 'prezzo', 'disponibile',
                  'categoria', 'categoria_nome', 'immagine_url']


class OrdineProdottoSerializer(serializers.Serializer):
    prodotto_id = serializers.IntegerField()
    quantita = serializers.IntegerField(min_value=1, default=1)


class OrdineProdottoDetailSerializer(serializers.ModelSerializer):
    prodotto = ProdottoSerializer(read_only=True)

    class Meta:
        model = OrdineProdotto
        fields = ['prodotto', 'quantita']


class OrdineSerializer(serializers.ModelSerializer):
    prodotti_dettaglio = OrdineProdottoDetailSerializer(
        source='ordineprodotto_set', many=True, read_only=True
    )
    utente_username = serializers.CharField(source='utente.username', read_only=True)

    class Meta:
        model = Ordine
        fields = ['id', 'utente', 'utente_username', 'data_ordine', 'stato',
                  'totale', 'note', 'prodotti_dettaglio']
        read_only_fields = ['utente', 'totale', 'data_ordine', 'stato']


class CreaOrdineSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)
    prodotti = OrdineProdottoSerializer(many=True, min_length=1)

    def validate_prodotti(self, value):
        for item in value:
            try:
                prodotto = Prodotto.objects.get(id=item['prodotto_id'])
                if not prodotto.disponibile:
                    raise serializers.ValidationError(
                        f"Il prodotto '{prodotto.nome}' non è disponibile."
                    )
            except Prodotto.DoesNotExist:
                raise serializers.ValidationError(
                    f"Prodotto con id {item['prodotto_id']} non trovato."
                )
        return value


class StatoOrdineSerializer(serializers.Serializer):
    stato = serializers.ChoiceField(choices=[
        'in_attesa', 'in_preparazione', 'completato', 'annullato'
    ])
