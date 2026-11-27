# data/

This project uses only **synthetic** datasets. They are generated on the fly
from fixed random seeds by `src/generate_data.py` (via scikit-learn's
`make_blobs`, `make_moons` and `make_circles`), so no data files need to be
stored or downloaded here.

The `.gitignore` excludes any `*.csv` / `*.npy` files placed in this folder.
