LendingClub AutoML - Flow example
---

Data sets:

    1) LendingClub_original.csv (or lendingclub.csv)
    
    2) LendingClub_processed.csv (or dataset.csv)
    
Scripts:

    1) preprocess_lending_club.py (or preprocess.py) - preprocessing script for the original data sets (dataset number 1).
     it then exports a csv file named like data set number 2 (one of the two names, depends by the version).
     
    2) knn.py, random_forest_classifier.py (or random_forest.py), xgb.py (or XGBoost.py) - these are model scripts, 
    they should receive as an input data set number 2. Each of them outputs  sklearn trained model.
    
    3) cnvrg_sklearn_helper.py - helper file for the models in scripts 2. Don't drop it!
    
Full flow: 
    
    [LendingClub_original.csv] -> [preprocess.py] -> [knn.py | xgb.py | random_forest.py] -> trained model is ready!