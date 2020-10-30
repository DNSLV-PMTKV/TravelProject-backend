# Travel Project

### How to run locally:

1. Create a Python 3.8.5 virtualenv

2. Install dependencies:
    ```
    pip install -r requirements/dev.txt
    ```

3. Create database
   ```
    createuser -d travelproject --superuser
    createdb -O travelproject travelproject
   ```

4. Create tables
    ```
    python manage.py migrate
    ```

5. Run the server
    ```
    python manage.py runserver
    ```