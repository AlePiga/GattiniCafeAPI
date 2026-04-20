import sqlite3

from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Categoria, Prodotto, Ordine, OrdineProdotto
from .serializers import (
    UserSerializer, RegisterSerializer,
    CategoriaSerializer, ProdottoSerializer,
    OrdineSerializer, CreaOrdineSerializer, StatoOrdineSerializer,
)
from .permissions import IsAdminOrReadOnly


def get_db_conn():
    """Connessione diretta a SQLite (per modelli managed=False)."""
    return sqlite3.connect(str(settings.DATABASES['default']['NAME']))


# ─────────────────────────── AUTH ────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Credenziali non valide.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'detail': 'Credenziali non valide.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'detail': 'Account disabilitato.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ─────────────────────────── CATEGORIE ───────────────────────

class CategoriaListCreateView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all().order_by('id')
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]


# ─────────────────────────── PRODOTTI ────────────────────────

class ProdottoListCreateView(generics.ListCreateAPIView):
    serializer_class = ProdottoSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Prodotto.objects.select_related('categoria').all().order_by('id')
        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        disponibile = self.request.query_params.get('disponibile')
        if disponibile and disponibile.lower() == 'true':
            qs = qs.filter(disponibile=1)
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(nome__icontains=search) | Q(descrizione__icontains=search))
        return qs


class ProdottoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prodotto.objects.select_related('categoria').all()
    serializer_class = ProdottoSerializer
    permission_classes = [IsAdminOrReadOnly]


# ─────────────────────────── ORDINI ──────────────────────────

class OrdineListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            qs = Ordine.objects.all()
        else:
            qs = Ordine.objects.filter(utente=request.user)

        # Filtro per data (bonus)
        data_da = request.query_params.get('data_da')
        data_a = request.query_params.get('data_a')
        if data_da:
            qs = qs.filter(data_ordine__gte=data_da)
        if data_a:
            qs = qs.filter(data_ordine__lte=data_a + ' 23:59:59')

        qs = qs.prefetch_related('ordineprodotto_set__prodotto').select_related('utente').order_by('-id')
        return Response(OrdineSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CreaOrdineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        note = serializer.validated_data.get('note', '') or None
        prodotti_data = serializer.validated_data['prodotti']

        # Calcolo totale
        totale = 0.0
        for item in prodotti_data:
            prodotto = Prodotto.objects.get(id=item['prodotto_id'])
            totale += prodotto.prezzo * item['quantita']

        # Inserimento diretto via sqlite3 (modelli managed=False)
        conn = get_db_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO ordine (utente_id, data_ordine, stato, totale, note) "
                "VALUES (?, datetime('now'), 'in_attesa', ?, ?)",
                (request.user.id, totale, note)
            )
            ordine_id = cur.lastrowid
            for item in prodotti_data:
                cur.execute(
                    "INSERT INTO ordine_prodotto (ordine_id, prodotto_id, quantita) VALUES (?, ?, ?)",
                    (ordine_id, item['prodotto_id'], item['quantita'])
                )
            conn.commit()
        finally:
            conn.close()

        ordine = Ordine.objects.prefetch_related('ordineprodotto_set__prodotto').get(id=ordine_id)
        return Response(OrdineSerializer(ordine).data, status=status.HTTP_201_CREATED)


class OrdineDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_ordine(self, pk, user):
        try:
            ordine = Ordine.objects.prefetch_related(
                'ordineprodotto_set__prodotto'
            ).select_related('utente').get(pk=pk)
        except Ordine.DoesNotExist:
            return None, Response({'detail': 'Ordine non trovato.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_staff and ordine.utente != user:
            return None, Response({'detail': 'Non autorizzato.'}, status=status.HTTP_403_FORBIDDEN)
        return ordine, None

    def get(self, request, pk):
        ordine, err = self._get_ordine(pk, request.user)
        if err:
            return err
        return Response(OrdineSerializer(ordine).data)


class OrdineStatoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            ordine = Ordine.objects.get(pk=pk)
        except Ordine.DoesNotExist:
            return Response({'detail': 'Ordine non trovato.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StatoOrdineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conn = get_db_conn()
        try:
            conn.execute(
                "UPDATE ordine SET stato = ? WHERE id = ?",
                (serializer.validated_data['stato'], pk)
            )
            conn.commit()
        finally:
            conn.close()

        ordine = Ordine.objects.prefetch_related('ordineprodotto_set__prodotto').get(pk=pk)
        return Response(OrdineSerializer(ordine).data)


# ─────────────────────────── ADMIN STATS (BONUS) ─────────────

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        stati = ['in_attesa', 'in_preparazione', 'completato', 'annullato']
        ordini_per_stato = {s: Ordine.objects.filter(stato=s).count() for s in stati}

        conn = get_db_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.nome, SUM(op.quantita) as totale_venduto
                FROM ordine_prodotto op
                JOIN prodotto p ON p.id = op.prodotto_id
                JOIN ordine o ON o.id = op.ordine_id
                WHERE o.stato != 'annullato'
                GROUP BY p.id, p.nome
                ORDER BY totale_venduto DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            prodotto_top = {'nome': row[0], 'quantita_totale': row[1]} if row else None

            cur.execute("""
                SELECT COALESCE(SUM(totale), 0)
                FROM ordine
                WHERE date(data_ordine) = date('now')
                AND stato != 'annullato'
            """)
            incasso_oggi = cur.fetchone()[0]
        finally:
            conn.close()

        return Response({
            'ordini_per_stato': ordini_per_stato,
            'prodotto_piu_venduto': prodotto_top,
            'incasso_totale_oggi': round(incasso_oggi, 2),
        })
