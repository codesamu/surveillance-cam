# Surveillance Camera Streaming Application

A secure Flask-based web application that allows users to stream their camera feed with password protection and enables others to view the streams in real-time.

## Features

- 🔐 **Password Protection**: Streams require a password to start broadcasting
- 📹 **Real-time Streaming**: WebRTC-based camera streaming for low latency
- 👥 **Multi-viewer Support**: Multiple users can watch the same stream simultaneously
- 📱 **Mobile Responsive**: Works on both desktop and mobile devices
- 🔄 **Live Updates**: Real-time stream status and viewer count updates
- 🎨 **Modern UI**: Beautiful, intuitive interface with smooth animations

## How It Works

1. **Streamer**: User visits `/stream` page, enters a password, and starts broadcasting their camera
2. **Viewers**: Other users visit `/view` page to see available streams and watch them
3. **WebRTC**: Direct peer-to-peer connections for efficient video streaming
4. **Security**: Password protection ensures only authorized users can start streams

## Prerequisites

- Python 3.7 or higher
- Modern web browser with camera access support
- Network access for WebRTC connections

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd surveillance-cam
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

1. **Run the Flask application**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   - Open your browser and go to `http://localhost:5000`
   - The server will be accessible from other devices on your network at `http://<your-ip>:5000`

### Starting a Stream

1. Click **"Start Streaming"** on the main page
2. Enter a **stream name** (optional, defaults to "My Camera Stream")
3. Enter a **password** (required)
4. Click **"Start Streaming"** button
5. Allow camera access when prompted
6. Your stream is now live and others can view it

### Watching Streams

1. Click **"View Streams"** on the main page
2. See all available active streams
3. Click **"Watch Stream"** on any stream you want to view
4. The video will appear and start playing automatically

## API Endpoints

- `GET /` - Main page
- `GET /stream` - Streaming page
- `GET /view` - Viewing page
- `POST /api/start_stream` - Start a new stream
- `POST /api/stop_stream` - Stop an active stream
- `GET /api/streams` - Get list of active streams
- `POST /api/join_stream` - Join a stream as viewer

## WebSocket Events

- `join_stream` - Join a stream room
- `leave_stream` - Leave a stream room
- `stream_signal` - WebRTC signaling from streamer
- `viewer_signal` - WebRTC signaling from viewer
- `stream_ended` - Stream has ended
- `viewer_joined` - New viewer joined
- `viewer_left` - Viewer left

## Security Features

- **Password Protection**: Each stream requires a unique password
- **Stream Isolation**: Streams are isolated in separate rooms
- **Secure WebRTC**: Uses STUN servers for NAT traversal
- **Session Management**: Secure session handling with Flask

## Network Configuration

### For Local Network Access

The application runs on `0.0.0.0:5000` by default, making it accessible from other devices on your local network.

### For Internet Access

To make the application accessible from the internet:

1. **Configure your router** to forward port 5000 to your server
2. **Use a dynamic DNS service** if you don't have a static IP
3. **Consider using HTTPS** for production deployments

## Troubleshooting

### Common Issues

1. **Camera not working**:
   - Ensure you're using HTTPS or localhost
   - Check browser permissions for camera access
   - Try refreshing the page

2. **Stream not connecting**:
   - Check network connectivity
   - Ensure firewall allows port 5000
   - Verify WebRTC is supported in your browser

3. **Performance issues**:
   - Reduce video quality in browser settings
   - Check network bandwidth
   - Close unnecessary browser tabs

### Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Mobile browsers**: Full support

## Development

### Project Structure

```
surveillance-cam/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── index.html     # Main page
│   ├── stream.html    # Streaming page
│   └── view.html      # Viewing page
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding Features

- **Authentication**: Add user accounts and login system
- **Recording**: Implement stream recording functionality
- **Multiple Cameras**: Support for multiple camera streams
- **Chat**: Add real-time chat during streams
- **Notifications**: Push notifications for new streams

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on the repository.