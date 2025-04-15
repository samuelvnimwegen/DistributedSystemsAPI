# Distributed Systems

This is the project of Samuel van Nimwegen for the university of antwerp.
## Correctness:
The following things are tested every push on GitHub actions on https://github.com/samuelvnimwegen/DistributedSystemsAPI/actions/runs/:
- The `./run_full_project.sh` together with `consume_api.py`
- All the tests
- The linting and type checking

**These will 100% certainly be fine in a neutral environment since they can run on GitHub actions**

## How to run
### Full Project
The best way to run it is:
```bash
# Set the API Key (you can skip this if you did it before)
export API_KEY="{Enter API Key}"

# Disable Postgres since we want to keep port 5432 clear
sudo systemctl disable postgresql
sudo systemclt stop postgresql

# Start Docker
sudo systemclt start docker

# Run the project
./run_full_project.sh
```
And the website will be on:
http://localhost:5173

The API will be on: http://localhost:5000/api/ and http://localhost/api/

The Website will here use the API and you will have the full project.

### Just the API
**Warning**: You will need to enter the password for the postgres user 2 times. 
This script will create a local database.
```bash
# Set the API Key (you can skip this if you did it before)
export API_KEY="{Enter API Key}"

# Run the project
./run_api.sh
```

### Just the API and you already have a database set up
```bash
# Go to the API
cd api/

# Make a virtual environment and install the requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the app
python python app.py --key {ENTER API KEY}
```

### Run the frontend
```bash
# Go to the frontend
cd frontend/

# Install & Run
npm install
npm run dev
```

### Run the script:
First, start the API, see `./run_api.sh`, `./run_api.sh` or the `run the app` section. Then do:
```bash
./run_script.sh
```



