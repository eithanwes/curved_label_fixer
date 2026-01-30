# Curved RTL Label Fixer Plugin for QGIS

This QGIS plugin fixes the rendering of right-to-left (RTL) labels on curved lines, ensuring proper display of languages such as Arabic and Hebrew.
After installing the plugin, a `normalize_rtl_label` function is added to the "Custom" expression functions, which can be used to correct RTL text rendering issues.

A button is added to the **labeling** (so you need to have the labeling toolbar visible) toolbar that executes the label fixing process on all applicable layers (all vector and vector tile layers with "Curved" placement mode) in the current QGIS project.

In strings with both LTR and RTL characters, the function attempts to preserve the correct order of LTR substrings while reversing the RTL characters.


## Known Issues

- Kurdish (Sorani) text may not render correctly due to the absence of proper Unicode bidirectional control characters in the current implementation. (Pull requests to address this issue are welcome!)
- The plugin may not handle complex mixed-direction text perfectly in all scenarios. Further improvements may be needed for specific use cases.

## Any help is welcome!

If you would like to contribute to the development of this plugin, please feel free to fork the repository and submit pull requests. Your contributions are highly appreciated!

## Installation

You can install the Curved RTL Label Fixer Plugin directly from the QGIS Plugin Manager or by downloading the latest release from the [GitHub repository](https://github.com/bogind/curved_label_fixer/releases) and installing it as a ZIP file.