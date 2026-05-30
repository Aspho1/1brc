# 1BRC

## Python

There are 1 billion rows. Python. No external deps. 

As of writing this `pypy` supports python 3.11. Using pypy over cpython is an easy 15-50% reduced computation time (43s to 30s with the current setup). Could probably use JIT computations in the hot loop but that might count as an external package.

1. Get the repo

    ```sh
    git clone git@github.com:Aspho1/1brc.git
    cd 1brc
    uv init .
    ```

2. Install pypy (debianlike) and select it as the interpreter for this project.

    ```sh
    sudo apt install -y pypy3 
    uv run --python pypy 
    ```

3. Create the `data/measurements.csv` file

    ```sh
    uv run create_measurements_custom.py
    ```

4. Run the primary script:

    ```sh
    uv run parse_and_compute.py
    ```


## Julia

Always a pleasure to code in this language. Without much optimization down to 41 seconds. Still want to see if I can minimize decoding in the hotloop, read floats faster...  