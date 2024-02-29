# Speech Coach Web App

## Description
A Flask app that uses the OpenAI API to generate constructive critiques when a user inputs a YouTube URL or uploads one of the supported file types (`mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, or `webm`). 

| URL Demo | Upload Demo |
|---------|---------|
| ![Video 1](https://github.com/nickmccarty/speech-coach-web-app/blob/main/images/youtube-url-demo.gif) | ![Video 2](https://github.com/nickmccarty/speech-coach-web-app/blob/main/images/upload-demo.gif) |

## Usage

1) Use `pip` or `conda` to install the dependencies in `requirements.txt`.
2) Enter your OpenAI API where indicated in the `application.py` file.
3) Run `python application.py`.

Your browser should automatically open up with the app running (e.g., at `http://127.0.0.1:5000`)

## Time-Stamped Transcript Generation using OpenAI's `Whisper` speech-to-text model

When a file is uploaded, a time-stamped transcript (named `timestamped-transcript.txt` is saved in the app directory (excerpt of generated output shown below): 

```
Hi (0.23999999463558197 - 0.8600000143051147)
everybody (0.8600000143051147 - 1.340000033378601)
Kathy (1.5399999618530273 - 1.6399999856948853)
Armillas (1.6399999856948853 - 1.899999976158142)
here (1.899999976158142 - 2.440000057220459)
So (2.7200000286102295 - 2.9800000190734863)
today (2.9800000190734863 - 3.259999990463257)
I'm (3.259999990463257 - 3.5999999046325684)
going (3.5999999046325684 - 3.6600000858306885)
to (3.6600000858306885 - 4.0)
talk (4.0 - 4.0)
to (4.0 - 4.199999809265137)
you (4.199999809265137 - 4.400000095367432)
about (4.400000095367432 - 4.699999809265137)
effort (4.699999809265137 - 5.239999771118164)
and (5.960000038146973 - 6.340000152587891)
in (6.340000152587891 - 6.739999771118164)
regards (6.739999771118164 - 7.139999866485596)
to (7.139999866485596 - 7.800000190734863)
marketing (7.800000190734863 - 8.220000267028809)
...
```
