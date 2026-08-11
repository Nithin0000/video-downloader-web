import os
from flask import Flask, jsonify, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route('/')
def home():
  return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
  data = request.json
  url = data.get('url')
  format_type = data.get('format', 'video')

  if not url:
    return jsonify({'error': 'URL is required'}), 400

  ydl_opts = {
      'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
      'quiet': True,
      'no_warnings': True,
  }

  if format_type == 'audio':
    ydl_opts.update({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })
  else:
    ydl_opts.update({'format': 'best[ext=mp4]/best'})

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      file_path = ydl.prepare_filename(info)

      if format_type == 'audio':
        file_path = os.path.splitext(file_path)[0] + '.mp3'

      filename = os.path.basename(file_path)

      return jsonify({
          'success': True,
          'filename': filename,
          'download_url': f'/file/{filename}',
      })

  except Exception as e:
    return jsonify({'error': str(e)}), 500


@app.route('/file/<filename>')
def serve_file(filename):
  file_path = os.path.join(DOWNLOAD_DIR, filename)
  return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
  app.run(debug=True, port=5000)