## Petrol Management System Written in Flask

## creating virtual environment

```{bash}
python3 -m venv venv
```

## Activating virtual environment

#### on windows

```{bash}
venv\Scripts\activate.bat
```

#### on linux
```{bash}
source venv/bin/activate
```

### create Database

```{python}
from src import db
from app import app

with app.app_context():
	db.create_all()
	
```
