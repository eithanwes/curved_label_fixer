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

    # Arabic letter forms: [isolated, final, initial, medial]
    # Only including most common letters for brevity
    arabic_forms = {
        '\u0627': ['\uFE8D', '\uFE8E', '\uFE8D', '\uFE8E'],  # Alef
        '\u0628': ['\uFE8F', '\uFE90', '\uFE91', '\uFE92'],  # Beh
        '\u062A': ['\uFE95', '\uFE96', '\uFE97', '\uFE98'],  # Teh
        '\u062B': ['\uFE99', '\uFE9A', '\uFE9B', '\uFE9C'],  # Theh
        '\u062C': ['\uFE9D', '\uFE9E', '\uFE9F', '\uFEA0'],  # Jeem
        '\u062D': ['\uFEA1', '\uFEA2', '\uFEA3', '\uFEA4'],  # Hah
        '\u062E': ['\uFEA5', '\uFEA6', '\uFEA7', '\uFEA8'],  # Khah
        '\u062F': ['\uFEA9', '\uFEAA', '\uFEA9', '\uFEAA'],  # Dal
        '\u0630': ['\uFEAB', '\uFEAC', '\uFEAB', '\uFEAC'],  # Thal
        '\u0631': ['\uFEAD', '\uFEAE', '\uFEAD', '\uFEAE'],  # Reh
        '\u0632': ['\uFEAF', '\uFEB0', '\uFEAF', '\uFEB0'],  # Zain
        '\u0633': ['\uFEB1', '\uFEB2', '\uFEB3', '\uFEB4'],  # Seen
        '\u0634': ['\uFEB5', '\uFEB6', '\uFEB7', '\uFEB8'],  # Sheen
        '\u0635': ['\uFEB9', '\uFEBA', '\uFEBB', '\uFEBC'],  # Sad
        '\u0636': ['\uFEBD', '\uFEBE', '\uFEBF', '\uFEC0'],  # Dad
        '\u0637': ['\uFEC1', '\uFEC2', '\uFEC3', '\uFEC4'],  # Tah
        '\u0638': ['\uFEC5', '\uFEC6', '\uFEC7', '\uFEC8'],  # Zah
        '\u0639': ['\uFEC9', '\uFECA', '\uFECB', '\uFECC'],  # Ain
        '\u063A': ['\uFECD', '\uFECE', '\uFECF', '\uFED0'],  # Ghain
        '\u0641': ['\uFED1', '\uFED2', '\uFED3', '\uFED4'],  # Feh
        '\u0642': ['\uFED5', '\uFED6', '\uFED7', '\uFED8'],  # Qaf
        '\u0643': ['\uFED9', '\uFEDA', '\uFEDB', '\uFEDC'],  # Kaf
        '\u0644': ['\uFEDD', '\uFEDE', '\uFEDF', '\uFEE0'],  # Lam
        '\u0645': ['\uFEE1', '\uFEE2', '\uFEE3', '\uFEE4'],  # Meem
        '\u0646': ['\uFEE5', '\uFEE6', '\uFEE7', '\uFEE8'],  # Noon
        '\u0647': ['\uFEE9', '\uFEEA', '\uFEEB', '\uFEEC'],  # Heh
        '\u0648': ['\uFEED', '\uFEEE', '\uFEED', '\uFEEE'],  # Waw
        '\u064A': ['\uFEF1', '\uFEF2', '\uFEF3', '\uFEF4'],  # Yeh
        '\u0629': ['\uFE93', '\uFE94', '\uFE93', '\uFE94'],  # Teh Marbuta
    }
    
    # Non-connecting letters (only have isolated and final forms)
    non_connecting = {'\u0627', '\u062F', '\u0630', '\u0631', '\u0632', '\u0648'}
    
    def reshape_arabic(text):
        """Convert Arabic text to presentation forms based on position"""
        result = []
        chars = list(text)
        
        for i, ch in enumerate(chars):
            if ch not in arabic_forms:
                # Not a shapeable Arabic letter, keep as-is
                result.append(ch)
                continue
            
            # Determine position: 0=isolated, 1=final, 2=initial, 3=medial
            prev_connects = i > 0 and chars[i-1] in arabic_forms and chars[i-1] not in non_connecting
            next_connects = i < len(chars) - 1 and chars[i+1] in arabic_forms
            
            if prev_connects and next_connects:
                form_idx = 3  # medial
            elif prev_connects:
                form_idx = 1  # final
            elif next_connects and ch not in non_connecting:
                form_idx = 2  # initial
            else:
                form_idx = 0  # isolated
            
            result.append(arabic_forms[ch][form_idx])
        
        return ''.join(result)

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
            # Check if text contains Arabic characters
            has_arabic = any('\u0600' <= ch <= '\u06FF' or '\u0750' <= ch <= '\u077F' 
                            or '\u08A0' <= ch <= '\u08FF' for ch in text)
            
            if has_arabic:
                # For Arabic: reshape to presentation forms, then reverse
                reshaped = reshape_arabic(text)
                adjusted_text = reshaped[::-1].translate(rtl_punctuation_map)
            else:
                # For Hebrew and other RTL: reverse character order
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