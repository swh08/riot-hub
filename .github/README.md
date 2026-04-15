Required repository configuration for Docker publishing:

- `DOCKERHUB_USERNAME` secret: Docker Hub login username
- `DOCKERHUB_TOKEN` secret: Docker Hub access token
- Optional `DOCKERHUB_NAMESPACE` repository variable: namespace/org for published images

Image names published by the workflow:

- `${DOCKERHUB_NAMESPACE}/riot-hub-backend`
- `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`

Publish behavior:

- Pull requests only build-check the images and do not push
- Pushing to `main` automatically creates the next version tag using patch increments
- Versioning starts at `v0.1.0` when the repository has no prior `v*` tags
- Example: if the latest git tag is `v1.2.3`, the next release becomes `v1.2.4`
- Each release publishes two tags for each image:
  - `latest`
  - the new version tag, for example `v1.2.4`
