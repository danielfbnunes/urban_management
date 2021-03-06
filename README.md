# urban_management
Urban Management is an API that allows users to report occurrences, update their status and search for created
occurrences based on some filters ([more details here](#the-api))

# Start project
In the root of the project:

1º - Make sure that no container is stopped by removing every service:
```shell
docker-compose down -v
```

2º - Build app service with the last changes:
```shell
docker-compose build app
```

3ª - Start the API connected to the database:
```shell
docker-compose up app
```

# Run tests
In the root of the project:

1º - Make sure that no container is stopped by removing every service:
```shell
docker-compose down -v
```

2º - Build app service with the last changes:
```shell
docker-compose build test
```

3ª - Start the API connected to the database:
```shell
docker-compose up test
```

# Users
When you start the project, an admin user will be already created with the following credentials:

Role    | Username | Password   |
:-----: | :------: | :--------: |
Admin   | admin    | admin12345 |

With these credentials, you can access [Django Admin](http://localhost:8000/admin) 

# The API
- [Here](https://www.getpostman.com/collections/fed832dd7554420136db) you can find a Postman collection with all the 
available endpoints;
- A `YES` on the `Token` column means that the a user with the `Role` specified must use the token provided when the
user authenticates on the API, through the `login` endpoint. This token should be used in the headers of the request
with the key `Authorization` followed by the value `Token <token key>`.
- The base url for the requests is http://localhost:8000.

| Role   | Token  | Method  | Endpoint              | Body / Params                                                                                   |
|:------:|:------:|:-------:|-----------------------|-------------------------------------------------------------------------------------------------|
| Anyone | NO     | POST    | login/                | Body: `{"username":<string>, "password":<string>}`                                              |
| Anyone | NO     | GET     | get_occurrence/       | Params: (`category`, `author__user__username`, `dist`, `point`)                                 |
| Author | YES    | POST    | add_occurrence/       | Body: `{"description":<string>, "latitude":<double>, "longitude":<double>, "category":<string>}`|
| Admin  | YES    | PUT     | update_occurrence/:id | Body: `{"status":<string>}`                                                                     |

**Note**: Description about the endpoints and the validation of fields can be found in the 
[Swagger documentation](http://localhost:8000/docs/).

# Use case
1. Start the project ([info](#start-project));
2. Login in django admin and create an author;
3. Authenticate with the credentials created for the author in the `/login` endpoint;
4. Use the token provided on step 3 to create an occurrence (`/add_occurrence`);
5. Verify if the occurrence was created in the `/get_occurrence` endpoint;
6. Authenticate with the credentials for the admin user ([info](#users)) in the `/login` endpoint;
7. Update the occurrence created using the occurrence id in the `update_occurrence/:id` endpoint (the id can be found
on step 3)
8. Verify if the occurrence was updated in the `/get_occurrence` endpoint;

# Testing

The project is currently integrated with [Circle CI](https://circleci.com/), which allows be to run the tests in an 
automated pipeline for each commit.

# Some notes
- It was my first time using Circle CI and I can say that the integration was quite easy and that the tool has some
pretty nice features, specially for a free solution;
- Django rest framework version is the **3.11.2** since the latest versions were having some unresolved conflicts with
the swagger documentation ([more info](https://github.com/encode/django-rest-framework/issues/7555))
