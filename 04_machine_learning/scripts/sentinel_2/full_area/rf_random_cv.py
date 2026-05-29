import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.model_selection import KFold

import os
import shutil
import yaml

with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)

# load training_samples.csv
data = pd.read_csv(
    "/home/basti/Documents/Lund/Master_Thesis/03_processed/sampling/bedrock_study_area/training_samples.csv"
)

# drop rows with NaNs
data = data.dropna()


# target variable
y = data["ML_Group"]
# predictors
X = data.drop(columns=["ML_Group", "grid_id"])


# Random K-Fold Cross Validation
# n_splits=10 means that the data will be split into 10 folds, and the model will be trained and tested 10 times, each time using a different fold as the test set and the remaining 9 folds as the training set.
# shuffle=True means that the data will be shuffled before splitting into folds, which helps to ensure that each fold is representative of the overall dataset.
# random_state=42 is used to ensure reproducibility of the results, meaning that the same random splits will be generated each time the code is run with this seed value.
kf = KFold(n_splits=10, shuffle=True, random_state=42)

print("Number of folds:", kf.get_n_splits())

# saves results of all folds
all_predictions = []
all_truth = []

feature_importances = []

# Loop through each fold and train/test the model
for fold, (train_index, test_index) in enumerate(kf.split(X), start=1):
    print(f"Fold {fold}")

    # separates data into training and test data based on the fold indices.
    train = data.iloc[train_index]
    test = data.iloc[test_index]

    X_train = train.drop(columns=["ML_Group", "grid_id"])
    y_train = train["ML_Group"]

    X_test = test.drop(columns=["ML_Group", "grid_id"])
    y_test = test["ML_Group"]


    # RF init with default parameters
    model = RandomForestClassifier(
        n_estimators=500, max_features="sqrt", random_state=42, n_jobs=-1
    )

    # RF training with provided training data.
    model.fit(X_train, y_train)

    # RF prediction with provided test data.
    predictions = model.predict(X_test)

    all_predictions.extend(predictions)
    all_truth.extend(y_test)

    feature_importances.append(model.feature_importances_)

    print("Fold finished\n")




# confusion matrix results

cm = confusion_matrix(all_truth, all_predictions)
print(cm)

labels = sorted(list(set(all_truth)))
cm_df = pd.DataFrame(cm, index=labels, columns=labels)

print("\nConfusion Matrix (rows = reference, cols = prediction)")
print(cm_df)



report = classification_report(all_truth, all_predictions, output_dict=True)
report_df = pd.DataFrame(report).transpose()

report_df = report_df.rename(
    columns={
        "precision": "User_Accuracy",
        "recall": "Producer_Accuracy",
        "f1-score": "F1_score",
    }
)

print("\n===== ACCURACY METRICS =====")
print(report_df[["User_Accuracy", "Producer_Accuracy", "F1_score", "support"]])

print("\nOverall Accuracy:", accuracy_score(all_truth, all_predictions))


feature_importances = np.mean(feature_importances, axis=0)

importance_df = pd.DataFrame(
    {"feature": X.columns, "importance": feature_importances}
).sort_values(by="importance", ascending=False)

print("\n===== FEATURE IMPORTANCE =====")
print(importance_df)


# save confusion matrix + configs + RF parameters in new directory.

model_dir = os.path.join(
    config["base_dir"],
    "04_machine_learning",
    "results",
    config["project_name"],
    "random_cv",
)

os.makedirs(model_dir, exist_ok=True)

print(f"Saving results in: {model_dir}")

# confusion matrix + accuracy metrics
cm_df.to_csv(os.path.join(model_dir, "confusion_matrix_random_cv.csv"))
report_df.to_csv(os.path.join(model_dir, "accuracy_metrics_random_cv.csv"))
importance_df.to_csv(os.path.join(model_dir, "feature_importance_random_cv.csv"))

# Copy S2 config file
config_src = "/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml"
shutil.copy(config_src, os.path.join(model_dir, "config_s2.yaml"))
