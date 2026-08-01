# D3 Main Panel — Flow

**About:** [description](../__about/D3_MainPanel.md)

GUI file — the zone tree below is what earns this file its Algorithmic
tier: 8 tabs plus a search bar is too much to hold from prose alone.

## Zone tree

```
📁 Window_Frame (right-hand panel, root row1/col1)
  📁 Search Bar (row 0)
    🔘 Add/Remove row icons
    📝 "SEARCH BY" label
    📁 1–7 dynamic search rows (built by C3_SelectDB.SearchBar_DynamicPart)
    ☑️ per-column filter checkbuttons + FILTER buttons
    🔘 "FILTER from Pacijenti" toggle (shared with the Graph tab)
    🔘 SEARCH / SHOW ALL buttons
  📁 Notebook (row 9, 8 tabs)
    📁 Tab 0 — Pacijenti (patient list)
      ☑️ column-visibility checkbuttons (Checkbutton_Create, shared w/ Settings)
      🗄️ Treeview → MainTablePacijenti
    📁 Tab 1 — Slike (images)
      📁 left: button bar (Add/Edit/Delete/Download) + input row + Treeview → SlikeTable
      📁 right: canvas image/video viewer (Media.Slike_Viewer)
    📁 Tab 2 — Katalog (MKB-10 + staff)
      📁 left: MKB-10 Treeview → MKBTable + entry form (Katalog_Entry_Create)
      📁 right: Zaposleni Treeview → ZaposleniTable + entry form
    📁 Tab 3 — Grafikon (analytics/charts)
      📁 axis wizard: Y combobox → X1[-2/-3] → X2[-2/-3] (see C3_SelectDB flow)
      🔘 plot-type radio (bars/stacked/pie), color/values/filter checkboxes
      📊 embedded matplotlib canvas
    📁 Tab 4 — Logs (hidden by default — GodMode "Admin")
      🗄️ Treeview → LogsTable
      📁 free_query_panel (shared with Tab 5 — GodMode raw-SQL console)
      📝 Full Query / Full Error detail panels
    📁 Tab 5 — Session (hidden by default — GodMode "Admin")
      🗄️ Treeview → SessionTable
      📁 free_query_panel (shared with Tab 4)
      📝 paged PC-info report panel (SelectDB.swapping_session_data)
    📁 Tab 6 — Settings
      🎨 Theme picker (image radio buttons, per Theme_Names)
      🖼️ Title-image picker (per Title_Names)
      ☑️ default-visible-columns picker (reuses Checkbutton_Create)
      📁 System settings: Language/Font comboboxes, Meter gauges (Font Size,
         Width, Height, Title Height, Button/Thread cooldown)
      🔘 Restore Default / Save Settings
    📁 Tab 7 — About
      📝 title + description text
      📋 credits table (role → developer)
      🔗 support email (mailto:) + GitHub link
      🖼️ MUVS logo canvas
```

## Boot-order note

`initializeMP(root)` builds these 8 tabs strictly in this order (Pacijenti,
Slike, Katalog, Grafikon, Logs, Session, Settings, About) — Logs/Session
start hidden (`NoteBook.hide(4)`/`hide(5)`) and are revealed only by
`GodMode.GodMode_Password` (see
[C1 Controller](../__about/C1_Controller.md)) unlocking "Admin"/"God Mode".
