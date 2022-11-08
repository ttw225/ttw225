FROM python:3.10-slim

# Setting Language Environment Variables
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Update pip3 to the latest version
RUN python3 -m pip install --upgrade pip

# Install dependencies
RUN pip3 install --upgrade pipenv
COPY cat_readme/Pipfile Pipfile
COPY cat_readme/Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --system

# Copy src files
COPY README.md /
COPY cat_readme/ /src
WORKDIR /src

# Create User
RUN useradd -ms /bin/bash user
RUN chown -R user:user /README.md
RUN chown -R user:user /src
USER user

# Default Command
ENTRYPOINT [ "python3", "src/build_readme.py" ]
CMD [ "cat|eat|Can" ]

