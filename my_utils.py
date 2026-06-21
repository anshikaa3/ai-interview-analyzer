import speech_recognition as sr
from textblob import TextBlob
from pydub import AudioSegment
from pydub.utils import which
import re

# Auto detect ffmpeg
AudioSegment.converter = which("ffmpeg")


# -----------------------------
# Extract Keywords
# -----------------------------
def extract_keywords(text):
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    stop_words = {
        "the", "is", "are", "a", "an", "to", "of", "for",
        "and", "or", "in", "on", "with", "at", "by",
        "from", "this", "that", "it", "be", "as",
        "was", "were", "will", "would", "can", "could",
        "should", "have", "has", "had", "i", "you",
        "he", "she", "they", "we", "my", "your"
    }

    return [word for word in words if word not in stop_words]


# -----------------------------
# Speech To Text
# -----------------------------
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()

    if not audio_path.endswith(".wav"):
        try:
            sound = AudioSegment.from_file(audio_path)
            new_path = audio_path.rsplit(".", 1)[0] + ".wav"

            sound.export(
                new_path,
                format="wav",
                parameters=["-ac", "1", "-ar", "16000"]
            )

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
    except Exception as e:
        print("Speech Recognition Error:", e)
        return ""


# -----------------------------
# Analyze Text
# -----------------------------
def analyze_text(text, question=None):

    words = text.lower().split()
    total_words = len(words)

    filler_words = ["um", "uh", "like", "you know", "basically"]
    filler_count = sum(text.lower().count(f) for f in filler_words)

    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0:
        sentiment = "Positive 😊"
    elif polarity < 0:
        sentiment = "Negative 😟"
    else:
        sentiment = "Neutral 😐"

    relevance = 100

    if question:
        q_words = extract_keywords(question)

        if len(q_words) > 0:
            matches = sum(1 for word in q_words if word in text.lower())
            relevance = int((matches / len(q_words)) * 100)

    confidence = max(100 - (filler_count * 10), 0)

    if 100 <= total_words <= 160:
        clarity = 100
    else:
        clarity = 70

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

    if total_words < 100:
        feedback.append("Your speaking pace is slow.")
    elif total_words > 170:
        feedback.append("You are speaking too fast.")

    if polarity < 0:
        feedback.append("Try to sound more confident and positive.")

    if not feedback:
        feedback.append("Great answer! Well structured and confident.")

    return {
        "total_words": total_words,
        "filler_count": filler_count,
        "wpm": total_words,
        "sentiment": sentiment,
        "relevance": relevance,
        "confidence": confidence,
        "clarity": clarity,
        "final_score": final_score,
        "level": level,
        "feedback": feedback
    }