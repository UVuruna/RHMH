# dialogs — Flow

**About:** [description](../__about/dialogs.md)

## Algorithm 1 — `Dialog` template-method lifecycle

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["Messagebox.xxx() or Querybox.xxx()<br/>constructs a Dialog subclass"] --> B["show(position)"]
    B --> C["build(): construct the Toplevel,<br/>bind Escape → destroy"]
    C --> D["create_body(master)<br/>— subclass-specific content"]
    D --> E["create_buttonbox(master)<br/>— subclass-specific buttons"]
    E --> F["_locate(): position relative<br/>to the parent window"]
    F --> G["grab_set() — modal"]
    G --> H["wait_window() — blocks the<br/>caller until closed"]
    H --> I["user clicks a button →<br/>on_button_press() / on_submit()"]
    I --> J["record self._result,<br/>destroy the window"]
    J --> K["wait_window() returns,<br/>caller reads .result"]
```

Pseudocode:

    ON Messagebox.show_xxx() / Querybox.get_xxx():
        dialog = MessageDialog(...) or QueryDialog(...)
        dialog.show(position)

    METHOD Dialog.show(position):
        build()                      # constructs Toplevel, binds Escape
        create_body(master)          # subclass fills in its content
        create_buttonbox(master)     # subclass fills in its buttons
        _locate(position)            # position relative to parent
        grab_set()                   # make modal
        wait_window()                # BLOCKS here until destroyed

    ON a button pressed (MessageDialog) / Submit pressed (QueryDialog):
        IF QueryDialog: validate() the entry value first; on failure, show
           an error Messagebox and do NOT close
        result = the chosen value / button label
        destroy the window            # wait_window() in show() now returns

    CALLER (after show() returns): read dialog.result

## Algorithm 2 — `DatePickerDialog` calendar navigation

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["DatePickerDialog(startdate)"] --> B["_draw_titlebar():<br/>month/year label + chevrons"]
    B --> C["_draw_calendar():<br/>Radiobutton grid for the<br/>current month's days"]
    C --> D{user action}
    D -->|click a day| E["_on_date_selected():<br/>store the date, close"]
    D -->|click ◀/▶ chevron| F["on_prev_month / on_next_month"]
    D -->|right-click title| G["on_prev_year / on_next_year"]
    D -->|click title text| H["on_reset_date:<br/>jump back to startdate's month"]
    F --> I["_selection_callback wrapper:<br/>redraw the grid for the<br/>new month"]
    G --> I
    H --> I
    I --> C
    E --> J["result available to<br/>Querybox.get_date() caller"]
```

Pseudocode:

    ON DatePickerDialog(startdate):
        build own Toplevel (does NOT reuse the Dialog base class)
        draw titlebar (month/year, prev/next chevrons)
        draw the current month's day grid as Radiobuttons
        grab_set(); wait_window()

    DECORATOR _selection_callback(nav_function):
        # wraps every prev/next/reset handler
        RUN nav_function()            # changes the displayed month/year
        redraw the day grid for the new month

    ON a day Radiobutton clicked:
        store the clicked date as the result
        destroy the window            # wait_window() returns

`FontDialog` follows the same `Dialog`-subclass template as
`MessageDialog`/`QueryDialog` (Algorithm 1) with a 4-panel body (family
list, size list, weight/slant/effects, live preview) — no separate diagram
needed; see [about](../__about/dialogs.md) for its method list.
