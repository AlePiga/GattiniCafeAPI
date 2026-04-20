# 🐱 Gattini Cafe API

API REST per la gestione di menu e ordini del Gattini Cafe, la caffetteria felina di Pallino il Maine Coon.

Realizzata con **Django 4+**, **Django REST Framework** e autenticazione **JWT** via `djangorestframework-simplejwt`.

---

## Struttura del progetto

```
gattini_cafe_project/
├── manage.py
├── gattini_cafe.db          ← database SQLite (fornito)
├── requirements.txt
├── README.md
├── .gitignore
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── cafe/
    ├── models.py            ← Categoria, Prodotto, Ordine, OrdineProdotto
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── permissions.py       ← IsAdminOrReadOnly, IsOwnerOrAdmin
    └── admin.py
```

---

## Installazione

### 1. Clona il repository e crea il virtualenv

```bash
git clone <URL_REPO>
cd gattini_cafe_project

python -m venv venv
source venv/bin/activate        # Linux/macOS
# oppure: venv\Scripts\activate  # Windows
```

### 2. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configura il database

Assicurati che il file `gattini_cafe.db` sia nella root del progetto, poi:

```bash
python manage.py migrate
```

### 4. Crea un superuser admin

```bash
python manage.py createsuperuser
```

Oppure usa le credenziali di test già incluse (vedi sotto).

### 5. Avvia il server di sviluppo

```bash
python manage.py runserver
```

Il server sarà disponibile su `http://127.0.0.1:8000/`

---

## Credenziali admin per i test

| Campo    | Valore               |
| -------- | -------------------- |
| Username | `admin`              |
| Password | `Pallino2024!`       |
| Email    | `admin@gattini.cafe` |

---

## Endpoint disponibili

### Autenticazione

| Metodo | Endpoint                   | Auth | Descrizione                                |
| ------ | -------------------------- | ---- | ------------------------------------------ |
| POST   | `/api/auth/register/`      | No   | Registra un nuovo utente                   |
| POST   | `/api/auth/login/`         | No   | Login — restituisce access + refresh token |
| POST   | `/api/auth/token/refresh/` | No   | Rinnova l'access token                     |
| GET    | `/api/auth/me/`            | Sì   | Dati utente autenticato                    |

### Menu (pubblici)

| Metodo | Endpoint               | Descrizione                      |
| ------ | ---------------------- | -------------------------------- |
| GET    | `/api/categorie/`      | Lista categorie                  |
| GET    | `/api/categorie/{id}/` | Dettaglio categoria              |
| GET    | `/api/prodotti/`       | Lista prodotti (supporta filtri) |
| GET    | `/api/prodotti/{id}/`  | Dettaglio prodotto               |

**Query parameters per `/api/prodotti/`:**

- `?categoria=<id>` — filtra per categoria
- `?disponibile=true` — solo prodotti disponibili
- `?search=<testo>` — cerca per nome o descrizione

### Gestione menu (solo admin)

| Metodo    | Endpoint               | Descrizione        |
| --------- | ---------------------- | ------------------ |
| POST      | `/api/prodotti/`       | Crea prodotto      |
| PUT/PATCH | `/api/prodotti/{id}/`  | Modifica prodotto  |
| DELETE    | `/api/prodotti/{id}/`  | Elimina prodotto   |
| POST      | `/api/categorie/`      | Crea categoria     |
| PUT       | `/api/categorie/{id}/` | Modifica categoria |
| DELETE    | `/api/categorie/{id}/` | Elimina categoria  |

### Ordini (utente autenticato)

| Metodo | Endpoint                  | Descrizione                           |
| ------ | ------------------------- | ------------------------------------- |
| GET    | `/api/ordini/`            | Lista ordini (propri; tutti se admin) |
| POST   | `/api/ordini/`            | Crea nuovo ordine                     |
| GET    | `/api/ordini/{id}/`       | Dettaglio ordine                      |
| PATCH  | `/api/ordini/{id}/stato/` | Aggiorna stato (solo admin)           |

### Bonus

| Metodo | Endpoint            | Descrizione                                                             |
| ------ | ------------------- | ----------------------------------------------------------------------- |
| GET    | `/api/admin/stats/` | Statistiche: ordini per stato, prodotto più venduto, incasso del giorno |

---

## Esempi di chiamate API (curl)

### 1. Login e ottenimento token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Pallino2024!"}'
```

Risposta:

```json
{
  "user": { "id": 1, "username": "admin", "is_staff": true, ... },
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### 2. Lista prodotti filtrata per categoria con paginazione

```bash
curl "http://localhost:8000/api/prodotti/?categoria=1&disponibile=true"
```

### 3. Creazione ordine con JWT

```bash
curl -X POST http://localhost:8000/api/ordini/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "note": "Senza glutine!",
    "prodotti": [
      {"prodotto_id": 1, "quantita": 2},
      {"prodotto_id": 7, "quantita": 1}
    ]
  }'
```

### 4. Aggiornamento stato ordine (solo admin)

```bash
curl -X PATCH http://localhost:8000/api/ordini/1/stato/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"stato": "completato"}'
```

### 5. Statistiche admin

```bash
curl http://localhost:8000/api/admin/stats/ \
  -H "Authorization: Bearer <access_token>"
```

Risposta:

```json
{
	"ordini_per_stato": {
		"in_attesa": 2,
		"in_preparazione": 1,
		"completato": 5,
		"annullato": 0
	},
	"prodotto_piu_venduto": {
		"nome": "Cappuccino Baffi Bianchi",
		"quantita_totale": 14
	},
	"incasso_totale_oggi": 47.5
}
```

---

## Funzionalità implementate

- [x] Autenticazione JWT (register, login, refresh, me)
- [x] Endpoint pubblici menu (categorie + prodotti con filtri)
- [x] Endpoint admin protetti (CRUD su prodotti e categorie)
- [x] Endpoint ordini per utente autenticato
- [x] Calcolo automatico totale ordine (`prezzo × quantità`)
- [x] Paginazione (PAGE_SIZE=20, bonus)
- [x] Filtro ordini per data `?data_da=` / `?data_a=` (bonus)
- [x] Endpoint statistiche admin `/api/admin/stats/` (bonus)
- [x] CORS abilitato per client browser
