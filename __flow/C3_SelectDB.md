# C3 Select DB — Flow

**About:** [description](../__about/C3_SelectDB.md)

This file is 1,257 lines covering ~12 distinct features (full breakdown in
the about doc's responsibility table). The two pieces below are the ones a
diagram genuinely explains better than the code: the Graph-tab wizard
(`graph_choice_analyze`) and the search-bar's per-column-type widget
morphing (`search_options`). Everything else in the file is Standard-grade
CRUD/display glue, documented in prose in the about doc.

## Algorithm 1 — `graph_choice_analyze` (Graph-tab cascading wizard)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    Y["Y combobox chosen<br/>(Graph.Y_options)"] --> X1["X1 combobox enabled"]
    X1 --> X1CHOICE{X1 needs a<br/>sub-dimension?<br/>e.g. MKB / staff}
    X1CHOICE -->|yes| X12["X1-2 combobox activates<br/>(graph_activate_afterchoice)"]
    X1CHOICE -->|no| X2GATE
    X12 --> X13{needs a third level?}
    X13 -->|yes| X13B["X1-3 combobox activates"]
    X13 -->|no| X2GATE
    X13B --> X2GATE["X2 combobox enabled<br/>(second grouping dimension,<br/>optional — graph_activating_X2)"]
    X2GATE --> X2CHOICE{X2 chosen and<br/>needs sub-dimensions?}
    X2CHOICE -->|yes| X22["X2-2 / X2-3 comboboxes<br/>activate, same pattern as X1"]
    X2CHOICE -->|no| PLOT
    X22 --> PLOT["plot-type Radiobuttons show<br/>(bars / stacked / pie)"]
    PLOT --> READY["Show_Graph / Configure_Graph<br/>enabled"]
    X1 -. change X1 .-> RESET["graph_remove_afterchoice:<br/>clear every downstream combobox<br/>(X1-2, X1-3, X2, X2-2, X2-3, plot type)"]
    RESET --> X1CHOICE
```

Pseudocode:

    ON Y changed:
        enable X1 combobox with options relevant to the chosen Y

    ON X1 changed:
        graph_remove_afterchoice()   # clear every downstream combobox first
        IF X1's type needs a sub-dimension (e.g. "MKB category" needs which category):
            activate X1-2 (and, if that also branches, X1-3)
        enable X2 (the optional second grouping axis), same cascade rules

    ON X2 changed:  # same cascade as X1, one level deeper
        graph_remove_afterchoice() for X2's downstream only
        IF X2's type needs a sub-dimension:
            activate X2-2 (and X2-3)

    WHEN the full Y/X1[.../X2...] chain is resolved:
        show the plot-type Radiobuttons (bars / stacked bar / pie)
        enable "Show Graph" / "Configure Graph"

The fixed axis-name sequence driving this cascade is
`['Y','X1-1','X1-2','X1-3','X2-1','X2-2','X2-3']` — index-based list
slicing against this sequence is how `graph_choice_analyze` knows which
comboboxes are "downstream" of a given change.

## Algorithm 2 — `search_options` (search-bar column-type widget morphing)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["user picks a column in a<br/>search-bar row's Combobox"] --> B{column type?}
    B -->|date column<br/>e.g. Datum Prijema, ID Time| C["value widget → DateEntry<br/>(2× for BETWEEN)"]
    B -->|numeric column<br/>e.g. Godište, Veličina, Session| D["value widget → Entry<br/>(2× for BETWEEN)"]
    B -->|categorical column<br/>e.g. Pol, Format, Opis, Email| E["value widget → Combobox<br/>(dropdown of known values)"]
    B -->|anything else| F["value widget → plain Entry"]
    C --> G["comparator sign set:<br/>EQUAL / LIKE / NOT LIKE / BETWEEN"]
    D --> G
    E --> G
    F --> G
    G --> H["search_options_swap:<br/>click the sign icon to rotate<br/>through the allowed signs"]
```

Pseudocode:

    ON column selected in a search-bar row:
        IF column IN date-type list: build a DateEntry (or 2, for BETWEEN)
        ELIF column IN numeric-type list: build an Entry (or 2, for BETWEEN)
        ELIF column IN categorical list: build a Combobox of known values
        ELSE: build a plain Entry
        set the row's allowed comparator signs for this column's type

    ON comparator sign icon clicked:
        rotate to the next sign in the allowed set (search_options_swap)
