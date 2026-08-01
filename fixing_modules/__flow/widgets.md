# widgets — Flow

**About:** [description](../__about/widgets.md)

## Algorithm — `Meter`'s draw pipeline (the file's most complex logic)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["Meter.__init__(amountmin, amounttotal,<br/>amountused, arcrange, arcoffset, ...)"] --> B["_set_arc_offset_range():<br/>compute start/end degrees<br/>(full circle 360° or semi 270°)"]
    B --> C["_draw_base_image():<br/>draw the static high-res<br/>trough/background arc at 3× scale"]
    C --> D["_meter_value():<br/>map amountused ∈ [amountmin, amounttotal]<br/>to a degree position<br/># dodato: clamps against amountmin,<br/>not always 0"]
    D --> E{indicator style?}
    E -->|solid| F["_draw_solid_meter():<br/>draw one continuous arc band<br/>from start to the value degree"]
    E -->|striped| G["_draw_striped_meter():<br/>draw discrete wedges up to<br/>the value degree"]
    F --> H["composite onto a copy of<br/>the base trough image"]
    G --> H
    H --> I["downscale 3×→1× with<br/>Image.BICUBIC for anti-aliasing"]
    I --> J["update the indicator<br/>Label's PhotoImage"]
    J --> K{interactive?}
    K -->|yes| L["_on_dial_interact(event):<br/>cursor angle → clamped, stepped value<br/># dodato: clamps to amountmin/amounttotal"]
    L --> D
    K -->|no| M["static — updates only via<br/>configure(amountused=...)"]
```

Pseudocode:

    ON Meter created (or amountused/amounttotal/amountmin changed):
        compute arc start/end degrees from arcrange/arcoffset/meter type
        draw the static trough/background arc once, at 3× supersampling

        FUNCTION _meter_value():
            # dodato: the local patch — upstream always assumed min=0
            fraction = (amountused - amountmin) / (amounttotal - amountmin)
            RETURN start_degree + fraction * arc_span_degrees

        value_degree = _meter_value()
        IF style == "solid":
            draw one continuous colored arc from start_degree to value_degree
        ELSE:  # striped
            draw discrete wedges up to value_degree

        composite the colored arc onto a copy of the base trough image
        downscale 3× → 1× (BICUBIC) for a smooth edge
        update the indicator Label's image

    ON mouse drag (if interactive=True):
        angle = angle of the cursor relative to the meter's center
        raw_value = map angle back to an amount, using the same
                    amountmin/amounttotal range as _meter_value()
        # dodato: clamp raw_value into [amountmin, amounttotal]
        IF raw_value <= amountmin: amountused = amountmin
        ELIF raw_value >= amounttotal: amountused = amounttotal
        ELSE: amountused = raw_value
        redraw (loop back to the top)

`DateEntry` and `Floodgauge` are comparatively simple keyword-wiring widgets
— no diagram needed for them; see [about](../__about/widgets.md) for their
method lists.
