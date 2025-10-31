# app.py
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import os

app = Flask(__name__)

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.json
        video_id = data.get('videoId')
        
        if not video_id:
            return jsonify({'error': 'videoId is required'}), 400
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text
        full_transcript = ' '.join([item['text'] for item in transcript_list])
        
        return jsonify({
            'transcript': full_transcript,
            'language': 'en',
            'videoId': video_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)