import speech_recognition as sr
from textblob import TextBlob

from pydub import AudioSegment
from pydub.utils import which


# 🔥 auto-detect ffmpeg
AudioSegment.converter = which("ffmpeg")


# 🎤 SPEECH TO TEXT
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()

    # 🔥 convert ANY format to proper PCM WAV
    if not audio_path.endswith(".wav"):
        try:
            sound = AudioSegment.from_file(audio_path)
            new_path = audio_path.rsplit(".", 1)[0] + ".wav"

            # ✅ FIX: proper wav format
            sound.export(new_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])

            audio_path = new_path

        except Exception as e:
            print("Conversion Error:", e)
            return ""

    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
    except Exception as e:
        print("Audio Read Error:", e)
        return ""

    try:
        return recognizer.recognize_google(audio)
    except:
        return ""

def analyze_text(text, question=None):
    words = text.lower().split()
    total_words = len(words)

    filler_words = ["um", "uh", "like", "you know", "basically"]
    filler_count = sum(text.lower().count(f) for f in filler_words)

    wpm = total_words

    polarity = TextBlob(text).sentiment.polarity
    sentiment = "Positive 😊" if polarity > 0 else "Negative 😟" if polarity < 0 else "Neutral 😐"

    relevance = 0

    q_words = []

    if question:
     q_words = extract_keywords(question)

    matches = 0
    for word in q_words:
      if word in text.lower():
        matches += 1

if len(q_words) > 0:
    relevance = int((matches / len(q_words)) * 100)

    confidence = max(100 - (filler_count * 10), 0)
    clarity = 100 if 100 <= wpm <= 160 else 70
    final_score = int((confidence + clarity + relevance) / 3)

    if final_score >= 80:
        level = "Excellent ⭐"
    elif final_score >= 60:
        level = "Good 👍"
    else:
        level = "Needs Improvement ⚠"

    feedback = []

    if relevance < 50:
        feedback.append("Your answer missed key concepts required for this question.")

    if filler_count > 3:
        feedback.append("Frequent filler words reduce confidence.")

    if wpm < 100:
        feedback.append("Your speaking pace is slow.")
    elif wpm > 170:
        feedback.append("You are speaking too fast.")

    if polarity < 0:
        feedback.append("Try to sound more confident.")

    if not feedback:
        feedback.append("Great answer! Well structured and confident.")

    return {
        "total_words": total_words,
        "filler_count": filler_count,
        "wpm": int(wpm),
        "sentiment": sentiment,
        "relevance": relevance,
        "confidence": confidence,
        "clarity": clarity,
        "final_score": final_score,
        "level": level,
        "feedback": feedback
    }