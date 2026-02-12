# Matcha Shop Beta

## Setup

git clone <repo_url>
cd matcha_shopbeta

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py runserver
