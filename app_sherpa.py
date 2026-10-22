import os
import sys
import sherpa_onnx
import sounddevice as sd

from buh import count_fillers
from score import evaluate_speech

model_dir = "sherpa-model"

if not os.path.exists(model_dir):
    print("දෝෂයකි: 'sherpa-model' folder එක හමු නොවීය. Folder එකේ නම පරීක්ෂා කරන්න.")
    sys.exit(1)

# Sherpa-ONNX Recognizer සකස් කිරීම
recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
    tokens=os.path.join(model_dir, "tokens.txt"),
    encoder=os.path.join(model_dir, "encoder-epoch-99-avg-1.int8.onnx"),
    decoder=os.path.join(model_dir, "decoder-epoch-99-avg-1.onnx"),
    joiner=os.path.join(model_dir, "joiner-epoch-99-avg-1.int8.onnx"),
    num_threads=2,
    sample_rate=16000,
    feature_dim=80,
    decoding_method="greedy_search",
)

stream = recognizer.create_stream()
sample_rate = 16000

full_transcript = []
last_text = ""

print("\n=== කතා කරන්න පටන් ගන්න (නතර කිරීමට එක් වරක් Ctrl+C ඔබන්න) ===")

def audio_callback(indata, frames, time_info, status):
    samples = indata[:, 0]
    stream.accept_waveform(sample_rate, samples)

try:
    with sd.InputStream(channels=1, dtype="float32", samplerate=sample_rate, callback=audio_callback):
        while True:
            while recognizer.is_ready(stream):
                recognizer.decode_stream(stream)
            
            text = recognizer.get_result(stream).strip()
            if text and text != last_text:
                print(f"හඳුනාගත් කොටස: {text}")
                last_text = text
            sd.sleep(50)

except KeyboardInterrupt:
    print("\n\nශ්‍රවණය කිරීම නතර කරන ලදී...")

# අවසාන පෙළ ලබා ගැනීම
final_text = recognizer.get_result(stream).strip()
if final_text:
    full_transcript.append(final_text)

complete_text = " ".join(full_transcript).strip()

print("\n" + "=" * 50)
print(f"සම්පූර්ණ පෙළ (Transcript): '{complete_text}'")
print("=" * 50)

if not complete_text:
    print("අවවාදයයි: කිසිදු වචනයක් හඳුනා ගැනීමට නොහැකි විය.")
else:
    print("\nGrammar සහ Fillers පරීක්ෂා කරමින් පවතී...")
    try:
        fillers = count_fillers(complete_text)
        analysis = evaluate_speech(complete_text, fillers)

        print("\n" + "#" * 50)
        print("--- අවසන් වාර්තාව ---")
        print(f"අවසන් ලකුණු මට්ටම  : {analysis['score']} / 10")
        print(f"Grammar වැරදි ගණන  : {analysis['total_grammar_errors']}")
        print(f"Fillers / Hesitations : {analysis['filler_count']} (අඩු කළ ලකුණු: -{analysis['filler_deduction']})")
        print("#" * 50)

        for category, errors in analysis["details"].items():
            if errors:
                print(f"\n[{category}] ({len(errors)} ක් හමුවිය):")
                for err in errors:
                    print(f" • {err['message']} (Context: '{err['context']}')")
        print("=" * 50)
    except Exception as e:
        print(f"\nEvaluation එකේදී දෝෂයක් මතු විය: {e}")
