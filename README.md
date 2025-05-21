# Distributed Systems

This is the project of Samuel van Nimwegen from the University of Antwerp for the Distributed Systems course.

## Correctness:
The following things are tested every push on GitHub actions on https://github.com/samuelvnimwegen/DistributedSystemsAPI/actions:
- The `./run_microservices_docker.sh` together with `consume_script.py`
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
sudo systemctl stop postgresql

# Start Docker
sudo systemctl start docker

# Run the project
./run_microservices_docker.sh
```
And the website will be on:
http://localhost

The API's will be on:
- http://localhost/api/movies
- http://localhost/api/users
- http://localhost/api/preferences
- http://localhost/api/activity

The Website will here use the API and you will have the full project.





