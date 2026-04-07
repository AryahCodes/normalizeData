# normalizeData

Normalizes videos to 60fps and 720p resolution. Videos below 720p are upscaled, above 720p are downscaled.

To run pipeline.py locally:

One-time setup:
brew install ffmpeg

Create a folder named videos and put your .mp4 files inside it.

Every run:
1. Put your mp4 files in the videos/ folder
2. Run python pipeline.py
3. Collect results from final_videos/

Running on Google Colab (colab_pipeline.ipynb)
1. Go to https://colab.research.google.com
2. Click File → Upload notebook
3. Upload colab_pipeline.ipynb
4. Run cells top to bottom: install ffmpeg, upload pipeline.py, upload videos, run pipeline, download results