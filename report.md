**First name:** Samuel

**Last name:** van Nimwegen



**Explain how your API follows the RESTful principles.**

First, let's dive into the REST URI design, which is a key aspect of RESTful APIs. 
#### REST URI design
- It describes resources, not applications: Every API call is perfectly human-readable and understandable. 
This is important since resources are the main focus of RESTful APIs. These should always be human-readable and understandable. 
Example: `/movies/favorite/`. Everyone knows immediately what this is going to return: A list of favorite movies.

- It should be short, this is the case since I don't know how else you could shorten every URI without losing readability and understandability.

- It is hackable up the tree: 
in for example: `/movies/{movie_id}/same_genres`, you can see what happens if you go back a level in the tree.
`/movies/{movie_id}/` is a movie, and `/movies` is a list of movies.
- It is meaningful: There is no terminology used in the API that is technical or not understandable. The most technical term used is `movie_id`, which is a common term.
- All the words are nouns
- The URIs are permanent, it will always do the same thing in the future. The movie IDs will also never swap
- Query arguments are only used for parameters
- There are no extensions in the URIs

#### RESTful API
- It has a base URI: http://localhost/api, the frontend: http://localhost:5173/
- It has an Internet media type for the data: mainly JSON and one Image
- It uses standard HTTP methods: POST, GET, PUT, DELETE
- There are no hypertext links needed in the API

#### Architecture
- It is possible to both run the frontend and api separately from each-other.
- All components just use JSONs to communicate with each other.
- It does not take advantage of caching, it is available, but never necessary to produce correct results.
- Caching is used for multiple API routes that will consistently give the same result for the same input.
- Layering: since you are just sending a request, it is impossible to see whether we are going through a nginx proxy or not (both run options are available)

**[Optional] Motivate your design decisions. Are there any designs you considered but decided not to implement? Why?**

- I was thinking about a separate authentication API,
but I decided against it since it would be a lot of work for not much gain is the main reason I decided against it.




**Discuss efficiency. How would you improve the performance optimization of your API?**

- I would use a framework like FastAPI, which is a lot faster than Flask. I would probably also implement a load balancer and a kubernetes cluster for large numbers of requests.



**Fault tolerance: Can your API handle faulty requests? If so, what kind of errors does it address, and how are they handled?**

- It uses strict parsers for the input, so it will always return a 400 (BAD REQUEST) error if the input is not correct.
The parser will return in the error message what is wrong with the input, so the user can fix it.
- If the authentication fails, it will return a 401 (UNAUTHORIZED) error. This is handled through cookies and not through authentication tokens, so it is not possible to get a 401 error if you are not logged in (unless your cookie timed out).
- It will return a 404 (NOT FOUND) error if the resource is not found. This is if the url is not correct or if the resource does not exist. 
- It will return a 500 (INTERNAL SERVER ERROR) error if there is an error in the server. 
- It is protected against CSRF attacks and returns 401 (UNAUTHORIZED) then.

**[Extension] Carefully discuss your extensions. Describe what you have added and why. If you implemented additional technologies or algorithms, explain what they do, and how they function.
Note: Your extensions will be primarily evaluated based on the report, so ensure that each extension is documented with sufficient depth.**

- I implemented a limiter for the API, to limit the number of requests.
The default config for this is found in `limiter.py`.
The main page API calls have a higher limit than the other API calls, since they are more important and more likely to be used.
The limiter is done through the `flask_limiter` package, which is a great package for this.
- I implemented a caching system for the API to cache the results of the API calls. 
This is done through the `flask_caching` package, which is a great package for this.
Not all routes are cached, since some routes are often updated (like favorite movies). The default cache time is 5 minutes, but this can be changed in the `cache.py` file.
- I implemented authentication using JSON Web Tokens. This is done through **Cookies**. This means you don't have to manually change these every time you do a request. Cookies are created when you sign up or sign in. This is done using the `flask_jwt_extended` library.
- I created login and signed up using a **Database and hashable passwords**. I used SQLAlchemy and SHA256 for this as hashing algorithm.
- I created database migrations, these are so that the database is automatically updated every run. This is done using `alembic`.
- I created a CI workflow to test whether the API is still working. This is visible in `.github/workflows/ci.yaml` and using `github secrets`. 
The results of the runs are visible on https://github.com/samuelvnimwegen/DistributedSystemsAPI/actions/runs/.
This also lints and typechecks the code for formatting mistakes using `pylint` and `mypy`.
- I created python testing for all the endpoints and functions, this also tested in the workflow using `pytest`.
- I created a frontend using `react-vite` in `typescript`.![img.png](img.png)
![img_1.png](img_1.png)
![img_2.png](img_2.png)
- I created a `docker compose` system using `nginx` for routing, a newly built `postgres database`.
- I created a docker setup for every service so that we have a **Distributed System** ;)



**How many hours did you spend on this assignment? (used for statistics)**

- Number of hours: 25
