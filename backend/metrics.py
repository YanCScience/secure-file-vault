import math

def calculate_entropy(data: bytes) -> float:
    """Menghitung nilai Entropi Shannon dari data (ideal untuk cipherteks mendekati 8.0)"""
    if not data:
        return 0.0
    entropy = 0.0
    for x in range(256):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy -= p_x * math.log2(p_x)
    return entropy

def calculate_avalanche_effect(data1: bytes, data2: bytes) -> float:
    """Menghitung persentase perubahan bit antara dua cipherteks (Avalanche Effect)"""
    min_len = min(len(data1), len(data2))
    differing_bits = 0
    total_bits = min_len * 8
    
    for i in range(min_len):
        xor_result = data1[i] ^ data2[i]
        differing_bits += bin(xor_result).count('1')
        
    return (differing_bits / total_bits) * 100

def calculate_byte_histogram(data: bytes) -> dict:
    """Menghitung frekuensi kemunculan byte 0-255 untuk grafik histogram."""
    histogram = [0] * 256
    for byte in data:
        histogram[byte] += 1
    return {
        "total_bytes": len(data),
        "distribution": histogram 
    }