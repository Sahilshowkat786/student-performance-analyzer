"""Small, database-backed linear regression model for student performance."""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = (
    "attendance",
    "study_hours",
    "assignment",
    "previous_marks"
)
TARGET_COLUMN = "percentage"
MINIMUM_TRAINING_SAMPLES = 30
TEST_SIZE = 0.2
RANDOM_STATE = 42


def train_linear_regression(records):
    """Evaluate a holdout model and return a final model trained on all records."""

    sample_count = len(records)

    if sample_count < MINIMUM_TRAINING_SAMPLES:
        return {
            "ready": False,
            "sample_count": sample_count,
            "minimum_samples": MINIMUM_TRAINING_SAMPLES,
            "test_sample_count": 0,
            "mae": None,
            "r2": None,
            "model": None
        }

    features = [
        [float(record[column]) for column in FEATURE_COLUMNS]
        for record in records
    ]
    targets = [float(record[TARGET_COLUMN]) for record in records]

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        targets,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    evaluation_model = LinearRegression()
    evaluation_model.fit(x_train, y_train)

    test_predictions = evaluation_model.predict(x_test)
    mae = mean_absolute_error(y_test, test_predictions)
    r2 = r2_score(y_test, test_predictions)

    final_model = LinearRegression()
    final_model.fit(features, targets)

    return {
        "ready": True,
        "sample_count": sample_count,
        "minimum_samples": MINIMUM_TRAINING_SAMPLES,
        "test_sample_count": len(y_test),
        "mae": float(mae),
        "r2": float(r2),
        "model": final_model
    }
