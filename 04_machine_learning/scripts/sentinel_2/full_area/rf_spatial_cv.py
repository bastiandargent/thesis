import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

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
    os.path.join(config["base_dir"], "03_processed", "sampling", "training_samples.csv")
)

# drop rows with NaNs
data = data.dropna()

# target variable
y = data["ML_Group"]

# predictors
X = data.drop(columns=["ML_Group", "grid_id"])

# spatial folds (1, 2, ..., 25)
folds = data["grid_id"].unique()

# saves results of all folds.
all_pred = []
all_true = []

feature_importances_list = []
feature_names = X.columns


for fold in folds:
    print(f"Fold {fold}")

    # separates 25 folds into training (24 folds) and test data (1 fold).
    # Each fold will be used once as test data once.
    train = data[data["grid_id"] != fold]
    test = data[data["grid_id"] == fold]

    # X are predictors, y are target variables (Geology Group labels).

    X_train = train.drop(columns=["ML_Group", "grid_id"])
    y_train = train["ML_Group"]

    X_test = test.drop(columns=["ML_Group", "grid_id"])
    y_test = test["ML_Group"]

    # RF init with default parameters
    model = RandomForestClassifier(
        n_estimators=500, random_state=42, max_features="sqrt", n_jobs=-1
    )

    # RF training with provided 24 folds.
    model.fit(X_train, y_train)

    # RF prediction of the one test fold.
    predictions = model.predict(X_test)
    print(predictions)

    all_pred.extend(predictions)
    all_true.extend(y_test)

    feature_importances_list.append(model.feature_importances_)


# confusion matrix results

labels = sorted(data["ML_Group"].unique())

cm = confusion_matrix(all_true, all_pred, labels=labels)
print(cm)

# Convert confusion matrix to DataFrame for readability

cm_df = pd.DataFrame(cm, index=labels, columns=labels)

print("\nConfusion Matrix (rows = reference, cols = prediction)")
print(cm_df)


report = classification_report(all_true, all_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()

# rename columns in report:
# precision = User's Accuracy
# recall = Producer's Accuracy
# f1-score = F1_score
report_df = report_df.rename(
    columns={
        "precision": "User_Accuracy",
        "recall": "Producer_Accuracy",
        "f1-score": "F1_score",
    }
)

print("\nMetrics:")
print(report_df[["User_Accuracy", "Producer_Accuracy", "F1_score", "support"]])

print("\nOverall Accuracy:", accuracy_score(all_true, all_pred))

# save confusion matrix + configs + RF parameters in new directory.

model_dir = os.path.join(
    config["base_dir"], "04_machine_learning", "results", config["project_name"]
)

os.makedirs(model_dir, exist_ok=True)

print(f"Saving results in: {model_dir}")

# confusion matrix + accuracy metrics
cm_df.to_csv(os.path.join(model_dir, "confusion_matrix.csv"))
report_df.to_csv(os.path.join(model_dir, "accuracy_metrics.csv"))

# raw feature importance table
fi_df = pd.DataFrame(feature_importances_list, columns=feature_names)
fi_df.to_csv(os.path.join(model_dir, "feature_importances.csv"))

# mean and std of feature importance across folds
fi_mean = fi_df.mean()
fi_std = fi_df.std()
fi_summary = pd.DataFrame({"mean_importance": fi_mean, "std_importance": fi_std})
fi_summary = fi_summary.sort_values(by="mean_importance", ascending=False)
fi_summary.to_csv(os.path.join(model_dir, "feature_importances_summary.csv"))

# Copy S2 config file
config_src = "/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml"
shutil.copy(config_src, os.path.join(model_dir, "config_s2.yaml"))
