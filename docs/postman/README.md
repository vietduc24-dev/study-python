# Postman

Import `workbudget.postman_collection.json` into Postman.

Regenerate after adding or changing API routes:

```bash
docker compose -f docker/docker-compose.local.yml exec dev-workbudget-app python scripts/generate_api_docs.py
```

The generator groups requests by FastAPI route tags. For example,
`tags=["auth"]` becomes an `auth` folder in Postman.

To sync the generated file to Postman automatically, set these variables in
`WorkBudget/.env.local` or `WorkBudget/.env.dev`:

```env
POSTMAN_API_KEY=
POSTMAN_COLLECTION_ID=
POSTMAN_SYNC_ENABLED=true
```

Then run the same generator command. When sync is enabled, it replaces the
configured Postman collection with the generated collection.
