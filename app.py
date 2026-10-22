import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer

from buh import count_fillers
from score import evaluate_speech

model_path = "model"
if not os.path.exists(model_path):
    print("Vosk model එක හමු නොවීය. 'model' folder එක පරීක්ෂා කරන්න.")
    exit(1)

print("Vosk Model එක load වෙමින් පවතී...")
model = Model(model_path)
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

print("\n=== කතා කරන්න පටන් ගන්න (නතර කිරීමට එක් වරක් පමණක් Ctrl+C ඔබන්න) ===")

full_transcript = []

try:
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text_part = res.get("text", "").strip()
            if text_part:
                print(f"හඳුනාගත් කොටස: {text_part}")
                full_transcript.append(text_part)

except KeyboardInterrupt:
    print("\n\nකතා කිරීම නතර කරන ලදී. ශ්‍රව්‍ය ධාරාව වසා දමයි...")

# Audio stream එක වසා දැමීම
final_res = json.loads(rec.FinalResult())
final_text = final_res.get("text", "").strip()
if final_text:
    full_transcript.append(final_text)

stream.stop_stream()
stream.close()
p.terminate()

# පෙළ එකතු කිරීම
complete_text = " ".join(full_transcript).strip()

print("\n" + "=" * 50)
print(f"සම්පූර්ණ පෙළ (Transcript): '{complete_text}'")
print("=" * 50)

if not complete_text:
    print("අවවාදයයි: කිසිදු වචනයක් හඳුනා ගැනීමට නොහැකි විය. කරුණාකර මයික්‍රෆෝනය පරීක්ෂා කරන්න.")
else:
    print("\nGrammar සහ Hesitations පරීක්ෂා කරමින් පවතී (මඳ වේලාවක් රැඳෙන්න)...")
    try:
        fillers = count_fillers(complete_text)
        analysis = evaluate_speech(complete_text, fillers)

        print("\n" + "#" * 50)
        print("--- අවසන් වාර්තාව ---")
        print(f"අවසන් ලකුණු මට්ටම     : {analysis['score']} / 10")
        print(f"Grammar වැරදි ගණන     : {analysis['total_grammar_errors']}")
        print(f"Fillers (ඇදෙන වචන)    : {analysis['filler_count']} (අඩු කළ ලකුණු: -{analysis['filler_deduction']})")
        print("#" * 50)

        for category, errors in analysis["details"].items():
            if errors:
                print(f"\n[{category}] ({len(errors)} ක් හමුවිය):")
                for err in errors:
                    print(f" • {err['message']} (Context: '{err['context']}')")
        print("=" * 50)
    except Exception as e:
        print(f"\nEvaluation එකේදී දෝෂයක් මතු විය: {e}")