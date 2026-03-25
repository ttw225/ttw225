FROM python:3.14-slim

# Setting Language Environment Variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency manifests first (for layer caching)
COPY cat_readme/pyproject.toml /src/pyproject.toml
COPY cat_readme/uv.lock /src/uv.lock
WORKDIR /src

# Install runtime dependencies only (no dev tools)
RUN uv sync --frozen --no-dev --no-install-project

# Copy src files
COPY README.md /
COPY cat_readme/ /src

# Create User
RUN useradd -ms /bin/bash user
RUN chown -R user:user /README.md
RUN chown -R user:user /src
USER user

# Default Command
ENTRYPOINT [ "uv", "run", "--frozen", "--no-dev", "python3", "src/build_readme.py" ]
CMD [ "cat|eat|Can" ]

