# Run Django code in window os

## Step 1: python installation
- Setup python with vscode for window: https://www.youtube.com/watch?v=cUAK4x_7thA
- Check python version and pip version:
```
    python --version
    pip --version
```

## Step 2: Using virtualenv
*Reference*: https://www.youtube.com/watch?v=yG9kmBQAtW4

- Install virtualenv and activate:
```
    pip install virtualenv
    python -m venv env
    env\Scripts\activate
```
**Important**:
- Make sure you on the correct folder before running those command above.
- if you meet up with the error "running scripts is disabled on this system", [try this](https://www.stanleyulili.com/powershell/solution-to-running-scripts-is-disabled-on-this-system-error-on-powershell/).



## Step 3: running program
- Install the needed library
```    
    pip install -r requirements.txt
```
- Run django server
```
    python manage.py runserver
```

