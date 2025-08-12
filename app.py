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

# In-memory signaling/session maps
# stream_sessions: { stream_id: { 'streamer_sid': str | None, 'viewers': { viewer_id: sid } } }
stream_sessions = {}
# Reverse lookup to clean up on disconnect: { sid: { 'stream_id': str, 'viewer_id': str } }
viewer_sid_to_info = {}

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

    # Initialize signaling session map for this stream
    stream_sessions[stream_id] = { 'streamer_sid': None, 'viewers': {} }
    
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
    # Cleanup sessions
    try:
        for viewer_id, sid in (stream_sessions.get(stream_id, {}).get('viewers', {}).items()):
            socketio.server.leave_room(sid, stream_id)
    except Exception:
        pass
    stream_sessions.pop(stream_id, None)
    
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

@app.route('/api/authorize_view', methods=['POST'])
def authorize_view():
    """Authorize a viewer to join a stream using the stream password."""
    data = request.get_json()
    stream_id = data.get('stream_id')
    password = data.get('password')

    if stream_id not in active_streams:
        return jsonify({'error': 'Stream not found'}), 404

    if stream_passwords.get(stream_id) != password:
        return jsonify({'error': 'Invalid password'}), 401

    return jsonify({ 'authorized': True })

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

@socketio.on('register_streamer')
def on_register_streamer(data):
    stream_id = data['stream_id']
    join_room(stream_id)
    if stream_id in stream_sessions:
        stream_sessions[stream_id]['streamer_sid'] = request.sid

@socketio.on('register_viewer')
def on_register_viewer(data):
    stream_id = data['stream_id']
    viewer_id = data['viewer_id']
    join_room(stream_id)
    if stream_id in stream_sessions:
        stream_sessions[stream_id]['viewers'][viewer_id] = request.sid
        if stream_id in active_streams:
            active_streams[stream_id]['viewers'] += 1
        # Inform streamer a viewer joined
        emit('viewer_joined', {
            'viewerId': viewer_id,
            'viewers': active_streams[stream_id]['viewers'] if stream_id in active_streams else 0
        }, room=stream_id)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    # Could implement cleanup by tracking reverse mapping
    # Skipping detailed cleanup for brevity

@socketio.on('stream_signal')
def on_stream_signal_routed(data):
    """Streamer sends offers/ICE to a specific viewer."""
    stream_id = data['stream_id']
    signal_data = data['signal']
    viewer_id = signal_data.get('viewerId')
    # Route only to that viewer if known, else broadcast to room
    target_sid = stream_sessions.get(stream_id, {}).get('viewers', {}).get(viewer_id)
    if target_sid:
        emit('stream_signal', signal_data, to=target_sid)
    else:
        emit('stream_signal', signal_data, room=stream_id, include_self=False)

@socketio.on('viewer_signal')
def on_viewer_signal_routed(data):
    """Viewer sends answer/ICE back to streamer."""
    stream_id = data['stream_id']
    signal_data = data['signal']
    streamer_sid = stream_sessions.get(stream_id, {}).get('streamer_sid')
    if streamer_sid:
        emit('viewer_signal', signal_data, to=streamer_sid)
    else:
        emit('viewer_signal', signal_data, room=stream_id, include_self=False)

if __name__ == '__main__':
    # Prefer eventlet if available for better websockets
    try:
        import eventlet
        import eventlet.wsgi  # noqa: F401
        async_mode = 'eventlet'
    except Exception:
        async_mode = 'threading'
    socketio.run(app, host='0.0.0.0', port=5002, debug=True) 