Required repository configuration for Docker publishing:

- `DOCKERHUB_USERNAME` secret: Docker Hub login username
- `DOCKERHUB_TOKEN` secret: Docker Hub access token
- Optional `DOCKERHUB_NAMESPACE` repository variable: namespace/org for published images

Image names published by the workflow:

- `${DOCKERHUB_NAMESPACE}/riot-hub-backend`
- `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`

Publish behavior:

- Pull requests only build-check the images and do not push
- Pushing a tag like `v1.2.3` publishes two tags for each image:
  - `latest`
  - `v1.2.3`
- Manual runs also publish using the selected Git ref
