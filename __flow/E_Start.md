# E Start — Flow

**About:** [description](../__about/E_Start.md)

## Algorithm — application boot sequence

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["__main__: freeze_support(),<br/>record 'Loading Modules' timing"] --> B["start()"]
    B --> C["build tb.Window, withdraw it<br/>(hidden until fully built)"]
    C --> D["apply THEME, read every<br/>Colors.label_iter() entry<br/>into ThemeColors"]
    D --> E["configure global styles:<br/>Notebook.Tab, Treeview,<br/>Treeview.Heading, default fonts"]
    E --> F["Classes_Decorating([14 classes]):<br/>for every method of every class,<br/>wrap with method_efficency + error_catcher"]
    F --> G["GUI.initialize(root)<br/>— see D4 Window flow"]
    G --> H{frozen build?}
    H -->|yes| I["pyi_splash.close()"]
    H -->|no| J["skip"]
    I --> K["root.mainloop()"]
    J --> K
```

Pseudocode:

    ON __main__:
        multiprocessing.freeze_support()
        UserSession['GUI']['Loading Modules'] = elapsed time since TIME_START
        start()

    FUNCTION start():
        root = build tb.Window (hidden)
        style = apply THEME
        FOR each theme color label: ThemeColors[label] = style.colors.get(label)
        configure Notebook / Treeview / font styles globally

        FUNCTION Classes_Decorating(class_list):
            FOR each CLASS in class_list:
                FOR each method defined on CLASS:
                    replace it with method_efficency()(error_catcher()(method))

        Classes_Decorating([GoogleDrive, Database, Media, Graph, AI,
                             Controller, GodMode, ManageDB, SelectDB,
                             TopPanel, FormPanel, MainPanel, GUI])

        GUI.initialize(root)          # builds and shows the whole UI
        IF running as a frozen EXE: close the PyInstaller splash screen
        root.mainloop()

`Classes_Decorating` is the single mechanism that gives every method of
these 14 classes both perf telemetry (`method_efficency`) and audit-logged
error visibility (`error_catcher`) — see
[A2 Decorators](../__about/A2_Decorators.md). Any class NOT in this list
(e.g. `Loading_Splash`) gets neither, automatically.
