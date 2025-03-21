from av import open_input, Container, Stream

container = open_input('rtsp://admin:ng123456@192.168.1.101/stream')
for stream in container.streams:
    if stream.type == 'video':
        video_stream = stream
        break
codec_context = video_stream.codec_context
reader = container.open(video_stream)

while True:
    packet = reader.read_packet()
    frame = av.frame.Frame(codec_context.width, codec_context.height,
                           codec_context pix_fmt)
    reader.decode_video(packet, frame)
    # 处理帧数据c