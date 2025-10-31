# app.py
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'running',
        'message': 'YouTube Transcript API Service',
        'endpoints': {
            'POST /api/transcript': 'Get transcript for a video'
        }
    })

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.json
        video_id = data.get('videoId')
        url = data.get('url', '')
        
        # Extract video ID from URL if not provided directly
        if not video_id and url:
            import re
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
                r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
                r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
        
        if not video_id:
            return jsonify({'error': 'videoId or valid YouTube URL is required'}), 400
        
        # Get transcript using the correct method
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text segments
        full_transcript = ' '.join([item['text'] for item in transcript_list])
        
        # Get available languages
        transcript_info = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [t.language_code for t in transcript_info]
        
        return jsonify({
            'success': True,
            'transcript': full_transcript,
            'language': 'en',
            'videoId': video_id,
            'availableLanguages': available_languages,
            'segmentCount': len(transcript_list)
        })
    
    except TranscriptsDisabled:
        return jsonify({
            'success': False,
            'error': 'Transcripts are disabled for this video',
            'videoId': video_id
        }), 404
    
    except NoTranscriptFound:
        return jsonify({
            'success': False,
            'error': 'No transcript found for this video',
            'videoId': video_id
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)