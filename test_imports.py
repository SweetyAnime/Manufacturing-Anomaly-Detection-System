import sys
print("Python version:", sys.version)

try:
    import flask
    print("Flask version:", flask.__version__)
    
    import pandas as pd
    print("Pandas version:", pd.__version__)
    
    import sklearn
    print("Scikit-learn version:", sklearn.__version__)
    
    import plotly
    print("Plotly version:", plotly.__version__)
    
    import numpy as np
    print("NumPy version:", np.__version__)
    
    print("\nAll packages imported successfully!")
    print("You can now run the Flask application with: python app.py")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install missing packages using: pip install -r requirements.txt")
