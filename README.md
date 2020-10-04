# urban_management
Urban Management is an API that allows users to report occurrences and update their status

# Start project
In the root of the project:

1º - Make sure that no container is stopped by removing every service:
```shell
docker-compose down -v
```

2º - Build app service with the last changes:
```shell
docker-compose build
```

3ª - Start the API connected to the database:
```shell
docker-compose up
```