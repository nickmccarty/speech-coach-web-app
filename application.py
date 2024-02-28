from flask import Flask, render_template, request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from openai import OpenAI
import nltk
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

nltk.download('vader_lexicon')

application = Flask(__name__)

api_key = 'sk-...'

def process_audio_file(file_path: str) -> str:
    # api_key = "sk-..."
    client = OpenAI(api_key=api_key)
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
    words_with_timestamps = transcript.words
    transcript_text = ""
    for word_info in words_with_timestamps:
        word = word_info['word']
        start_time = word_info['start']
        end_time = word_info['end']
        transcript_text += f"{word} ({start_time} - {end_time})\n"
    transcript_file_path = file_path.rsplit('.', 1)[0] + "-transcript.txt"
    with open(transcript_file_path, "w") as transcript_file:
        transcript_file.write(transcript_text)
    return transcript_file_path

def process_mp3(file_path: str) -> str:
    # api_key = 'sk-...'
    client = OpenAI(api_key=api_key)  # Initialize OpenAI client properly
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
    return transcript

def count_vocal_fillers(text: str) -> int:
    word_count = len(text.split())
    average_words_per_minute = 150  # Average words per minute for speech
    duration = word_count / average_words_per_minute
    vocal_fillers = re.findall(r'\b(?:uh|um)\b', text, flags=re.IGNORECASE)
    filler_count = len(vocal_fillers)
    fillers_per_minute = filler_count / (duration / 60) if duration > 0 else 0
    return round((fillers_per_minute/100)*5, 1)*2

def generate_summary(text: str, fillers_per_minute: float) -> str:

    # api_key = "sk-..."
    client = OpenAI(api_key=api_key)  # Initialize OpenAI client properly
    # Rubric criteria
    rubric_criteria = {
        "Speech Clarity and Flow": [
            "Ensure that the speech is clear and coherent throughout the presentation.",
            "Avoid excessive use of fillers such as 'um' and 'uh'. Current rate: {:.2f} fillers per minute.".format(fillers_per_minute),
            "Work on improving the flow of speech to maintain listener engagement."
        ],
        "Content Organization": [
            "Organize the content logically with clear transitions between topics.",
            "Ensure that the main ideas are clearly articulated and supported with relevant details.",
            "Consider using visual aids or examples to enhance understanding."
        ],
        "Engagement with Audience": [
            "Engage the audience by using anecdotes, or relatable examples.",
            "Maintain a conversational tone to foster audience connection and participation.",
            "Encourage thought exploration by using hypotheticals or posing rhetorical questions."
        ],
        "Language and Expression": [
            "Use language appropriate for the target audience and context.",
            "Employ varied vocabulary and sentence structures to maintain interest.",
            "Avoid jargon or complex language that may hinder comprehension."
        ]
    }

    rubric_context = "Evaluation Rubric:\n"
    for dimension, criteria in rubric_criteria.items():
        rubric_context += f"{dimension}:\n"
        for criterion in criteria:
            rubric_context += f"- {criterion}\n"
        rubric_context += "\n"

    instructions = "Please summarize the provided text based on the evaluation rubric. The summary should also include any relevant core arguments, conclusions, findings, logical fallacies, etc., and any constructive critique thereof. Please provide the summary and critique output using bullet points, and please be sure to PROVIDE CLEAR EXAMPLES/SUGGESTIONS REGARDING AREAS TO IMPROVE."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text},
                {"role": "system", "content": rubric_context}
            ],
            temperature=0.2,
            n=1,
            max_tokens=4096,
            presence_penalty=0,
            frequency_penalty=0.1,
        )
    except:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text},
                {"role": "system", "content": rubric_context}
            ],
            temperature=0.2,
            n=1,
            max_tokens=4096,
            presence_penalty=0,
            frequency_penalty=0.1,
        )

    return response.choices[0].message.content.strip()

def evaluate_summary(summary: str) -> float:
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(summary)
    return sentiment_scores['compound']

def extract_youtube_video_id(url: str) -> str | None:
    found = re.search(r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})", url)
    if found:
        return found.group(1)
    return None

def get_video_transcript(video_id: str) -> str | None:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        return None
    text = " ".join([line["text"] for line in transcript])
    return text

def summarize_youtube_video(video_url: str) -> tuple[str, float, float]:
    video_id = extract_youtube_video_id(video_url)
    if video_id:
        transcript = get_video_transcript(video_id)
        if transcript:
            fillers_per_minute = count_vocal_fillers(transcript)
            summary = generate_summary(transcript, fillers_per_minute)
            summary_score = round(100 - (1 - evaluate_summary(summary))*350, 1)
            return summary, fillers_per_minute, summary_score
    return "No input provided", 0.0, 0.0

ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for handling file upload
@application.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['media_file']
        if file.filename == '':
            return render_template('upload.html', error='No selected file')
        if file and allowed_file(file.filename):
            file_path = 'timestamped.' + file.filename.rsplit('.', 1)[1].lower()
            file.save(file_path)
            transcript_file_path = process_audio_file(file_path)
            with open(transcript_file_path, "r") as transcript_file:
                transcript_content = transcript_file.read()
            fillers_per_minute = count_vocal_fillers(transcript_content)
            summary = generate_summary(transcript_content, fillers_per_minute)
            summary_score = round(100 - (1 - evaluate_summary(summary))*350, 1)
            return render_template('result.html', summary=summary.replace('\n', '<br>'), fillers_per_minute=fillers_per_minute, summary_score=summary_score)
        else:
            return render_template('upload.html', error='Invalid file type. Please upload one of the supported file formats: ' + ', '.join(ALLOWED_EXTENSIONS))
    return render_template('upload.html')


# Route for handling URL input
@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        summary, fillers_per_minute, summary_score = summarize_youtube_video(video_url)
        return render_template('result.html', summary=summary.replace('\n', '<br>'), fillers_per_minute=fillers_per_minute, summary_score=summary_score)
    return render_template('index.html')

if __name__ == '__main__':
    application.run()