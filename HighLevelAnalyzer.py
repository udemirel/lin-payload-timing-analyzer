from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame

class Hla(HighLevelAnalyzer):
    # We removed 'µs' and labels from the formats to keep Excel rows clean
    result_types = {
        'ibs': {'format': '{{data.ms}}'},
        'ifs': {'format': '{{data.ms}}'},
        'h_break': {'format': '{{data.lbl}}'},
        'h_sync': {'format': '{{data.lbl}}'},
        'h_pid': {'format': '{{data.lbl}}'},
        'd_byte': {'format': '{{data.lbl}}'},
        'chk_sum': {'format': '{{data.lbl}}'},
        # Dynamic summary types
        'DATA_LEN_1B': {'format': '{{data.lbl}}'},
        'DATA_LEN_2B': {'format': '{{data.lbl}}'},
        'DATA_LEN_3B': {'format': '{{data.lbl}}'},
        'DATA_LEN_4B': {'format': '{{data.lbl}}'},
        'DATA_LEN_5B': {'format': '{{data.lbl}}'},
        'DATA_LEN_6B': {'format': '{{data.lbl}}'},
        'DATA_LEN_7B': {'format': '{{data.lbl}}'},
        'DATA_LEN_8B': {'format': '{{data.lbl}}'}
    }

    def __init__(self):
        self.last_end = None
        self.d_idx = 0
        self.p_start = None
        self.p_end = None
        self.expecting_ifs = False

    def decode(self, frame: AnalyzerFrame):
        res = [] 
        
        # --- 1. GAP CALCULATION (Pure Numbers in Microseconds) ---
        if self.last_end is not None:
            try:
                # Value in microseconds
                gap_us = float(frame.start_time - self.last_end) * 1000000
                us_num_str = f"{gap_us:.1f}" # Pure number string
                
                t = 'ifs' if self.expecting_ifs else 'ibs'
                self.expecting_ifs = False 
                
                if gap_us >= 0:
                    # We store the pure number in the 'ms' field for the table
                    res.append(AnalyzerFrame(t, self.last_end, frame.start_time, {'ms': us_num_str}))
            except:
                pass

        # --- 2. FIELD PROCESSING ---
        is_data = frame.type == 'data'
        is_checksum = frame.type in ['checksum', 'data_or_checksum', 'checksum_error']
        
        lbl = str(frame.type).upper()
        val_for_table = "" 
        current_type = 'lin_data'

        if frame.type == 'header_break':
            self.d_idx = 0
            self.p_start = None
            self.p_end = None
            lbl = "BRK"
            current_type = 'h_break'
        elif frame.type == 'header_sync':
            lbl = "SYN"
            current_type = 'h_sync'
        elif frame.type == 'header_pid':
            raw_id = frame.data.get('identifier') or frame.data.get('pid') or \
                     frame.data.get('protected_id') or frame.data.get('data')
            lbl = f"ID:0x{int(raw_id):02X}" if raw_id is not None else "ID:??"
            current_type = 'h_pid'
            
        elif is_data:
            self.d_idx += 1
            if self.d_idx == 1: self.p_start = frame.start_time
            self.p_end = frame.end_time 
            
            val = frame.data.get('data', 0)
            lbl = "0" if val == 0 else ("1" if val == 1 else f"0x{val:02X}")
            current_type = 'd_byte'
        
        elif is_checksum:
            raw_chk = frame.data.get('checksum') or frame.data.get('data') or 0
            chk_hex = f"0x{int(raw_chk):02X}" if isinstance(raw_chk, (int, float)) else "CHK"
            self.expecting_ifs = True 
            
            if self.p_start and self.p_end:
                payload_us = float(self.p_end - self.p_start) * 1000000
                val_for_table = f"{payload_us:.1f}"
                # Label still shows unit for waveform readability, but 'data' column is pure
                lbl = f"{chk_hex} ({self.d_idx}B, {val_for_table}us)"
                current_type = f'DATA_LEN_{self.d_idx}B'

        # Append the frame with pure numeric values for columns
        res.append(AnalyzerFrame(current_type, frame.start_time, frame.end_time, {
            'lbl': lbl,          # Waveform label
            'data': val_for_table, # Pure number for Excel Data column
            'ms': val_for_table if is_checksum else "" # Fills ms column for summary rows
        }))

        self.last_end = frame.end_time
        return res