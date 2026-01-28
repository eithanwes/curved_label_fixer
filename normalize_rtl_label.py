from qgis.core import qgsfunction
import unicodedata

@qgsfunction(args=1, group='Custom')
def normalize_rtl_label(values, feature, parent):
    """
    normalize_rtl_label(<string>) → string
    Reverses characters in each RTL part of the input string,
    reorders adjacent RTL segments to ensure logical visual order,
    and corrects bracket directions in RTL text.
    """
    val = values[0]
    if val is None:
        return None
    if not isinstance(val, str):
        raise ValueError('normalize_rtl_label: input is not a string')

    # Define punctuation mappings for RTL contexts
    rtl_punctuation_map = str.maketrans({
        '(': ')',
        ')': '(',
        '[': ']',
        ']': '[',
        '{': '}',
        '}': '{',
        '<': '>',
        '>': '<'
    })

    # Step 1: Split into directional runs
    runs = []
    current_dir = None
    current_text = ''
    for ch in val:
        bidi = unicodedata.bidirectional(ch)
        if bidi in ('R', 'AL', 'RLE', 'RLO'):
            dir_flag = 'RTL'
        elif bidi in ('L', 'LRE', 'LRO'):
            dir_flag = 'LTR'
        else:
            dir_flag = 'Neutral'

        if dir_flag != current_dir:
            if current_text:
                runs.append((current_text, current_dir))
            current_text = ch
            current_dir = dir_flag
        else:
            current_text += ch

    if current_text:
        runs.append((current_text, current_dir))

    # Step 2: Reverse text of RTL runs and adjust punctuation
    reversed_runs = []
    for text, direction in runs:
        if direction == 'RTL':
            # Reverse the text and adjust punctuation
            adjusted_text = text[::-1].translate(rtl_punctuation_map)
            reversed_runs.append((adjusted_text, direction))
        else:
            reversed_runs.append((text, direction))

    # Step 3: Detect and reverse RTL run groups (optionally with surrounding neutrals)
    final_runs = []
    temp_group = []

    def flush_group():
        if temp_group:
            # Reverse the order of RTL+neutral runs inside the group
            final_runs.extend(reversed(temp_group))
            temp_group.clear()

    for text, direction in reversed_runs:
        if direction == 'RTL' or direction == 'Neutral':
            temp_group.append((text, direction))
        else:
            flush_group()
            final_runs.append((text, direction))

    flush_group()  # In case it ended with an RTL/neutral group

    # Step 4: Rebuild final string
    final_text = ''.join(text for text, _ in final_runs)

    # Step 5: Correct bracket directions in the final string
    final_text = final_text.translate(rtl_punctuation_map)

    return final_text