# OpenAlea.Visualea

OpenAlea.Visualea is an application that allows to use OpenAlea packages 
and to build dataflow graphically.


## License

OpenAlea.Visualea is released under a Cecill v2 license.

See LICENSE.txt
Nota : Cecill v2 license is a GPL compatible license.


## Dependencies

- Python >= 3.7    
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
    `python setup.py develop`
