from sklearn.pipeline import Pipeline
from src.fraud_data_preprocessor import FraudDataPreprocessor  # ВАЖНО: этот импорт должен быть до joblib.load!
import joblib


import pandas as pd
from sklearn.utils import resample

def temporal_split_and_balance(df, time_col, target_col, test_size=0.2):
    # 1. Сортируем по времени
    df_sorted = df.sort_values(time_col).reset_index(drop=True)
    
    # 2. Делим на train и test по времени
    n_test = int(len(df_sorted) * test_size)
    test = df_sorted.iloc[-n_test:]
    train = df_sorted.iloc[:-n_test]
    
    def balance_classes(data, target_col):
        min_count = data[target_col].value_counts().min()
        # Берём min_count объектов каждого класса
        fraud = data[data[target_col] == 1].sample(n=min_count, random_state=42)
        not_fraud = data[data[target_col] == 0].sample(n=min_count, random_state=42)
        balanced = pd.concat([fraud, not_fraud]).sample(frac=1, random_state=42)
        return balanced

    # 3. Балансируем train и test
    train_bal = balance_classes(train, target_col)
    test_bal  = balance_classes(test, target_col)
    
    print("Train balanced shape:", train_bal.shape)
    print("Test  balanced shape:", test_bal.shape)
    print('Train isFraud mean:', train_bal[target_col].mean())
    print('Test  isFraud mean:', test_bal[target_col].mean())
    return train_bal, test_bal

if __name__ == "__main__":

    train = pd.read_csv('./data/test_transactions.csv')
  
    categorical_features = [
        'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6',
        'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain', 'DeviceType', 'DeviceInfo'
    ]
    identity_categoricals = [col for col in train.columns if col.startswith('id_')]
    categorical_features += identity_categoricals
    m_features = [col for col in train.columns if col.startswith('M')]
    categorical_features += m_features
    categorical_features = [col for col in categorical_features if col in train.columns]
    categorical_features
  

    # Использование
    data_train, data_test = temporal_split_and_balance(train, time_col="TransactionDT", target_col="isFraud")



  

    pipeline = Pipeline([
        ('preprocessor', FraudDataPreprocessor(categorical_features=categorical_features))
    ])

    pipeline.fit(data_train)
    joblib.dump(pipeline, './preprocessor/fraud_pipeline.joblib')