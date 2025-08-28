FROM continuumio/miniconda3

COPY environment.yml .
RUN conda env create -f environment.yml

CMD ["conda", "run", "--no-capture-output", "-n", "csci-716-final-project", "python", "project/main.py"]