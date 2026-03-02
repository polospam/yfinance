# yfinance
Python project to get stock financial information.

## Project setup and run
1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment:
  - Windows: `venv\Scripts\Activate.ps1`
  - Linux: `venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
<<<<<<< Updated upstream
4. Run: `uvicorn api.main:app --reload`
=======
4. Run: `uvicorn api/main:app --reload`
>>>>>>> Stashed changes
5. If added dependencies, add them to the requirements file: `pip freeze > requirements.txt`
6. Deactivate the virtual environment: `deactivate`