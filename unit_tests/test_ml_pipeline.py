import os
import sqlite3
import pytest
import pandas as pd
from sklearn.pipeline import Pipeline


from src.ml_pipeline import CarPricePipeline #

@pytest.fixture
def sample_data():
    """Provides a basic DataFrame matching the expected schema for training."""
    return pd.DataFrame({
        'make': ['Ford', 'Toyota', 'BMW', 'Ford'],
        'model': ['Fiesta', 'Corolla', '3 Series', 'Focus'],
        'year': [2018, 2019, 2020, 2017],
        'mileage': [30000, 25000, 15000, 40000],
        'price': [10000, 15000, 25000, 12000]
    })

@pytest.fixture
def temp_pipeline(tmp_path):
    """Provides a CarPricePipeline instance with a temporary save path."""
    model_path = tmp_path / "models" / "test_model.joblib"
    return CarPricePipeline(model_path=str(model_path))


def test_initialization():
    """Test that the pipeline initializes with correct defaults."""
    pipe = CarPricePipeline()
    assert pipe.model_path == 'models/final_model.joblib'
    assert pipe.pipeline is None

def test_build_pipeline(temp_pipeline):
    """Test that the internal _build_pipeline method returns a valid sklearn Pipeline."""
    sk_pipeline = temp_pipeline._build_pipeline()
    
    assert isinstance(sk_pipeline, Pipeline)
    assert 'preprocessor' in sk_pipeline.named_steps
    assert 'regressor' in sk_pipeline.named_steps

def test_fit(temp_pipeline, sample_data):
    """Test the fit method manually."""
    # Ensure it returns self
    result = temp_pipeline.fit(sample_data)
    
    assert result is temp_pipeline
    assert temp_pipeline.pipeline is not None
    # sklearn pipelines add a classes_ or similar attributes when fitted, 
    # but checking that it is no longer None confirms initialization
    
def test_load_and_prepare_data(tmp_path):
    """Test SQLite extraction and data cleaning logic."""
    # 1. Setup a temporary SQLite database
    db_path = tmp_path / "test_car_data.db"
    conn = sqlite3.connect(db_path)
    
    # 2. Create raw dummy data with 'id' and 'engine_size'
    raw_df = pd.DataFrame({
        'id': [1, 2],
        'make': ['Audi', 'VW'],
        'model': ['A4', 'Golf'],
        'engine_size': [2.0, 1.4],
        'price': [20000, 15000]
    })
    raw_df.to_sql('cars', conn, index=False)
    conn.close()
    
    # 3. Test the extraction
    pipe = CarPricePipeline()
    cleaned_df = pipe.load_and_prepare_data(str(db_path))
    
    # 4. Assertions
    assert 'id' not in cleaned_df.columns, "'id' column should be dropped"
    assert 'engine_size' not in cleaned_df.columns, "'engine_size' should be renamed"
    assert 'displacement' in cleaned_df.columns, "'engine_size' should be renamed to 'displacement'"
    assert len(cleaned_df) == 2

def test_train_and_save_model(temp_pipeline, sample_data):
    """Test the full train method which fits and saves the model to disk."""
    temp_pipeline.train(sample_data)
    
    # Check if the file was actually created on disk
    assert os.path.exists(temp_pipeline.model_path)

def test_load_model_and_predict(temp_pipeline, sample_data):
    """Test loading an existing model and running inference."""
    # 1. Train and save a model first
    temp_pipeline.train(sample_data)
    
    # 2. Create a fresh pipeline object pointing to the same file
    new_pipe = CarPricePipeline(model_path=temp_pipeline.model_path)
    
    # 3. Create input data (drop target variable)
    X_input = sample_data.drop('price', axis=1).iloc[[0]] 
    
    # 4. Predict (this should automatically trigger load_model inside predict())
    predictions = new_pipe.predict(X_input)
    
    assert new_pipe.pipeline is not None, "Pipeline should have been loaded from disk"
    assert len(predictions) == 1
    assert isinstance(predictions[0], float)

def test_load_model_file_not_found(tmp_path):
    """Test that loading a non-existent model raises the correct error."""
    bad_path = tmp_path / "does_not_exist.joblib"
    pipe = CarPricePipeline(model_path=str(bad_path))
    
    with pytest.raises(FileNotFoundError):
        pipe.load_model()