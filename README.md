# notebooks

Create a new virtual environment and install the dependencies.

```
python3 -m venv ~/envs/nbdev \
  && source ~/envs/nbdev/bin/activate \
  && pip install --upgrade pip
```

Install the dependencies:

```
pip3 install -r requirements.tx`
```

Execute a notebook using [Papermill](https://papermill.readthedocs.io/en/latest/usage-execute.html), e.g.:

```
papermill --progress-bar TrainTestSplit.ipynb -
```

Run jupyter in VM setup as:

```
jupyter notebook --no-browser --ip 10.211.55.5 --port 8888
```