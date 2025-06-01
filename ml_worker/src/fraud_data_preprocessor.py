import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA

class FraudDataPreprocessor(BaseEstimator, TransformerMixin):
    """
    Улучшенный пайплайн для anti-fraud датасетов с возможностью явного указания категориальных признаков.
    """
    def __init__(
        self,
        drop_threshold_col=0.3,
        drop_threshold_row=0.5,
        skip_cols=['isFraud', 'TransactionID', 'TransactionDT'],
        categorical_features=None    # <-- новый параметр
    ):
        self.drop_threshold_col = drop_threshold_col
        self.drop_threshold_row = drop_threshold_row
        self.skip_cols = skip_cols if skip_cols is not None else []
        self.cols_to_drop_ = []
        self.label_encoders = {}
        self.numeric_medians = {}
        self.cat_cols_ = []
        self.time_features = ['Transaction_day', 'Transaction_hour', 'Transaction_weekday']
        self.min_transactiondt = None
        self.rare_label = 'RARE_CAT'
        self.rare_thresh = 10
        self.rare_labels_map = {}
        self.cat_count_maps = {}
        self.group_stats = {}
        self.lower_bound = None
        self.upper_bound = None
        self.base_num_cols_ = set()
        self.extra_num_cols_ = set()
        self.scaler = StandardScaler()
        self.v_cols_ = []
        self.v_pca = None
        self.v_pca_n_components_ = 0
        self.v_pca_scaler = None
        self.categorical_features = categorical_features

    def fit(self, X, y=None):
        df = X.copy()
        # Приведение типов для заданных категориальных признаков
        if self.categorical_features is not None:
            for col in self.categorical_features:
                if col in df.columns:
                    df[col] = df[col].astype('category')

        if 'isFraud' in df.columns:
            df = df.drop(columns=['isFraud'])

        self._drop_columns_by_missing_ratio(df)
        df = df.drop(columns=self.cols_to_drop_)
        df = self._drop_rows_by_missing_ratio(df)

        self._fit_categorical(df)
        self._fit_numerical(df)
        self._fit_time_features(df)
        self._fit_sum_features(df)

        if 'TransactionAmt' in df.columns:
            self.extra_num_cols_.add('log_TransactionAmt')
            self.extra_num_cols_.add('isOutlier')
        if 'TransactionAmt_binned' in df.columns:
            self.extra_num_cols_.add('TransactionAmt_binned')
        for col in ['card1', 'card4']:
            if col in df.columns and 'TransactionAmt' in df.columns:
                self.extra_num_cols_.add(f'TransactionAmt_to_mean_{col}')
                self.extra_num_cols_.add(f'TransactionAmt_to_std_{col}')

        self._fit_transaction_group_features(df)
        self._fit_v_pca_features(df)
        self._fit_v_pca_scaler(df)

        df_cat_trans = self._transform_categorical(df.copy())
        identity_nums = [col for col in df_cat_trans.columns if col.endswith('_count')]
        if identity_nums is not None:
            for col in identity_nums:
                self.extra_num_cols_.add(col)
        df_trans = df_cat_trans[identity_nums].copy()
        print(f'## df columns: {df_cat_trans.columns}')
        print(f'## identity_nums: {identity_nums}')
        print(f'## extra_num_cols_: {self.extra_num_cols_}')

        df_trans = self._transform_sum_features(df.copy())
        df_trans = self._transform_transaction_group_features(df_trans)
        self.full_num_cols_ = [col for col in list(self.base_num_cols_ | self.extra_num_cols_)
                               if col not in self.skip_cols and col in df_trans.columns]

        df_trans = self._fillna_numeric(df_trans, self.full_num_cols_)

        self.scaler.fit(df_trans[self.full_num_cols_])

        print(self.full_num_cols_)
        return self

    def transform(self, X):
        df = X.copy()
        # Приведение типов для заданных категориальных признаков
        if self.categorical_features is not None:
            for col in self.categorical_features:
                if col in df.columns:
                    df[col] = df[col].astype('category')

        y = None
        if 'isFraud' in df.columns:
            y = df['isFraud']
            df = df.drop(columns=['isFraud'])
        df = df.drop(columns=[col for col in self.cols_to_drop_ if col in df.columns], errors='ignore')
        df = self._drop_rows_by_missing_ratio(df)
        df = self._transform_categorical(df)
        df = self._transform_numerical(df)
        df = self._transform_time_features(df)
        df = self._transform_sum_features(df)
        df = self._transform_transaction_group_features(df)

        applied_num_cols = [col for col in list(self.full_num_cols_) if col in df.columns]
        print(f"### applied_num_cols: {applied_num_cols}")
        df = self._fillna_numeric(df, applied_num_cols)

        if np.isinf(df[applied_num_cols].to_numpy()).any():
            raise RuntimeError("Остались inf в числовых признаках!")
        if np.isnan(df[applied_num_cols].to_numpy()).any():
            raise RuntimeError("Остались nan в числовых признаках!")

        df[applied_num_cols] = self.scaler.transform(df[applied_num_cols])

        df = self._transform_v_pca_features(df)
        if hasattr(self, 'v_pca_scaler') and self.v_pca_scaler is not None:
            v_pca_cols = [col for col in df.columns if col.startswith('V_PCA_')]
            if v_pca_cols:
                df[v_pca_cols] = pd.DataFrame(
                    self.v_pca_scaler.transform(df[v_pca_cols]),
                    columns=v_pca_cols,
                    index=df.index
                )

        if y is not None:
            df['isFraud'] = y.loc[df.index]

        print("Inf in columns:", df[list(self.extra_num_cols_)].isin([np.inf, -np.inf]).any())
        print("NaN in columns:", df[list(self.extra_num_cols_)].isna().any())
        return df

    def _fillna_numeric(self, df, num_cols):
        for col in num_cols:
            if col in df.columns:
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                df[col] = df[col].fillna(0)
        return df

    def _drop_columns_by_missing_ratio(self, df):
        process_cols = [col for col in df.columns if col not in self.skip_cols]
        missing_ratio_col = df[process_cols].isnull().mean()
        self.cols_to_drop_ = missing_ratio_col[missing_ratio_col > self.drop_threshold_col].index.tolist()

    def _drop_rows_by_missing_ratio(self, df):
        process_cols = [col for col in df.columns if col not in self.skip_cols]
        missing_ratio_row = df[process_cols].isnull().mean(axis=1)
        return df.loc[missing_ratio_row <= self.drop_threshold_row]

    def _fit_categorical(self, df):
        process_cols = [col for col in df.columns if col not in self.skip_cols]
        self.cat_cols_ = df[process_cols].select_dtypes(include=['object', 'category']).columns.tolist()
        self.cat_count_maps = {}
        self.rare_labels_map = {}
        df[self.cat_cols_] = df[self.cat_cols_].astype(str)
        for col in self.cat_cols_:
            col_values = df[col].fillna('unknown')
            self.extra_num_cols_.add(f"{col}_count")

            value_counts = col_values.value_counts()
            rare_labels = value_counts[value_counts <= self.rare_thresh].index
            self.rare_labels_map[col] = set(rare_labels)
            col_values = col_values.replace(rare_labels, self.rare_label)
            if self.rare_label not in col_values.unique():
                col_values = pd.concat([col_values, pd.Series([self.rare_label])], ignore_index=True)
            le = LabelEncoder()
            le.fit(col_values)
            self.label_encoders[col] = le
            self.cat_count_maps[col] = col_values.value_counts(dropna=False)

    def _transform_categorical(self, df):
        for col in self.cat_cols_:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('unknown')
                df[col] = df[col].apply(lambda x: self.rare_label if x in self.rare_labels_map[col] else x)
                df[f"{col}_count"] = df[col].map(self.cat_count_maps[col]).fillna(0)
                le = self.label_encoders[col]
                df[col] = df[col].where(df[col].isin(le.classes_), self.rare_label)
                df[col] = le.transform(df[col])
        return df

    def _fit_numerical(self, df):
        process_cols = [col for col in df.columns if col not in self.skip_cols]
        num_cols = df[process_cols].select_dtypes(include='number').columns.tolist()
        for col in num_cols:
            median = df[col].median()
            self.numeric_medians[col] = median
            df[col] = df[col].fillna(median)
        self.base_num_cols_ = set(num_cols)

    def _transform_numerical(self, df):
        for col in self.base_num_cols_:
            if col in df.columns:
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                df[col] = df[col].fillna(self.numeric_medians[col])
        return df

    def _fit_time_features(self, df):
        if 'TransactionDT' in df.columns:
            self.min_transactiondt = df['TransactionDT'].min()
            rel_trx = df['TransactionDT'] - self.min_transactiondt
            df['Relative_TransactionDT'] = rel_trx
            df['Transaction_day'] = (rel_trx // (24 * 60 * 60)).astype(int)
            df['Transaction_hour'] = ((rel_trx // 3600) % 24).astype(int)
            df['Transaction_weekday'] = ((rel_trx // (3600*24)) % 7).astype(int)
            for f in self.time_features:
                if f in df.columns:
                    self.base_num_cols_.add(f)

    def _transform_time_features(self, df):
        if 'TransactionDT' in df.columns and self.min_transactiondt is not None:
            rel_trx = df['TransactionDT'] - self.min_transactiondt
            df['Relative_TransactionDT'] = rel_trx
            df['Transaction_day'] = (rel_trx // (24 * 60 * 60)).astype(int)
            df['Transaction_hour'] = ((rel_trx // 3600) % 24).astype(int)
            df['Transaction_weekday'] = ((rel_trx // (3600*24)) % 7).astype(int)
        return df

    def _fit_sum_features(self, df):
        if 'TransactionAmt' in df.columns:
            q1 = df['TransactionAmt'].quantile(0.25)
            q3 = df['TransactionAmt'].quantile(0.75)
            iqr = q3 - q1
            self.lower_bound = q1 - 1.5 * iqr
            self.upper_bound = q3 + 1.5 * iqr
            df['TransactionAmt_binned'] = pd.cut(
                df['TransactionAmt'],
                bins=[0, 100, 1000, 5000, 10000, np.inf],
                labels=['Low', 'Medium', 'High', 'Very High', 'Extremely High']
            ).astype(str).fillna('unknown')
            le = LabelEncoder()
            le.fit(df['TransactionAmt_binned'])
            self.label_encoders['TransactionAmt_binned'] = le

    def _transform_sum_features(self, df):
        if 'TransactionAmt' in df.columns and self.lower_bound is not None:
            df['log_TransactionAmt'] = np.log1p(df['TransactionAmt'])
            df['isOutlier'] = ((df['TransactionAmt'] < self.lower_bound) | (df['TransactionAmt'] > self.upper_bound)).astype(int)
            df['TransactionAmt_binned'] = pd.cut(
                df['TransactionAmt'],
                bins=[0, 100, 1000, 5000, 10000, np.inf],
                labels=['Low', 'Medium', 'High', 'Very High', 'Extremely High']
            ).astype(str).fillna('unknown')
            le = self.label_encoders.get('TransactionAmt_binned')
            if le is not None:
                df['TransactionAmt_binned'] = df['TransactionAmt_binned'].where(
                    df['TransactionAmt_binned'].isin(le.classes_), 'unknown')
                df['TransactionAmt_binned'] = le.transform(df['TransactionAmt_binned'])
        return df

    def _fit_transaction_group_features(self, df):
        self.group_stats = {}
        for col in ['card1', 'card4']:
            if col in df.columns and 'TransactionAmt' in df.columns:
                g = df.groupby(col)['TransactionAmt']
                self.group_stats[f'{col}_mean'] = g.mean()
                self.group_stats[f'{col}_std'] = g.std()

    def _transform_transaction_group_features(self, df):
        for col in ['card1', 'card4']:
            if col in df.columns and 'TransactionAmt' in df.columns:
                df[f'TransactionAmt_to_mean_{col}'] = df['TransactionAmt'] / df[col].map(self.group_stats.get(f'{col}_mean')).replace([np.inf, -np.inf], 0)
                df[f'TransactionAmt_to_std_{col}'] = df['TransactionAmt'] / df[col].map(self.group_stats.get(f'{col}_std')).replace([np.inf, -np.inf], 0)
                df[[f'TransactionAmt_to_mean_{col}', f'TransactionAmt_to_std_{col}']] = df[[f'TransactionAmt_to_mean_{col}', f'TransactionAmt_to_std_{col}']].fillna(0)
        return df

    def _fit_v_pca_features(self, df):
        self.v_cols_ = [col for col in df.columns if col.startswith('V')]
        common_cols = self.v_cols_
        if len(common_cols) > 0:
            X_v = df[common_cols].fillna(-999)
            v_scaler = StandardScaler()
            X_v_scaled = v_scaler.fit_transform(X_v)
            pca = PCA(n_components=0.90, random_state=42)
            X_v_pca = pca.fit_transform(X_v_scaled)
            self.v_pca = (pca, v_scaler)
            self.v_pca_n_components_ = X_v_pca.shape[1]

    def _transform_v_pca_features(self, df):
        if hasattr(self, "v_pca") and self.v_pca is not None and self.v_cols_:
            common_cols = [col for col in self.v_cols_ if col in df.columns]
            if len(common_cols) == 0:
                return df
            v_scaler = self.v_pca[1]
            pca = self.v_pca[0]
            X_v = df[common_cols].fillna(-999)
            X_v_scaled = v_scaler.transform(X_v)
            X_v_pca = pca.transform(X_v_scaled)
            for i in range(X_v_pca.shape[1]):
                df[f'V_PCA_{i}'] = X_v_pca[:, i]
            df = df.drop(columns=common_cols)
        return df

    def _fit_v_pca_scaler(self, df):
        if hasattr(self, 'v_pca') and self.v_pca is not None and self.v_cols_:
            common_cols = [col for col in self.v_cols_ if col in df.columns]
            if len(common_cols) == 0:
                return
            v_scaler = self.v_pca[1]
            pca = self.v_pca[0]
            X_v = df[common_cols].fillna(-999)
            X_v_scaled = v_scaler.transform(X_v)
            X_v_pca = pca.transform(X_v_scaled)
            v_pca_cols = [f'V_PCA_{i}' for i in range(X_v_pca.shape[1])]
            tmp = pd.DataFrame(X_v_pca, columns=v_pca_cols)
            self.v_pca_scaler = StandardScaler().fit(tmp)