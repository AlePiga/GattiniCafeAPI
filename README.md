# 🐱 Gattini Cafe API

## Struttura del progetto

```
GattiniCafeAOI/
├── manage.py
├── gattini_cafe.db # database SQLite (fornito)
├── requirements.txt
├── README.md
├── .gitignore
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── cafe/
    ├── models.py # Categoria, Prodotto, Ordine, OrdineProdotto
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── permissions.py # IsAdminOrReadOnly, IsOwnerOrAdmin
    └── admin.py
```

---

## Installazione

### 1. Clona il repository e crea l'ambiente virtuale

```bash
git clone <URL_REPO>
cd ./GattiniCafeAPI

python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

### 2. Installa le dipendenze all'interno del venv

```bash
pip install -r requirements.txt
```

### 3. Configura il database

Assicurati che il file `gattini_cafe.db` sia nella root del progetto, poi:

```bash
python manage.py migrate
```

### 4. Crea un utente superuser

```bash
python manage.py createsuperuser
```
### 5. Avvia il server di sviluppo

```bash
python manage.py runserver
```

Il server sarà disponibile su `http://127.0.0.1:8000/`

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
