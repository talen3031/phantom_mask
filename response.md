# Response
> The Current content is an **example template**; please edit it to fit your style and content.
## A. Required Information
### A.1. Requirement Completion Rate
- [O] 1.List all pharmacies open at a specific time and on a day of the week if requested.
  - Implemented at route/pharmacy.py.
- [O] 2.List all masks sold by a given pharmacy, sorted by mask name or price.
  - Implemented at route/mask.py.
- [O] 3.List all pharmacies with more or less than x mask products within a price range.
  - Implemented at route/pharmacy.py.
- [O] 4.The top x users by total transaction amount of masks within a date range.
  - Implemented at route/user.py.
- [O] 5.The total number of masks and dollar value of transactions within a date range.
  - Implemented at route/purchase.py.
- [O] 6.Search for pharmacies or masks by name, ranked by relevance to the search term.
  - Implemented at route/pharmacy.py.
- [O] 7.Process a user purchases a mask from a pharmacy, and handle all relevant data changes in an atomic transaction.
  - Implemented at route/purchase.py.
### A.2. API Document
Please read API documentation in [https://github.com/talen3031/phantom_mask/docs/API.md]

### A.3. Import Data Commands
Please run the commands to migrate the data into the database.

```bash
  python etl.py
```
Please run the commands to start API.

```bash
  python app.py
```
## B. Bonus Information

### B.1. Test Coverage Report

 Please check the test coverage report at [https://github.com/talen3031/phantom_mask/htmlcov/index.html].

You can run the test script by using the command below:

```bash
pytest
```
or

```bash
coverage run -m pytest
```

### B.2. Dockerized
- You can find my `Dockerfile` in the project root directory. 

On the local machine, please follow the commands below to build it.

```bash
  docker build -t phantom-mask-app .
  docker run -p 5000:5000 phantom-mask-app
# go inside the container, run the migrate data command.
  docker exec -it phantom-mask-app bash
  python etl.py

```



## C. Other Information

### C.1. ERD

My ERD is at [https://github.com/talen3031/phantom_mask/docs/ERD.png]

### C.2. Technical Document

For frontend programmer reading, please read [https://github.com/talen3031/phantom_mask/docs/API.md] to know how to operate those APIs.

- --
