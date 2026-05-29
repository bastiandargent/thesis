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
    os.path.join(config["base_dir"], "03_processed", "sampling", "training_samples_terrain_aug-sep_20m_scl_6_masked.csv")
)

# drop rows with NaNs
data = data.dropna()

# target variable
y = data["ML_Group"]

# keep terrain separately
terrain = data["terrain_1"]

# spatial folds (1, 2, ..., 25)
folds = data["grid_id"].unique()

# saves results of all folds.
all_pred = []
all_true = []

all_terrain = []

X = data.drop(columns=["ML_Group", "grid_id", "fid", "terrain_1"], errors="ignore")
feature_importances_list = []
feature_names = X.columns


for fold in folds:
    print(f"Fold {fold}")

    # separates 25 folds into training (24 folds) and test data (1 fold).
    # Each fold will be used once as test data once.
    train = data[data["grid_id"] != fold]
    test = data[data["grid_id"] == fold]

    # X are predictors, y are target variables (Geology Group labels).

    X_train = train.drop(columns=["ML_Group", "grid_id", "fid", "terrain_1"], errors="ignore")
    y_train = train["ML_Group"]

    X_test = test.drop(columns=["ML_Group", "grid_id", "fid", "terrain_1"], errors="ignore")
    y_test = test["ML_Group"]
    # keep terrain separately for evaluation later.
    terrain_test = test["terrain_1"]

    # RF init with default parameters
    model = RandomForestClassifier(
        n_estimators=500, random_state=42, max_features="sqrt", n_jobs=-1
    )

    # RF training with provided 24 folds.
    model.fit(X_train, y_train)

    # RF prediction of the one test fold.
    predictions = model.predict(X_test)

    all_pred.extend(predictions)
    all_true.extend(y_test)
    all_terrain.extend(terrain_test)

    feature_importances_list.append(model.feature_importances_)


results = pd.DataFrame(
    {"truth": all_true, "prediction": all_pred, "terrain": all_terrain}
)



def evaluation_terrain(df):
    """
    Evaluate model performance for a given
    terrain type (exposed or covered).
    """

    # confusion matrix results
    cm = confusion_matrix(df["truth"], df["prediction"])
    labels = sorted(data["ML_Group"].unique())
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    print("\nConfusion Matrix:")
    print(cm_df)

    report = classification_report(df["truth"], df["prediction"], output_dict=True)
    report_df = pd.DataFrame(report).transpose()

    report_df = report_df.rename(
        columns={
            "precision": "User_Accuracy",
            "recall": "Producer_Accuracy",
            "f1-score": "F1_score",
            "support": "num_samples",
        }
    )

    print("\nMetrics:")
    print(report_df[["User_Accuracy", "Producer_Accuracy", "F1_score", "num_samples"]])

    print("\nOverall Accuracy:", accuracy_score(df["truth"], df["prediction"]))

    return cm_df, report_df


cm_all, report_all = evaluation_terrain(results)

exposed = results[results["terrain"] == 1]
covered = results[results["terrain"] == 2]

cm_exp, report_exp = evaluation_terrain(exposed)
cm_cov, report_cov = evaluation_terrain(covered)

# save confusion matrix + configs + RF parameters in new directory.
model_dir = os.path.join(
    config["base_dir"], "04_machine_learning", "results", config["project_name"]
)

os.makedirs(model_dir, exist_ok=True)
print(f"\nSaving results in: {model_dir}")

# confusion matrix + accuracy metrics
cm_all.to_csv(os.path.join(model_dir, "confusion_matrix_overall.csv"))
report_all.to_csv(os.path.join(model_dir, "accuracy_metrics_overall.csv"))

# Save terrain
cm_exp.to_csv(os.path.join(model_dir, "confusion_matrix_exposed.csv"))
report_exp.to_csv(os.path.join(model_dir, "accuracy_metrics_exposed.csv"))

cm_cov.to_csv(os.path.join(model_dir, "confusion_matrix_covered.csv"))
report_cov.to_csv(os.path.join(model_dir, "accuracy_metrics_covered.csv"))

# raw feature importance table
fi_df = pd.DataFrame(feature_importances_list, columns=feature_names)
fi_df.to_csv(os.path.join(model_dir, "feature_importances.csv"))

# mean and std of feature importance across folds
fi_mean = fi_df.mean()
fi_std = fi_df.std()
fi_summary = pd.DataFrame({"mean_importance": fi_mean, "std_importance": fi_std})
fi_summary = fi_summary.sort_values(by="mean_importance", ascending=False)
fi_summary.to_csv(os.path.join(model_dir, "feature_importances_summary.csv"))

# Save config for reproducibility
config_src = "/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml"
shutil.copy(config_src, os.path.join(model_dir, "config_s2.yaml"))

print("\nDone!")
