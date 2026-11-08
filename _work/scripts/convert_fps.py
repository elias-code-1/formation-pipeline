import subprocess, sys, shlex, os

def run(cmd):
    subprocess.check_call(cmd, shell=True)

def main():
    if len(sys.argv) != 3:
        print('Usage: python convert_fps.py <input> <output>')
        sys.exit(1)
    inp, out = sys.argv[1], sys.argv[2]
    # Convert to constant 30 fps, keep original resolution, encode H.264 for consistency
    cmd = f"ffmpeg -y -i {shlex.quote(inp)} -filter:v fps=fps=30 -c:v libx264 -crf 20 -preset veryfast {shlex.quote(out)}"
    run(cmd)

if __name__ == '__main__':
    main()
