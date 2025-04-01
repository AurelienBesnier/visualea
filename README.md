# OpenAlea.Visualea

[![Last version](https://anaconda.org/openalea3/openalea.visualea/badges/version.svg)](https://anaconda.org/OpenAlea3/openalea.visualea/files)
[![Documentation Status](https://readthedocs.org/projects/visualea/badge/?version=latest)](https://visualea.readthedocs.io/en/latest/?badge=latest)
[![Licence](https://anaconda.org/openalea3/openalea.visualea/badges/license.svg)](https://cecill.info/licences/Licence_CeCILL_V2.1-en.html)
[![Platform](https://anaconda.org/openalea3/openalea.visualea/badges/platforms.svg)](https://anaconda.org/openalea3/openalea.visualea)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![Downloads](https://anaconda.org/openalea3/openalea.visualea/badges/downloads.svg)](https://anaconda.org/openalea3/openalea.visualea)

OpenAlea.Visualea is an application that allows to use OpenAlea packages 
and to build dataflow graphically.


## License

OpenAlea.Visualea is released under a Cecill v2 license.

See LICENSE.txt
Nota : Cecill v2 license is a GPL compatible license.


## Dependencies

- Python >= 3.8
- Qt >= 5.12	  
- QtPy (PyQt >= 5.12)	    


## Installation user mode

```bash
mamba install openalea.visualea -c openalea3 -c conda-forge  
```

## Installation dev mode

- Create a conda environment 
    
    ```
    mamba env create -n visualea -f conda/environment.yml
    mamba activate visualea  
    ```

- clone from the openalea org

    1 core  
    2 grapheditor  
    3 openalea-components  
    4 visualea

- Checkout the visualea branch  
    `pip install -e .`
