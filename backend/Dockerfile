FROM continuumio/miniconda3

COPY ./opensky-api/ /app/opensky-api/
COPY ./backend/environment.yml .
RUN conda env create -f environment.yml

CMD ["conda", "run", "--no-capture-output", "-n", "csci-716-final-project", "python", "main.py"]