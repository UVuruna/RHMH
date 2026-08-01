# B4 Graph — Flow

**About:** [description](../__about/B4_Graph.md)

## Algorithm — `Graph_makeQuery` / `get_Xgroups`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["Graph_makeQuery(Y, X1, X2, Filter)"] --> B["resolve Y → (SQL expr or 1, date column)<br/>via Y_options"]
    B --> C["get_Xgroups(X1, datewhere)"]
    C --> D{X1 type?}
    D -->|MKB category/code| E["build CASE per MKB group,<br/>LEFT JOIN mkb10/kategorija"]
    D -->|staff / role| F["build CASE per staff group,<br/>LEFT JOIN zaposleni/funkcija"]
    D -->|age| G["Graph_StarostGroups(jump):<br/>fixed-step BETWEEN brackets 0..80 + 80+"]
    D -->|Trauma / Pol binary| H["X_options[X1] explicit<br/>[labels, condition] pair"]
    D -->|generic date bucket| I["strftime(datetype, datewhere)<br/>grouping"]
    E --> J{X2 given?}
    F --> J
    G --> J
    H --> J
    I --> J
    J -->|yes| K["repeat get_Xgroups for X2,<br/>compose a 2D CASE/SUM matrix"]
    J -->|no| L["single-dimension aggregate query"]
    K --> M{Filter given?}
    L --> M
    M -->|yes| N["AND id_pacijent IN Filter"]
    M -->|no| O["no extra WHERE"]
    N --> P["assemble final SELECT ... GROUP BY"]
    O --> P
```

Pseudocode:

    FUNCTION Graph_makeQuery(Y, X1, X2, Filter):
        y_expr, date_col = Y_options[Y]

        FUNCTION get_Xgroups(X, datewhere):
            IF X is an MKB category or an individual MKB code:
                RETURN (CASE-per-MKB-group conditions, extra WHERE, "mkb10/kategorija")
            IF X is a staff member or a staff role:
                RETURN (CASE-per-staff conditions, extra WHERE, "zaposleni/funkcija")
            IF X == "Starost" (age):
                RETURN (Graph_StarostGroups(jump), None, None)
            IF X IN X_options AND X_options[X] is a [labels, condition] pair:
                RETURN (that pair, None, None)
            ELSE:  # generic date dimension (Year/Month/Weekday/Day)
                RETURN (strftime(DateTypes[X], datewhere) buckets, None, None)

        x1_groups, extra_where_1, join_1 = get_Xgroups(X1, date_col)
        IF X2: x1_groups, extra_where_2, join_2 = get_Xgroups(X2, date_col)  # 2D matrix

        query = SELECT (CASE-conditioned SUM/AVG of y_expr per group) ...
                FROM pacijent
                + conditional JOINs (join_1, join_2)
                + WHERE (extra_where_1 AND extra_where_2 AND id_pacijent IN Filter, if any)
        RETURN query

This is the **third** occurrence of the `dijagnoza/mkb10/kategorija` and
`operacija/funkcija/zaposleni` LEFT JOIN pattern in the codebase — the same
shape appears (twice) in [B2 SQLite](../__about/B2_SQLite.md)'s
`execute_join_select`/`get_patient_data`. A future rework should centralize
this JOIN template once.
