just create a requirements.txt

```
instagrapi
Pillow
python-dotenv
```
and a .env

```
IG_USERNAME=your_username
IG_PASSWORD=your_password
```
and run 


docker run -it --rm \
  -v "$(pwd)":/app \
  -w /app \
  --env-file .env \
  python:3.11-slim \
  bash -c "pip install --upgrade pip && pip install --upgrade instagrapi python-dotenv && python unfollow.py"
