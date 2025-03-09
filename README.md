Sure, here is the updated `README.md` in Markdown with the correct GitHub URL:

---

# Subtitle Translator

## Overview

This project utilizes the Ollama API to translate subtitle fragments from English to Brazilian Portuguese. The tool is useful for anyone who needs to subtitle videos or audio in different languages.

## Requirements

- Python 3.x
- `requests` library (`pip install requests`)
- An Ollama API key (obtain it from the official [Ollama](https://www.ollama.com/) website)

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/astrowar/SubtitleAutoTranslator.git
   ```

2. Navigate to the project directory:
   ```sh
   cd SubtitleAutoTranslator
   ```

3. Install the necessary dependencies:
   ```sh
   pip install requests
   ```

## Configuration

1. Create a `.env` file in the root of the project and add your Ollama API key:
   ```
   OLLAMA_API_KEY=your_api_token
   ```

## Usage

Execute the Python script to translate subtitle fragments:

```sh
python main.py Original.srt Destination.srt phi4
```

### Parameters

- `Original.srt`: Path to the SRT file containing the original subtitles.
- `Destination.srt`: Path where the translated file will be saved.
- `phi4`: Name of the translation model to be used.

### Example

```sh
python main.py subtitles.en.srt subtitles.pt-br.srt phi4
```

The program will read the fragments from the `subtitles.en.srt` file and generate a new file `subtitles.pt-br.srt` with the translated subtitles.

## Contributing

Feel free to contribute to this project! Follow the standard fork, clone, branch, commit, push, and pull request workflow:

1. Fork the repository
2. Clone your fork locally
3. Create a branch (`git checkout -b feature/new-feature`)
4. Make your changes and commit them (`git commit -m "Add new feature"`)
5. Push to the branch (`git push origin feature/new-feature`)
6. Open a pull request

## License

This project is licensed under the [MIT License](LICENSE).

---

 
