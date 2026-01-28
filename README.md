# Curved RTL Label Fixer Plugin for QGIS

This QGIS plugin fixes the rendering of right-to-left (RTL) labels on curved lines, ensuring proper display of languages such as Arabic and Hebrew.
After installing the plugin, a `normalize_rtl_label` function is added to the "Custom" expression functions, which can be used to correct RTL text rendering issues.

A button is added to the plugins toolbar that executes the label fixing process on all applicable layers (all vector and vector tile layers with "Curved" placement mode) in the current QGIS project.