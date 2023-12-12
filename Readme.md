# Feedback management

This service is responsible for handling wine feedback operations within our infrastructure. It provides functionality for user to add, delete or update a feedback.

## Deployment Instructions

To deploy the feedback service, start by copying the example application configuration:

```sh
cp example.app.yml app.yml
```

Next, you need to update the following variables in the `.env` file:

```yml
USER_MICROSERVICES: "YOUR-URL-ADMIN"
SPANNER_INSTANCE: "YOUR-SPANNER_INSTANCE"
SPANNER_DATABASE: "YOUR-SPANNER_DATABASE"
```

Replace the placeholders (`YOUR-URL-USER-MANAGMENT`, `YOUR-SPANNER_INSTANCE`, and `YOUR-WINE-DATABASE`) with your actual service URL, Spanner instance name, and Spanner database name, respectively.

For a more comprehensive guide on deployment, including detailed steps and additional configurations, please refer to our [App Engine Deployment Guide](https://github.com/Vintellect/deploy_backend_guide/blob/fd5863fb17d5386cdf16eb43cf58b0c6b8cc571f/Microserivces_guide.md).
