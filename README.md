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
When you start the project, an `admin` user will be already created with the following credentials:

Role    | Username | Password   |
:-----: | :------: | :--------: |
Admin   | admin    | admin12345 |

With this credentials, you can access [Django Admin](http://localhost:8000/admin) 

# The API
- [Here](https://www.getpostman.com/collections/fed832dd7554420136db) you can find a Postman collection with all the 
available endpoints;
- A `YES` on the `Token` column means that the a user with the `Role` specified must use the token provided when the
user authenticates in the API, through the `login` endpoint. This token should be used in the Headers of the request
with the key `Authorization` followed by the value `Token <token key>`.
- The base url for the requests is http://localhost:8000.

| Role   | Token  | Method  | Endpoint              | Body / Params                                                                                   |
|:------:|:------:|:-------:|-----------------------|:-----------------------------------------------------------------------------------------------:|
| Anyone | NO     | POST    | login/                | Body: `{"username":<string>, "password":<string>}`                                              |
| Anyone | NO     | GET     | get_occurrence/       | Params: (`category`, `author__user__username`, `dist`, `point`)                                 |
| Author | YES    | POST    | add_occurrence/       | Body: `{"description":<string>, "latitude":<double>, "longitude":<double>, "category":<string>}`|
| Admin  | YES    | PUT     | update_occurrence/:id | Body: `{"status":<string>}`                                                                     |

**Note**: Description about the endpoints and the validation of fields can be found in the [Swagger documentation]().