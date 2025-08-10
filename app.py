from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active streams and their metadata
active_streams = {}
stream_passwords = {}

@app.route('/')
def index():
    """Main page with options to start streaming or view streams"""
    return render_template('index.html')

@app.route('/stream')
def stream_page():
    """Page for the streamer to start broadcasting"""
    return render_template('stream.html')

@app.route('/view')
def view_page():
    """Page for viewers to watch streams"""
    return render_template('view.html')

@app.route('/test')
def test_page():
    """Page for testing camera compatibility"""
    return render_template('test.html')

@app.route('/api/start_stream', methods=['POST'])
def start_stream():
    """Start a new stream with password protection"""
    data = request.get_json()
    password = data.get('password')
    stream_name = data.get('stream_name', 'Camera Stream')
    
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    # Generate unique stream ID
    stream_id = secrets.token_urlsafe(16)
    
    # Store stream info
    active_streams[stream_id] = {
        'name': stream_name,
        'started_at': datetime.now(),
        'viewers': 0,
        'active': True
    }
    stream_passwords[stream_id] = password
    
    return jsonify({
        'stream_id': stream_id,
        'message': 'Stream started successfully'
    })

@app.route('/api/stop_stream', methods=['POST'])
def stop_stream():
    """Stop an active stream"""
    data = request.get_json()
    stream_id = data.get('stream_id')
    password = data.get('password')
    
    if stream_id not in active_streams:
        return jsonify({'error': 'Stream not found'}), 404
    
    if stream_id not in stream_passwords or stream_passwords[stream_id] != password:
        return jsonify({'error': 'Invalid password'}), 401
    
    # Remove stream
    del active_streams[stream_id]
    del stream_passwords[stream_id]
    
    # Notify all viewers that stream has ended
    socketio.emit('stream_ended', {'stream_id': stream_id}, room=stream_id)
    
    return jsonify({'message': 'Stream stopped successfully'})

@app.route('/api/streams')
def get_streams():
    """Get list of active streams"""
    streams = []
    for stream_id, stream_data in active_streams.items():
        if stream_data['active']:
            streams.append({
                'id': stream_id,
                'name': stream_data['name'],
                'started_at': stream_data['started_at'].isoformat(),
                'viewers': stream_data['viewers']
            })
    return jsonify(streams)

@app.route('/api/join_stream', methods=['POST'])
def join_stream():
    """Join a stream as a viewer"""
    data = request.get_json()
    stream_id = data.get('stream_id')
    
    if stream_id not in active_streams:
        return jsonify({'error': 'Stream not found'}), 404
    
    if not active_streams[stream_id]['active']:
        return jsonify({'error': 'Stream is not active'}), 400
    
    # Increment viewer count
    active_streams[stream_id]['viewers'] += 1
    
    return jsonify({
        'stream_id': stream_id,
        'stream_name': active_streams[stream_id]['name']
    })

# WebSocket events
@socketio.on('join_stream')
def on_join_stream(data):
    """Handle viewer joining a stream"""
    stream_id = data['stream_id']
    join_room(stream_id)
    
    if stream_id in active_streams:
        active_streams[stream_id]['viewers'] += 1
        emit('viewer_joined', {'viewers': active_streams[stream_id]['viewers']}, room=stream_id)

@socketio.on('leave_stream')
def on_leave_stream(data):
    """Handle viewer leaving a stream"""
    stream_id = data['stream_id']
    leave_room(stream_id)
    
    if stream_id in active_streams:
        active_streams[stream_id]['viewers'] = max(0, active_streams[stream_id]['viewers'] - 1)
        emit('viewer_left', {'viewers': active_streams[stream_id]['viewers']}, room=stream_id)

@socketio.on('stream_signal')
def on_stream_signal(data):
    """Handle WebRTC signaling from streamer"""
    stream_id = data['stream_id']
    signal_data = data['signal']
    
    # Broadcast signal to all viewers in the stream room
    emit('stream_signal', signal_data, room=stream_id, include_self=False)

@socketio.on('viewer_signal')
def on_viewer_signal(data):
    """Handle WebRTC signaling from viewer"""
    stream_id = data['stream_id']
    signal_data = data['signal']
    
    # Send signal back to streamer
    emit('viewer_signal', signal_data, room=stream_id, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 