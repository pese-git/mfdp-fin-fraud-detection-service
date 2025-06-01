
import pandas as pd

import numpy as np
import torch
from torch_geometric.data import Data




def to_graph_data(
    df: pd.DataFrame,
    edge_keys=['card1'],
    target_col='isFraud',
    ignore_cols=None,
    num_cols=None,        # список float признаков
    cat_cols=None,        # список категориальных признаков (label-encoded!)
    edge_features_fn=None # функция, если нужны edge_attr
):
    if ignore_cols is None:
        ignore_cols = [target_col]
    if num_cols is None or cat_cols is None:
        num_cols = df.select_dtypes(include=['float', 'float32', 'float64']).columns.tolist()
        cat_cols = df.select_dtypes(include=['int', 'int32', 'int64']).columns.tolist()
        num_cols = [c for c in num_cols if c not in ignore_cols]
        cat_cols = [c for c in cat_cols if c not in ignore_cols]

    # Тензоры признаков
    x_num = torch.tensor(df[num_cols].values, dtype=torch.float32) if num_cols else None
    x_cat = torch.tensor(df[cat_cols].values, dtype=torch.long) if cat_cols else None
    y = torch.tensor(df[target_col].values, dtype=torch.float32) if target_col in df.columns else None

    #print("cat_features:", cat_cols)
    #print("df[cat_features].columns:", df[cat_cols].columns.tolist())
    #print("df[cat_features].shape:", df[cat_cols].shape)

    # Рёбра и признаки ребер (если понадобится)
    edges_src, edges_dst, edge_attrs = [], [], []
    for edge_key in edge_keys:
        groups = df.groupby(edge_key).indices
        for indxs in groups.values():
            indxs = np.asarray(list(indxs))
            if len(indxs) > 1:
                src, dst = np.meshgrid(indxs, indxs)
                mask = src != dst
                src, dst = src[mask], dst[mask]
                edges_src.append(src)
                edges_dst.append(dst)
                # Если есть функция для edge_attr — например разности каких-нибудь признаков:
                if edge_features_fn is not None:
                    edge_feat = edge_features_fn(df.iloc[src], df.iloc[dst]) # shape: [num_edges, n_edge_feats]
                    edge_attrs.append(edge_feat)
    if len(edges_src) > 0:
        edges_src = np.concatenate(edges_src)
        edges_dst = np.concatenate(edges_dst)
        edge_index = torch.tensor(np.stack([edges_src, edges_dst]), dtype=torch.long)
        if len(edge_attrs) > 0:
            edge_attr = np.concatenate(edge_attrs, axis=0)
            edge_attr = torch.tensor(edge_attr, dtype=torch.float32)
        else:
            edge_attr = None
    else:
        edge_index = torch.zeros((2, 0), dtype=torch.long)
        edge_attr = None


    if x_num is not None and x_cat is not None:
        x = torch.cat([x_num, x_cat.float()], dim=1)
    elif x_num is not None:
        x = x_num
    elif x_cat is not None:
        x = x_cat.float()
    else:
        x = None

    return Data(
        x=x,
        x_num=x_num, 
        x_cat=x_cat, 
        edge_index=edge_index, 
        edge_attr=edge_attr, # (None если нет)
        y=y
    )
