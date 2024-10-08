# Dank Discord Bot

## Requirements

- Python 3.12
- ffmpeg

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Create a `.env` file in the project directory with the following content:

```bash
DISCORD_TOKEN=your-discord-token
TEST_CHANNEL=your-test-channel-id
```

Replace `your-discord-token` with your Discord token and `your-test-channel-id` with the ID of the channel you want to test the bot in.

### Run on local machine

```bash
python bot.py
```

### Run on a Docker container

```bash
# build the image
docker build -t dank-bot .

# run the container (pick one)
docker run -d dank-bot # run in background
docker run -it dank-bot # run in foreground
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
