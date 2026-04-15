Required repository configuration for Docker publishing:

- `DOCKERHUB_USERNAME` secret: Docker Hub login username
- `DOCKERHUB_TOKEN` secret: Docker Hub access token
- Optional `DOCKERHUB_NAMESPACE` repository variable: namespace/org for published images

Image names published by the workflow:

- `${DOCKERHUB_NAMESPACE}/riot-hub-backend`
- `${DOCKERHUB_NAMESPACE}/riot-hub-frontend`
